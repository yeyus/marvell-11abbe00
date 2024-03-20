from datetime import datetime
import urllib3
import requests
import logging

from marvell_11abbe00.endpoints import (
    Sections,
    SystemActions,
    get_login_endpoint,
    get_section_query,
    get_system_action_endpoint,
    get_wcd_endpoint,
)
from marvell_11abbe00.builder import (
    VLAN,
    BridgeSetting,
    CurrentLocalTime,
    DeviceConfiguration,
    GlobalSetting,
    InterfaceEntry,
    ServiceFactory,
    Version,
    Entry,
    Value,
)
import xml.etree.ElementTree as ET

from marvell_11abbe00.response import ActionStatus, StatusCode

logger = logging.getLogger(__name__)

urllib3.disable_warnings()
urllib3.util.url._QUERY_CHARS.add("{")
urllib3.util.url._QUERY_CHARS.add("}")


def handle_response_code(request):
    xmltree = ET.fromstring(request.text)
    actionStatus = ActionStatus.from_xml_response(xmltree)
    if actionStatus.statusCode is not None and actionStatus.statusCode != StatusCode.OK:
        raise Exception(f"error response: {actionStatus.statusString}")

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
                ServiceFactory(
                    serviceName=Sections.EWS_SERVICE_TABLE.value, action="set"
                ).append(
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
                ServiceFactory(serviceName=Sections.TIME_SETTING.value, action="set")
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
    def set_vlan_id(self, vlanid):
        payload = (
            DeviceConfiguration()
            .append(Version("1.0"))
            .append(
                ServiceFactory(
                    serviceName=Sections.VLAN_LIST.value, action="set"
                ).append(VLAN().append(Value(key="VLANID", value=str(vlanid))))
            )
        ).build()

        xml = ET.tostring(payload, encoding="utf8")
        r = requests.post(
            get_wcd_endpoint(self.host, [Sections.VLAN_LIST.value]),
            data=xml,
            verify=False,
            headers={"sessionID": self.token},
        )

        if not handle_response_code(r):
            raise Exception("error while setting vlan id")

    @is_authenticated
    def set_section_settings(self, *, section, settings=None):
        entries = Entry()
        for entry in settings or []:
            for key, value in entry.items():
                entries = entries.append(Value(key=key, value=str(value)))

        payload = (
            DeviceConfiguration()
            .append(Version("1.0"))
            .append(ServiceFactory(serviceName=section, action="set").append(entries))
        ).build()

        xml = ET.tostring(payload, encoding="utf8")
        url = get_wcd_endpoint(
            self.host,
            [section],
        )

        logger.debug(f"url: {url}")
        logger.debug(f"payload: {ET.tostring(payload)}")

        r = requests.post(
            url,
            data=xml,
            verify=False,
            headers={"sessionID": self.token},
        )

        logger.debug(f"response: {ET.tostring(ET.fromstring(r.text))}")

        if not handle_response_code(r):
            raise Exception(f"error while setting interface {section} settings")

    @is_authenticated
    def set_interface_section_settings(self, *, section, interfaceName, settings=None):
        Container = (
            InterfaceEntry
            if section == Sections.LLDP_INTERFACE_LIST.value
            or section == Sections.STANDARD_8021X_INTERFACE_LIST.value
            else Entry
        )
        entries = Container().append(Value(key="interfaceName", value=interfaceName))
        for entry in settings or []:
            for key, value in entry.items():
                entries = entries.append(Value(key=key, value=str(value)))

        payload = (
            DeviceConfiguration()
            .append(Version("1.0"))
            .append(ServiceFactory(serviceName=section, action="set").append(entries))
        ).build()

        xml = ET.tostring(payload, encoding="utf8")
        url = get_wcd_endpoint(
            self.host,
            [
                get_section_query(
                    section,
                    {"interfaceName": interfaceName},
                )
            ],
        )

        logger.debug(f"url: {url}")
        logger.debug(f"payload: {ET.tostring(payload)}")

        r = requests.post(
            url,
            data=xml,
            verify=False,
            headers={"sessionID": self.token},
        )

        logger.debug(f"response: {ET.tostring(ET.fromstring(r.text))}")

        if not handle_response_code(r):
            raise Exception(f"error while setting interface {section} settings")

    @is_authenticated
    def set_interface_vlan_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.VLAN_INTERFACE_IS_LIST.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_interface_lldp_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.LLDP_INTERFACE_LIST.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_interface_cdp_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.CDP_INTERFACE_LIST.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_lan1_interface_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.LAN1_MODULE_INTERFACE_TABLE.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_poe_pse_interface_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.POE_PSE_INTERFACE_LIST.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_stp_settings(
        self,
        *,
        bpduHandlingMode,
        forwardDelay,
        helloTime,
        maxAge,
        pathCostDefaultValueType,
        bridgePriority,
    ):
        payload = (
            DeviceConfiguration()
            .append(Version("1.0"))
            .append(
                ServiceFactory(serviceName=Sections.STP.value, action="set").append(
                    GlobalSetting()
                    .append(
                        Value(key="BPDUHandlingMode", value=bpduHandlingMode).append(
                            Value(
                                key="pathCostDefaultValueType",
                                value=pathCostDefaultValueType,
                            )
                        )
                    )
                    .append(
                        BridgeSetting()
                        .append(Value(key="forwardDelay", value=forwardDelay))
                        .append(Value(key="helloTime", value=helloTime))
                        .append(Value(key="maxAge", value=maxAge))
                        .append(Value(key="bridgePriority", value=bridgePriority))
                    )
                )
            )
        ).build()

        xml = ET.tostring(payload, encoding="utf8")
        r = requests.post(
            get_wcd_endpoint(self.host, [Sections.STP.value]),
            data=xml,
            verify=False,
            headers={"sessionID": self.token},
        )

        if not handle_response_code(r):
            raise Exception("error while setting stp settings")

    @is_authenticated
    def set_stp_global_settings(self, *, settings):
        return self.set_section_settings(
            section=Sections.SPANNING_TREE_GLOBAL_PARAM.value, settings=settings
        )

    @is_authenticated
    def set_security_interface_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.INTERFACE_SECURITY_TABLE.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_forwarding_global_settings(self, *, settings):
        return self.set_section_settings(
            section=Sections.FORWARDING_GLOBAL_SETTING.value, settings=settings
        )

    @is_authenticated
    def set_interface_8021x_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.STANDARD_8021X_INTERFACE_LIST.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def set_interface_8023_settings(self, *, interfaceName, settings):
        return self.set_interface_section_settings(
            section=Sections.STANDARD_8023_LIST.value,
            interfaceName=interfaceName,
            settings=settings,
        )

    @is_authenticated
    def get_sections_xml(self, sections=[]):
        endpoint = get_wcd_endpoint(self.host, sections)
        http = urllib3.PoolManager(cert_reqs="CERT_NONE")
        r = http.request(
            "GET",
            endpoint,
            headers={"sessionID": self.token},
        )

        xmltree = ET.fromstring(r.data)
        ET.indent(xmltree, space="\t", level=0)
        ET.dump(xmltree)
        # print(ET.tostring(xmltree, encoding="utf8"))

    @is_authenticated
    def download_config(self):
        """
        It won't certainly work as the config that the ENCS5400 will pull doesn't seem to match the current state
        """
        endpoint = get_system_action_endpoint(
            self.host, SystemActions.DOWNLOAD_CONFIGURATION_FILE.value
        )
        r = requests.get(endpoint, verify=False, headers={"sessionID": self.token})

        print(f"Response: {r.text}")
