from enum import Enum


def get_host(host):
    return f"https://{host}/"


def get_login_endpoint(host, user, password):
    return f"{get_host(host)}System.xml?action=login&user={user}&password={password}"


def get_logout_endpoint(host):
    return f"{get_host(host)}System.xml?action=logout"


def get_keep_alive_endpoint(host):
    return f"{get_host(host)}device/authenticate_user.xml"


def get_wcd_endpoint(host, queries=[]):
    return f"{get_host(host)}wcd?{''.join([query for query in queries])}"


class StatusCode(Enum):
    OK = "0"
    ENTRY_EXISTS = "3"
    AUTHENTICATION_ERROR = "4"
