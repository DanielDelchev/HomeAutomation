import RPi.GPIO as GPIO
import time

SleepTimeL = 1


ON = False
OFF = True


PIN1 = 17
PIN2 = 23
'''specific pins on the board'''


def init(pin1, pin2):
    GPIO.setmode(GPIO.BCM)
    pinList = [pin1, pin2]
    for i in pinList:
        GPIO.setup(i, GPIO.OUT, initial=GPIO.HIGH)
'''picking BCM(Broadcom chip-specific pin numbers) -pin-numbering scheme
in contrast to BOARD(board numbering scheme)
set up pin to output with initial value , 1=True=GPIO.HIGH  (3.3
volts), 0=False=GPIO.LOW  (0 volts)'''


def switchState(pin, op):
    #  if the switch is pointless simply ignore the request
    if (GPIO.getmode() != 11):
        GPIO.setmode(GPIO.BCM)

    if (
        (op == GPIO.HIGH and getState(pin) == GPIO.HIGH)or
        (op == GPIO.LOW and getState(pin) == GPIO.LOW)
    ):
        return None

    try:
        GPIO.output(pin, op)
        time.sleep(SleepTimeL)
    except KeyboardInterrupt:
        print ("ERROR" + str(pin))
        GPIO.cleanup()
''' change the value (GPIO.LOW / GPIO.HIGH) of a pin
should something go wrong reset all pins that have been used by the
program so far'''


def getState(pin):
    return GPIO.input(pin)
'''Read value of a GPIO pin. return 0 (GPIO.LOW) or 1 (GPIO.HIGH)'''


def clean():
    GPIO.cleanup()
'''reset all pins that have been used by this program so far'''
