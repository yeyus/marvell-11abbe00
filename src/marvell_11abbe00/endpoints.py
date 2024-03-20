from enum import Enum

from urllib.parse import urlencode


def get_host(host):
    return f"https://{host}/"


def get_login_endpoint(host, user, password):
    return f"{get_host(host)}System.xml?action=login&user={user}&password={password}"


def get_logout_endpoint(host):
    return f"{get_host(host)}System.xml?action=logout"


def get_keep_alive_endpoint(host):
    return f"{get_host(host)}device/authenticate_user.xml"


def get_wcd_endpoint(host, queries=[]):
    queryString = "".join(["{" + query + "}" for query in queries])
    return f"{get_host(host)}wcd?{queryString}"


def get_wcd_raw_endpoint(host):
    return f"{get_host(host)}wcd?"


def get_system_action_endpoint(host, action):
    return f"{get_host(host)}System.xml?action={action}"


def get_section_query(section, query):
    querystring = urlencode(query)
    return f"{section}&{querystring}"


class SystemActions(Enum):
    DOWNLOAD_CONFIGURATION_FILE = "downloadConfigurationFile"
    UPLOAD_CONFIGURATION_FILE = "uploadConfigurationFile"
    UPDATE_FIRMWARE = "updateFirmaware"
    LOAD_FIRMWARE = "loadFirmware"


class Sections(Enum):
    EWS_SERVICE_TABLE = "EWSServiceTable"
    TIME_SETTING = "TimeSetting"
    FULL_INTERFACE_LIST = "FullInterfaceList"
    VLAN_LIST = "VLANList"
    VLAN_INTERFACE_IS_LIST = "VLANInterfaceISList"
    LLDP_INTERFACE_LIST = "LLDPInterfaceList"
    CDP_INTERFACE_LIST = "CDPInterfaceList"
    LAN1_MODULE_INTERFACE_TABLE = "LAN1ModuleInterfaceTable"
    LAN1_INP_COS_MAPPING_INTERFACE_TABLE = "LAN1InpCoSMappingInterfaceTable"
    LAN1_OUT_QUEUE_MAPPING_INTERFACE_TABLE = "LAN1OutQueueMappingInterfaceTable"
    LAN1_x86_PFC_TABLE = "LAN1x86PfcTable"
    POE_PSE_INTERFACE_LIST = "PoEPSEInterfaceList"
    STP = "STP"
    SPANNING_TREE_GLOBAL_PARAM = "SpanningTreeGlobalParam"
    INTERFACE_SECURITY_TABLE = "InterfaceSecurityTable"
    FORWARDING_GLOBAL_SETTING = "ForwardingGlobalSetting"
    STANDARD_8021X_INTERFACE_LIST = "Standard_802_1xInterfaceList"
    STANDARD_8023_LIST = "Standard802_3List"


class SwitchPortModeAdmin(Enum):
    GENERAL = "10"
    ACCESS = "11"
    TRUNK = "12"
    PRIVATE_VLAN_PROMISCUOUS = "13"
    PRIVATE_VLAN_HOST = "14"
    CUSTOMER = "15"


class LLDPInterfaceListPortState(Enum):
    TX_ONLY = "1"
    RX_ONLY = "2"
    TX_AND_RX = "3"
    DISABLED = "4"


class POEPSEInterfaceAdminEnable(Enum):
    """
    @param adminEnable
    True (1)- Turns on the device discovery protocol and applies power to the device (auto).
    False(2)- Turns off the device discovery protocol and stops supplying power to the device (never).
    CLI: power inline {auto | never}
    """

    ENABLED = "1"
    DISABLED = "2"


class STPOperationMode(Enum):
    STP_COMPATIBLE = "0"
    RSTP = "2"
    MSTP = "3"


class LockInterfaceAdminEnabled(Enum):
    """
    This variable indicates whether this interface should operate in locked or unlocked mode.
    In unlocked mode the device learns all MAC addresses from this port and forwards all frames arrived at this port.
    In locked mode no new MAC addresses are learned and only frames with known source MAC addresses are forwarded.
    locked(1) (disabled) unlocked(2) (enabled)
    """

    LOCKED = "1"
    UNLOCKED = "2"


class LearningMode(Enum):
    """
    This variable indicates what is the learning limitation on the locked interface.
    Possible values:
      disabled(1) (locked) - learning is stopped. The dynamic addresses associated with the port are
                             not aged out or relearned on other port as long as the port is locked.
      dynamic(2) (max-addresses) - dynamic addresses can be learned up to the maximum dynamic addresses allowed
                             on the port. Relearning and aging of the dynamic addresses are enabled.
                             The learned addresses aren't kept after reset.
      secure-permanent(3) - secure addresses can be learned up to the maximum addresses allowed on the port.
                            Relearning and aging of addresses are disabled. The learned addresses are kept after reset.
      secure-delete-on-reset(4) - secure addresses can be learned up to the maximum addresses allowed on the port.
                            Relearning and aging of addresses are disabled. The learned addresses are not kept after
                            reset.
    """

    DISABLED = "1"
    DYNAMIC = "2"
    SECURE_PERMANENT = "3"
    SECURE_DELETE_ON_RESET = "4"


class MACAuthenticationMethod(Enum):
    """
    CLI commands (ethernet ports): dot1x mac-authentication {mac-only | mac-and-802.1x} no dot1x mac-authentication
    CLI commands (ethernet ports): dot1x authentication no dot1x authentication
    CLI commands (ethernet ports): dot1x authentication {dot1x | mac | web} no dot1x authentication
    """

    EAPOL_ONLY = "1"
    MAC_AND_EAPOL = "2"
    MAC_ONLY = "3"
    WEB_ONLY = "4"
    WEB_AND_EAPOL = "5"
    WEB_AND_MAC = "6"
    WEB_AND_MAC_AND_EAPOL = "7"


class PowerPriority(Enum):
    """
    This object controls the priority of the port from the point of view of a power management algorithm.
    The priority that is set by this variable could be used by a control mechanism that prevents over current situations
    by disconnecting first ports with lower power priority. Ports that connect devices critical to the
    operation of the network - like the E911 telephones ports - should be set to higher priority.
    CLI: power inline priority
    """

    CRITICAL = "1"
    HIGH = "2"
    LOW = "3"


class HostMode(Enum):
    """
    This variable indicates the 802.1X host mode of a port. Relevant when the port's 802.1X control is auto.
    In addtion multiple-auth was added.
    CLI commands (ethernet ports): dot1x multiple-hosts [authentication] no dot1x multiple-hosts
    """

    SINGLE = "1"
    MULTIPLE = "2"
    MULTIPLE_AUTH = "3"


class AdminPortControlType(Enum):
    """
    Change the min & max values and add defaults value enum1=1,forceUnauthorized enum2=2,auto enum3=3,forceAuthorized
    """

    FORCE_UNAUTHORIZED = "1"
    AUTO = "2"
    FORCE_AUTHORIZED = "3"


class ActionOnViolationType(Enum):
    """
    This variable indicates which action this interface should be taken in locked mode and
    therefore relevant only in locked mode.
    Possible actions:
        discard(1) - every packet is dropped.
        forwardNormal(2) - every packet is forwarded according to the DST address.
        discardDisable(3) - drops the first packet and suspends the port.
    ** Default value is product specific.
    """

    DISCARD = "1"
    FORWARD_NORMAL = "2"
    DISCARD_DISABLED = "3"
