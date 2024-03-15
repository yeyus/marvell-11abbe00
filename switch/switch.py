import requests
from switch.endpoints import StatusCode, get_login_endpoint, get_wcd_endpoint
from switch.builder import DeviceConfiguration, ServiceFactory, Version, Entry, Value
import xml.etree.ElementTree as ET


def handle_response_code(request):
    xmltree = ET.fromstring(request.text)
    print(ET.dump(xmltree))
    statusCode = next(xmltree.iter("statusCode"), None)
    statusString = next(xmltree.iter("statusString"), None)
    if statusCode is not None and statusCode.text != StatusCode.OK.value:
        raise Exception(f"error response: {statusString.text}")

    return True

def is_authenticated(cls):
    def wrapper():


class SwitchConfigurationManager:
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

        xml = ET.dump(payload)
        r = requests.post(get_wcd_endpoint(self.host, []), data=xml, verify=False)

        if not handle_response_code(r):
            raise Exception("error while setting idle timeout")
