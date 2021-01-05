import gpio_pin
import os
# import psutil
import RPi.GPIO as gpio
from spm_conn import SPMConn
import time

context = {
    "state": None
}

# SPM connection is instantiated during start
conn = None

# PWM instance to control LED (only available for version 2.X)
led_pwm = None


def heartbeat_handler():
    """
    Triggers SPM heartbeat and fires power on event when booting.
    """

    # try:

    #     # Check if not in state on
    #     if context["state"] != "on":

    #         # Get current status
    #         res = conn.status()

    #         old_state = context["state"]
    #         new_state = res["last_state"]["up"]

    #         # On first time only
    #         if old_state == None:

    #             # Trigger last off state event if last boot time is found
    #             try:
    #                 boot_time = __salt__["rpi.boot_time"]().get("value", None)
    #                 if boot_time == None:
    #                     log.warning("Last boot time could not be determined")
    #                 else:
    #                    # Last boot time is considered identical to last power off time because of 'fake-hwclock'
    #                     edmp.trigger_event({
    #                         "timestamp": boot_time
    #                     }, "system/power/last_off")
    #             except Exception as ex:
    #                 log.warning("Unable to trigger last system off event: {:}".format(ex))

    #             # Trigger recover state event
    #             if res["last_trigger"]["down"] not in ["none", "rpi"]:
    #                 log.warning("Recovery due to SPM trigger '{:}'".format(res["last_trigger"]["down"]))

    #                 edmp.trigger_event({
    #                     "trigger": res["last_trigger"]["down"]
    #                 }, "system/power/recover")

    #         # Check if state has changed
    #         if old_state != new_state:
    #             context["state"] = new_state

    #             # Trigger state event
    #             edmp.trigger_event({
    #                 "trigger": res["last_trigger"]["up"],
    #                 "awaken": res["last_state"]["down"]
    #             }, "system/power/{:}{:}".format("_" if new_state in ["booting"] else "", new_state))

    # finally:

    # Trigger heartbeat as normal
    conn.heartbeat()


def reset_handler():
    """
    Reset/restart ATtiny. 
    """

    ret = {}

    try:

        print("Setting GPIO output pin {:} high".format(gpio_pin.HOLD_PWR))
        gpio.output(gpio_pin.HOLD_PWR, gpio.HIGH)

        print("Resetting ATtiny")
        gpio.output(gpio_pin.SPM_RESET, gpio.LOW)

        # Keep pin low for a while
        time.sleep(.1)

        gpio.output(gpio_pin.SPM_RESET, gpio.HIGH)

    finally:

        print("Sleeping for 1 sec to give ATtiny time to recover")
        time.sleep(1)

        print("Setting GPIO output pin {:} low".format(gpio_pin.HOLD_PWR))
        gpio.output(gpio_pin.HOLD_PWR, gpio.LOW)

    return ret

def main():
    try:

        # Give process higher priority
        # psutil.Process(os.getpid()).nice(-1)

        # Initialize GPIO
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)

        gpio.setup(gpio_pin.HOLD_PWR, gpio.OUT, initial=gpio.LOW)
        gpio.setup(gpio_pin.SPM_RESET, gpio.OUT, initial=gpio.HIGH)

        # Initialize SPM connection
        global conn

        conn = SPMConn()
        conn.setup()

        print(reset_handler())
        # print(conn.heartbeat_timeout())
        # print(conn.sleep_interval())
        # print(conn.version())
        # print(conn.status())
        # heartbeat_handler()

    except Exception:
        print("Failed to start SPM manager")
        
        raise
    finally:
        print("Stopping SPM manager")

        if getattr(conn, "is_open", False) and conn.is_open():
            try:
                conn.close()
            except:
                print("Failed to close SPM connection")

if __name__ == "__main__":
    main()
