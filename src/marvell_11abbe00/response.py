from enum import Enum
from typing import Optional
import xml.etree.ElementTree as ET


class StatusCode(Enum):
    NOT_FOUND = "-1"
    OK = "0"
    PAYLOAD_ERROR = "3"
    AUTHENTICATION_ERROR = "4"


def get_node_text(xmlnode: ET.Element, tag: str, default=None) -> Optional[str]:
    node = next(xmlnode.iter(tag), None)
    return node.text if node is not None else default


class ActionStatus:
    def __init__(
        self,
        version,
        requestURL,
        statusCode: StatusCode,
        deviceStatusCode,
        statusString,
    ):
        self.version = version
        self.requestURL = requestURL
        self.statusCode = statusCode
        self.deviceStatusCode = deviceStatusCode
        self.statusString = statusString

    def __str__(self):
        return (
            f"<ActionStatus/{self.version} requestURL={self.requestURL} "
            f"statusCode={self.statusCode} statusString={self.statusString}>"
        )

    @classmethod
    def from_xml_response(cls, xmltree: ET.Element) -> "ActionStatus":
        actionStatus = next(xmltree.iter("ActionStatus"), None)

        if not actionStatus:
            raise ValueError("Can't find <ActionStatus> root")

        version = get_node_text(actionStatus, "version")
        requestURL = get_node_text(actionStatus, "requestURL")
        statusCode = get_node_text(actionStatus, "statusCode")
        deviceStatusCode = get_node_text(actionStatus, "deviceStatusCode")
        statusString = get_node_text(actionStatus, "statusString")

        return cls(
            version=version,
            requestURL=requestURL,
            statusCode=StatusCode(statusCode) if statusCode is not None else None,
            deviceStatusCode=deviceStatusCode,
            statusString=statusString,
        )


class WCDResponse:
    def __init__(self, actionStatus, deviceConfiguration):
        self.actionStatus = actionStatus
        self.deviceConfiguration = deviceConfiguration

    @classmethod
    def from_xml_response(cls, xmltree: ET.Element) -> "WCDResponse":
        actionStatus = ActionStatus.from_xml_response(xmltree)
        deviceConfiguration = next(xmltree.iter("DeviceConfiguration"), None)

        return cls(actionStatus=actionStatus, deviceConfiguration=deviceConfiguration)
