from datetime import datetime
import urllib3
import requests

from switch.endpoints import (
    StatusCode,
    get_http_download_endpoint,
    get_login_endpoint,
    get_wcd_endpoint,
    get_wcd_raw_endpoint,
)
from switch.builder import (
    CurrentLocalTime,
    DeviceConfiguration,
    ServiceFactory,
    Version,
    Entry,
    Value,
)
import xml.etree.ElementTree as ET

urllib3.disable_warnings()
urllib3.util.url._QUERY_CHARS.add("{")
urllib3.util.url._QUERY_CHARS.add("}")


def handle_response_code(request):
    xmltree = ET.fromstring(request.text)
    statusCode = next(xmltree.iter("statusCode"), None)
    statusString = next(xmltree.iter("statusString"), None)
    if statusCode is not None and statusCode.text != StatusCode.OK.value:
        raise Exception(f"error response: {statusString.text}")

    return True


class SwitchConfigurationManager:
    def is_authenticated(func):
        def inner(*args, **kwargs):
            if args[0].token is None:
                raise Exception("Method should be called in an authenticated context")
            func(*args, **kwargs)

        return inner

    def __init__(self, host):
        self.host = host
        self.token = None

    def login(self, user="cisco", password="cisco"):
        r = requests.get(
            get_login_endpoint(self.host, user=user, password=password), verify=False
        )
        if r.status_code != 200:
            raise Exception("Invalid HTTP status code")

        if not handle_response_code(r):
            raise Exception("error while login")

        sessionid = r.headers.get("sessionID")
        if not sessionid:
            raise Exception("Error while login: sessionID not found")

        self.token = r.headers["sessionID"]
        return self.token

    @is_authenticated
    def set_max_idle_timeout(self, timeout=0):
        payload = (
            DeviceConfiguration()
            .append(Version("1.0"))
            .append(
                ServiceFactory(serviceName="EWSServiceTable", action="set").append(
                    Entry().append(Value(key="maxIdleTimeout", value=str(timeout)))
                )
            )
        ).build()

        xml = ET.tostring(payload, encoding="utf8")
        r = requests.post(
            get_wcd_endpoint(self.host, []),
            data=xml,
            verify=False,
            headers={"sessionID": self.token},
        )

        if not handle_response_code(r):
            raise Exception("error while setting idle timeout")

    @is_authenticated
    def set_time(self, date=datetime.today()):
        payload = (
            DeviceConfiguration().append(
                ServiceFactory(serviceName="TimeSetting", action="set")
                .append(Value(key="setTimeMode", value=str(1)))
                .append(
                    CurrentLocalTime()
                    .append(Value(key="year", value=str(date.year)))
                    .append(Value(key="month", value=str(date.month)))
                    .append(Value(key="day", value=str(date.day)))
                    .append(Value(key="hour", value=str(date.hour)))
                    .append(Value(key="minute", value=str(date.minute)))
                    .append(Value(key="second", value=str(date.second)))
                )
            )
        ).build()

        xml = ET.tostring(payload, encoding="utf8")
        r = requests.post(
            get_wcd_endpoint(self.host, []),
            data=xml,
            verify=False,
            headers={"sessionID": self.token},
        )

        if not handle_response_code(r):
            raise Exception("error while setting time")

    @is_authenticated
    def get_time(self):
        endpoint = get_wcd_endpoint(self.host, ["TimeSetting"])
        http = urllib3.PoolManager(cert_reqs="CERT_NONE")
        r = http.request(
            "GET",
            endpoint,
            headers={"sessionID": self.token},
        )

        print(f"Response: {r.data}")

    @is_authenticated
    def download_config(self):
        endpoint = get_http_download_endpoint(self.host)
        http = urllib3.PoolManager(cert_reqs="CERT_NONE")
        r = http.request(
            "GET",
            endpoint,
            headers={"sessionID": self.token},
        )

        print(f"Response: {r.data}")
