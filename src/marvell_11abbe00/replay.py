import json
import logging
import argparse
from urllib.parse import urlparse
import requests
import urllib3
import xml.etree.ElementTree as ET

from haralyzer import HarPage
from haralyzer.http import Request

from marvell_11abbe00.response import StatusCode, WCDResponse
from marvell_11abbe00.switch import SwitchConfigurationManager

logging.basicConfig(encoding="utf-8", level=logging.INFO)
logger = logging.getLogger(__name__)

urllib3.disable_warnings()
urllib3.util.url._QUERY_CHARS.add("{")
urllib3.util.url._QUERY_CHARS.add("}")


def request_process_filter(request: "Request") -> bool:
    # we will do our own login
    if "System.xml?action=login" in request.url:
        return False

    # do not send password overwrite requests
    if "wcd" in request.url and "AdminUserEntry" in request.text:
        return False

    # we will also set our own time
    if "wcd" in request.url and 'TimeSetting action="set"' in request.text:
        return False

    return True


def request_replace_headers(request: "Request", sessionId: str) -> dict[str, str]:
    headers = {}
    for header in request.headers:
        key = header["name"]
        value = header["value"]
        if key.lower() == "sessionid":
            headers[key] = sessionId
        else:
            headers[key] = value

    return headers


def request_process(request: "Request", host, sessionId) -> WCDResponse:
    originalUrl = urlparse(request.url)
    replacedUrl = originalUrl._replace(netloc=host)
    response = requests.request(
        method=request.method,
        url=replacedUrl.geturl(),
        data=request.text,
        headers=request_replace_headers(request, sessionId),
        verify=False,
    )

    return response


def main():
    parser = argparse.ArgumentParser(description="Replay a HAR file to the switch")
    parser.add_argument(
        "--host",
        required=True,
        dest="host",
        type=str,
        help="host switch api",
    )
    parser.add_argument(
        "--har",
        required=True,
        dest="harFile",
        type=str,
        help="path to the HAR file to replay",
    )
    parser.add_argument(
        "--username",
        required=False,
        default="cisco",
        dest="username",
        type=str,
        help="switch api username",
    )
    parser.add_argument(
        "--password",
        required=False,
        default="cisco",
        dest="password",
        type=str,
        help="switch api password",
    )

    args = parser.parse_args()

    with open(args.harFile, "r") as f:
        har_page = HarPage("unknown", har_data=json.loads(f.read()))

    switch = SwitchConfigurationManager(args.host)
    sessionId = switch.login(args.username, args.password)
    switch.set_time()

    logger.info(f"loaded {args.harFile} with {len(har_page.entries)} entries")

    for index, entry in enumerate(har_page.entries):
        req = entry.request
        logger.info(f"[{index} / {len(har_page.entries)}] processing entry - {req.url}")

        if not request_process_filter(req):
            logger.info(
                f"[{index} / {len(har_page.entries)}] url did not pass url filter skip"
            )
            continue

        while True:
            response = request_process(req, args.host, sessionId)

            if "/device/authenticate_user.xml" in req.url:
                logger.info(f"[{index} / {len(har_page.entries)}] session keep alive")
                break

            xmlResponse = ET.fromstring(response.text)
            wcdResponse = WCDResponse.from_xml_response(xmlResponse)
            actionStatus = wcdResponse.actionStatus

            if actionStatus is not None:
                if actionStatus.statusCode == StatusCode.AUTHENTICATION_ERROR:
                    logger.warning("token expired. login again.")
                    sessionId = switch.login(args.username, args.password)
                    continue
                elif actionStatus.statusCode == StatusCode.PAYLOAD_ERROR:
                    logger.error("payload error.")
                    ET.dump(response.text)
                    break
                logger.info(
                    f"[{index} / {len(har_page.entries)}] result - {str(actionStatus)}"
                )
                break
            else:
                logger.info("Unknown response format!")
                break


if __name__ == "__main__":
    main()
