from pybricks.hubs import CityHub
from pybricks.pupdevices import DCMotor, Light, Remote
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait, StopWatch
from uerrno import ENODEV, ETIMEDOUT
import ustruct  # byte(s) <> int conversion

hub = CityHub()
print("CityHub:", hub.system.name())
print("  Reset reason: ", hub.system.reset_reason())
print("  voltage: ", hub.battery.voltage(), "mV")
print("  current: ", hub.battery.current(), "mA")

sys_tick = StopWatch()

# --- Global variables/constants: ----------------------------------------------
# example:
speed = None
brightness = None
motor_on = True

# for check_button_2s_5s(): keep track how long button is pressed.
hub.system.set_stop_button(None)
hub_button_start = 0  # sys_tick time the press started

# for service_remote(): try to reconnect with a remote periodically
remote = None
REMOTE_PERIOD = 10000 # 10s
last_remote_search = -REMOTE_PERIOD # always try first service


# --- Loading/saving variables to flash: ---------------------------------------
def load_variables():
    bytes = hub.system.storage(offset=0, read=2)
    data = ustruct.unpack("BB", bytes)
    (speed_new,brightness_new) = data

    if speed_new > 200:
        speed_new = -50
    else:
        speed_new -= 100
    if brightness_new > 100:
        brightness_new = 50
    print("load:", bytes, data, "speed:", speed_new, "brightness:", brightness_new)
    
    return (speed_new, brightness_new)


def save_variables():
    global speed
    global brightness

    # prevent Flash wear:
    (speed_old, brightness_old) = load_variables()
    if speed != speed_old:
        byte = ustruct.pack("B", speed + 100)
        print("save speed:", speed,"as:", byte)
        hub.system.storage(offset = 0, write = byte)
    if brightness != brightness_old:
        byte = ustruct.pack("B", brightness)
        print("save brightness:", brightness, "as:", byte)
        hub.system.storage(offset = 1, write = byte)


# --- Hub with single button - check if pressed quickly, 2s or 5s --------------
def check_button_2s_5s():
    # returns False if button is not pressed
    # returns True if button is pressed quickly (<1.5s)
    # stops script if button is pressed for 2s (and released)
    # Turns off Hub if button is pressed for 5s
    global hub_button_start

    # if Button.CENTER in hub.buttons.pressed():  # multi-button hub
    if hub.button.pressed(): # single-button hub
        if hub_button_start == 0:        # start press time
            hub_button_start = sys_tick.time()
        elif (sys_tick.time() - hub_button_start) >= 5000:
            hub.system.shutdown()        # power off
    else:                                # button release or no press
        if hub_button_start > 0:         # a running press
            if (sys_tick.time() - hub_button_start) < 1500: # quick action
                hub_button_start = 0     # stop press time
                return True
            elif (sys_tick.time() - hub_button_start) < 4500:
                raise SystemExit         # Stop script
    return False


# --- try to reconnect with a remote periodically ------------------------------
# --- Function returns new speed/brightness, controlled by the buttons. --------
def service_remote():
    global remote
    global last_remote_search
    
    # try to (re-)connect to a remote periodically
    if not(remote):
        if (sys_tick.time() - last_remote_search) > REMOTE_PERIOD:
            print("searching remote...")
            try:  # to (re-)connect to a remote
                remote = Remote(name = None, timeout = 2000)
                if remote == None:
                    errno = ETIMEDOUT
                    print("Remote() returned None")
                    OSError(errno)
                print("Remote: " + remote.name())
                remote.light.on(Color.GREEN)
            except OSError as ex:
                if ex.errno != ETIMEDOUT:
                    raise
                remote = None
            last_remote_search = sys_tick.time()
        return (speed, brightness)  # return, service on next poll
    
    try:
        pressed = remote.buttons.pressed()
    except OSError as ex:
        if not ex.errno == ENODEV:
            raise
        print("Lost remote")
        remote = None  # empty handle
        last_remote_search = sys_tick.time()
        return (speed, brightness)

    if len(pressed) == 0:
        return (speed, brightness)


    speed_new = speed
    brightness_new = brightness

    # Port.A Motor speed:
    if Button.LEFT_PLUS in pressed:
        speed_new += 10
        if speed_new > 100:
            speed_new = 100
    if Button.LEFT_MINUS in pressed:
        speed_new -= 10
        if speed_new < -100:
            speed_new = -100
    if Button.LEFT in pressed:
        speed_new = 0
    # Port.B Light brightness:
    if Button.RIGHT_PLUS in pressed:
        brightness_new += 10
        if brightness_new > 100:
            brightness_new = 100
    if Button.RIGHT_MINUS in pressed:
        brightness_new -= 10
        if brightness_new < 0:
            brightness_new = 0
    if Button.RIGHT in pressed:
        brightness_new = 0

    return (speed_new, brightness_new)


# --- Initialize: --------------------------------------------------------------
(speed, brightness) = load_variables()
motor = DCMotor(Port.A)
light = Light(Port.B)
hub.light.on(Color.GREEN)

# start functionality before connecting to a remote
motor.dc(speed)
light.on(brightness)

while True:
    wait(100)
    if check_button_2s_5s():
        print("quick action")
        if motor_on:
            save_variables()
            motor_on = False
            motor.dc(0)
        else:
            motor_on = True
            motor.dc(speed)

    # do not set speed/brightness blindly to not interfere with code above
    (speed_new,brightness_new) = service_remote()
    if speed_new is not speed:
        speed = speed_new
        motor.dc(speed)
    if brightness_new is not brightness:
        brightness = brightness_new
        light.on(brightness)