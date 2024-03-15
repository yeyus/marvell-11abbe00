from switch.switch import SwitchConfigurationManager

DEFAULT_HOST = "169.254.1.0"
FORWARDED_HOST = "127.0.0.1:2363"

if __name__ == "__main__":
    switch = SwitchConfigurationManager(FORWARDED_HOST)
    sessionid = switch.login("cisco", "cisco")
    print(f"Your sessionID is {sessionid}")

    # infinite login timeout
    switch.set_max_idle_timeout(0)
