import logging
from marvell_11abbe00.endpoints import (
    ActionOnViolationType,
    AdminPortControlType,
    HostMode,
    LLDPInterfaceListPortState,
    LearningMode,
    LockInterfaceAdminEnabled,
    MACAuthenticationMethod,
    POEPSEInterfaceAdminEnable,
    PowerPriority,
    STPOperationMode,
    Sections,
    SwitchPortModeAdmin,
    get_section_query,
)
from marvell_11abbe00.switch import SwitchConfigurationManager

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

DEFAULT_HOST = "169.254.1.0"
FORWARDED_HOST = "127.0.0.1:2363"

if __name__ == "__main__":
    switch = SwitchConfigurationManager(FORWARDED_HOST)
    sessionid = switch.login("cisco", "cisco")
    print(f"Your sessionID is {sessionid}")

    # dump the config
    switch.get_sections_xml(
        [
            Sections.EWS_SERVICE_TABLE.value,
            Sections.VLAN_INTERFACE_IS_LIST.value,
            get_section_query(
                Sections.LLDP_INTERFACE_LIST.value, {"interfaceName": "te1"}
            ),
            Sections.CDP_INTERFACE_LIST.value,
            Sections.LAN1_MODULE_INTERFACE_TABLE.value,
            Sections.LAN1_INP_COS_MAPPING_INTERFACE_TABLE.value,
            Sections.LAN1_OUT_QUEUE_MAPPING_INTERFACE_TABLE.value,
            Sections.LAN1_x86_PFC_TABLE.value,
            Sections.STP.value,
            Sections.SPANNING_TREE_GLOBAL_PARAM.value,
        ]
    )

    # infinite login timeout
    switch.set_max_idle_timeout(0)
    switch.set_time()
    switch.set_vlan_id(2350)
    switch.set_vlan_id(2351)
    switch.set_vlan_id(2352)
    switch.set_vlan_id(2353)
    switch.set_vlan_id(2363)

    # setup te1 and te3
    for interface in ["te1", "te3"]:
        switch.set_interface_vlan_settings(
            interfaceName=interface,
            settings=[
                {"switchportModeAdmin": SwitchPortModeAdmin.GENERAL.value},
                {"generalPVID": 2351},
                {
                    (
                        "generalTaggedVLANs"
                        if interface == "te1"
                        else "generalUntaggedVLANs"
                    ): "2350-2351"
                },
            ],
        )
        switch.set_interface_vlan_settings(
            interfaceName=interface,
            settings=[
                {"generalTaggedVLANs": 2351},
            ],
        )
        switch.set_interface_lldp_settings(
            interfaceName=interface,
            settings=[{"portState": LLDPInterfaceListPortState.DISABLED.value}],
        )
        switch.set_interface_cdp_settings(
            interfaceName=interface, settings=[{"enbl": 2}]
        )

    # setup te2
    switch.set_interface_vlan_settings(
        interfaceName="te2",
        settings=[
            {"switchportModeAdmin": SwitchPortModeAdmin.TRUNK.value},
            {"trunkMemberVLANs": "2-2349,2363,2450-4093"},
        ],
    )

    # setup te4
    switch.set_interface_vlan_settings(
        interfaceName="te4",
        settings=[
            {"switchportModeAdmin": SwitchPortModeAdmin.GENERAL.value},
            {"generalPVID": 4095},
            {"generalUntaggedVLANs": 2350},
        ],
    )
    switch.set_interface_lldp_settings(
        interfaceName="te4",
        settings=[{"portState": LLDPInterfaceListPortState.DISABLED.value}],
    )
    switch.set_interface_cdp_settings(interfaceName="te4", settings=[{"enbl": 2}])

    # Error with General error
    # setup te3 lan1
    # switch.set_lan1_interface_settings(
    #     interfaceName="te3",
    #     settings=[
    #         {
    #             "CPTrafficEnable": "1",
    #             "MulticastAllowedVLAN": "2",
    #             "ingressGroupID": "1",
    #             "egressGroupList": "7,8",
    #         }
    #     ],
    # )
    switch.set_interface_section_settings(
        section=Sections.LAN1_INP_COS_MAPPING_INTERFACE_TABLE.value,
        interfaceName="te3",
        settings=[{"profileIndex": 1}],
    )

    # Error with General error
    # setup te4 lan1
    # switch.set_lan1_interface_settings(
    #     interfaceName="te4",
    #     settings=[
    #         {
    #             "CPTrafficEnable": "2",
    #             "MulticastAllowedVLAN": "3",
    #             "ingressGroupID": "1",
    #             "egressGroupList": "8",
    #         }
    #     ],
    # )
    switch.set_interface_section_settings(
        section=Sections.LAN1_INP_COS_MAPPING_INTERFACE_TABLE.value,
        interfaceName="te4",
        settings=[{"profileIndex": 1}],
    )

    switch.set_interface_section_settings(
        section=Sections.LAN1_INP_COS_MAPPING_INTERFACE_TABLE.value,
        interfaceName="te1",
        settings=[{"profileIndex": 1}],
    )
    switch.set_interface_section_settings(
        section=Sections.LAN1_INP_COS_MAPPING_INTERFACE_TABLE.value,
        interfaceName="te3",
        settings=[{"profileIndex": 2}],
    )

    # With Wrong value
    # for priority in [0, 1, 2]:
    #     switch.set_section_settings(
    #         section=Sections.LAN1_x86_PFC_TABLE.value,
    #         settings=[
    #             {
    #                 "priority": str(priority),
    #                 "isLossy": "2",
    #                 "xOffThreshold": "167",
    #                 "xOnThreshold": "156",
    #             }
    #         ],
    #     )

    for ports in ["gi0", "gi1", "gi2", "gi3", "gi4", "gi5", "gi6", "gi7"]:
        switch.set_poe_pse_interface_settings(
            interfaceName=ports,
            settings=[
                {
                    "adminEnable": POEPSEInterfaceAdminEnable.ENABLED.value,
                    "powerPriority": PowerPriority.LOW.value,
                }
            ],
        )

    switch.set_vlan_id(1)
    switch.set_stp_settings(
        bpduHandlingMode="2",
        forwardDelay="15",
        helloTime="2",
        maxAge="20",
        pathCostDefaultValueType="2",
        bridgePriority="32768",
    )

    switch.set_stp_global_settings(
        settings=[{"STPOperationMode": STPOperationMode.RSTP.value, "enabled": "1"}]
    )

    for ports in ["gi0", "gi1", "gi2", "gi3", "gi4", "gi5", "gi6", "gi7"]:
        switch.set_security_interface_settings(
            interfaceName=ports,
            settings=[
                {
                    "maxMACCount": "0",
                    "lockInterfaceAdminEnabled": LockInterfaceAdminEnabled.UNLOCKED.value,
                    "learningMode": LearningMode.SECURE_DELETE_ON_RESET.value,
                }
            ],
        )

    switch.set_forwarding_global_settings(settings=[{"agingInterval": 300}])
    switch.set_interface_8021x_settings(
        interfaceName="gi0",
        settings=[
            {
                "MACAuthenticationMethod": MACAuthenticationMethod.EAPOL_ONLY.value,
                "hostMode": HostMode.MULTIPLE.value,
                "adminPortControlType": AdminPortControlType.FORCE_AUTHORIZED.value,
                "maxEAPRequestNo": "2",
                "quietPeriod": "60",
                "reauthenticationPeriod": "3600",
                "serverTimeout": "30",
                "supplicantTimeout": "30",
                "resendingEAP": "30",
                "actionOnViolationType": ActionOnViolationType.DISCARD.value,
            }
        ],
    )

    # TODO TYPES and LACPPortList root lines 2500....
    switch.set_interface_8023_settings(
        interfaceName="gi0",
        settings=[
            {
                "autoNegotiationAdminEnabled": "1",
                "MDIAdminMode": "3",
                "actorPortPriority": "1",
                "actorPortAdminTimeout": "2",
                "speedAdmin": "1000",
            }
        ],
    )

    # dump the config
    switch.get_sections_xml(
        [
            Sections.EWS_SERVICE_TABLE.value,
            Sections.VLAN_INTERFACE_IS_LIST.value,
            get_section_query(
                Sections.LLDP_INTERFACE_LIST.value, {"interfaceName": "te1"}
            ),
            Sections.CDP_INTERFACE_LIST.value,
            Sections.LAN1_MODULE_INTERFACE_TABLE.value,
            Sections.LAN1_INP_COS_MAPPING_INTERFACE_TABLE.value,
            Sections.LAN1_OUT_QUEUE_MAPPING_INTERFACE_TABLE.value,
            Sections.LAN1_x86_PFC_TABLE.value,
            Sections.STP.value,
            Sections.SPANNING_TREE_GLOBAL_PARAM.value,
        ]
    )

    # switch.get_sections_xml(
    #     [Sections.FULL_INTERFACE_LIST.value, Sections.VLAN_LIST.value]
    # )
