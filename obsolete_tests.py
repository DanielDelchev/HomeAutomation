import unittest
import web_control as control
import pin_controls as PINS
import RPi.GPIO as GPIO
import time
from beaker.middleware import SessionMiddleware
from cork import Cork
import logging

class TestPins(unittest.TestCase):
    def testInit(self):
        PINS.init(PINS.PIN1, PINS.PIN2)
        BCM = 11
#  check if the board numeration mode matches BCM mode
        self.assertEqual(BCM, GPIO.getmode())
#  check if both pins are raised (OFF state) after initialiazation
        self.assertEqual(GPIO.HIGH, GPIO.input(PINS.PIN1))
        self.assertEqual(GPIO.HIGH, GPIO.input(PINS.PIN2))

        PINS.clean()

    def testSwitch(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        PINS.switchState(PINS.PIN1, GPIO.LOW)
#  check if PIN's state matches the expected after the switch
        self.assertEqual(GPIO.LOW, GPIO.input(PINS.PIN1))

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.LOW)
#  check if PIN's state matches the expected after the switch
        PINS.switchState(PINS.PIN1, GPIO.HIGH)
        self.assertEqual(GPIO.HIGH, GPIO.input(PINS.PIN1))

        PINS.clean()

    def testGetState(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
#  check if the correct state of the PIN is returned
        self.assertEqual(GPIO.HIGH, PINS.getState(PINS.PIN1))

        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.LOW)
#  check if the correct state of the PIN is returned
        self.assertEqual(GPIO.LOW, PINS.getState(PINS.PIN2))

        PINS.clean()


class TestManualControl(unittest.TestCase):

    def testStatus(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
#  check if the correct status of the relay is returned
        self.assertEqual('off', control.getStatus(PINS.PIN1))

        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.LOW)
#  check if the correct status of the relay is returned
        self.assertEqual('on', control.getStatus(PINS.PIN2))

        PINS.clean()

    def testState(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.LOW)

        actual = control.state()
        expected1 = '{"relay2": "on", "relay1": "off"}'
        expected2 = '{"relay1": "off", "relay2": "on"}'
        self.assertTrue((actual == expected1) or (actual == expected2))

        PINS.clean()

    def testManualSwitch(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.LOW)

        control.relay1('on')
        control.relay2('off')

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertTrue(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.relay1('off')
        control.relay2('on')

        time.sleep(3)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        PINS.clean()


class appointmentTester(unittest.TestCase):
    def testLessThan(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        appointment1 = control.Appointment(
            'N/A', 'N/A', 150, 90, True, 'code'
            )
        appointment2 = control.Appointment(
            'N/A', 'N/A', 100, 200, False, 'code'
            )

        self.assertTrue(appointment1 < appointment2)

        appointment3 = control.Appointment(
            'N/A', 'N/A', 100, 150, False, 'code'
            )
        appointment4 = control.Appointment(
            'N/A', 'N/A', 70, 200, False, 'code'
            )
        #  test operator <
        self.assertFalse(appointment3 < appointment4)

        control.clearAllR1()
        control.clearAllR2()

    def testExpired(self):
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        appointmentX = control.Appointment(
            'N/A', 'N/A', 100, 150, False, 'code'
            )
        self.assertTrue(appointmentX.expired())

        future = round(time.time()) + 5
        appointmentY = control.Appointment(
            'N/A', 'N/A', 150, future, False, 'code'
            )
        self.assertFalse(appointmentY.expired())

        time.sleep(7)
        self.assertTrue(appointmentY.expired())

        control.clearAllR1()
        control.clearAllR2()


class AutoSwitchTester(unittest.TestCase):
    # tests if auto switch performs properly
    # also checks if different events
    # interfere with each other in an
    # unexpected or unusuall manner
    def testSimultaniously1(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 16, epOff=now + 20, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 16, epOff=now + 20, relay='relay2'
            )

        time.sleep(18)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(5)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testSimultaniously2(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.LOW)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 16, epOff=now + 20, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=True,
            epOn=now + 20, epOff=now + 16, relay='relay2'
            )

        time.sleep(18)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(5)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testOverlap1(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 15, epOff=now + 25, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 20, epOff=now + 30, relay='relay2'
            )

        time.sleep(18)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(5)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(4)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(7)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testOverlap2(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=True,
            epOn=now + 30, epOff=now + 20, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 15, epOff=now + 25, relay='relay2'
            )

        time.sleep(18)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(5)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(4)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(7)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testDominantOverlap1(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=True,
            epOn=now + 30, epOff=now + 10, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 15, epOff=now + 25, relay='relay2'
            )

        time.sleep(12)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(5)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(6)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testDominantOverlap2(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.LOW)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=True,
            epOn=now + 10, epOff=now + 30, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 25, epOff=now + 15, relay='relay2'
            )

        time.sleep(12)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(5)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(6)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testHomogenousOverlap(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 30, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 15, epOff=now + 20, relay='relay1'
            )

        time.sleep(12)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)

        time.sleep(5)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)

        time.sleep(8)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)

        time.sleep(7)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testHeterogenousOverlap(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 30, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=True,
            epOn=now + 20, epOff=now + 15, relay='relay1'
            )

        time.sleep(12)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)

        time.sleep(5)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)

        time.sleep(8)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)

        time.sleep(7)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testDigitalAnalogue(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 45, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 20, relay='relay2'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 25, epOff=now + 35, relay='relay2'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 40, epOff=now + 45, relay='relay2'
            )

        time.sleep(13)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(5)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(5)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(8)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    def testDigitalDigital(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 17, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 17, epOff=now + 27, relay='relay2'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 27, epOff=now + 37, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 37, epOff=now + 47, relay='relay2'
            )

        time.sleep(13)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(8)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.LOW)

        time.sleep(10)
        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()


class EraseTester(unittest.TestCase):
    # test if clearing events for one relay
    # clears it correctly without influencing
    # the other relay

    def testErase(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 3600, epOff=now + 7200, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 1800, epOff=now + 3600, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=True,
            epOn=now + 3600, epOff=now + 1800, relay='relay2'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 3600, epOff=now + 9000, relay='relay2'
            )

        time.sleep(3)

        self.assertEqual(len(control.RELAY1_TIMERS), 4)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 2)

        self.assertEqual(len(control.RELAY2_TIMERS), 4)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 2)

        control.eraseR1()

        time.sleep(3)

        self.assertEqual(len(control.RELAY1_TIMERS), 0)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 0)

        self.assertEqual(len(control.RELAY2_TIMERS), 4)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 2)

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 3600, epOff=now + 9000, relay='relay1'
            )

        control.eraseR2()

        time.sleep(3)

        self.assertEqual(len(control.RELAY1_TIMERS), 2)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 1)

        self.assertEqual(len(control.RELAY2_TIMERS), 0)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 0)

        control.clearAllR1()
        control.clearAllR2()

    # checks if removing a snigle appointment from a relay
    # works as expected
    def testRemoveSingle1(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 20, relay='relay1'
            )

        ID = control.RELAY1_APPOINTMENTS[0].ID

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 25, epOff=now + 35, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 3600, epOff=now + 7200, relay='relay2'
            )

        control.remove_singleR1(str(ID))

        time.sleep(15)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(7)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(6)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(10)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    # checks if removing a snigle appointment from a relay
    # works as expected
    def testRemoveSingle2(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 20, relay='relay1'
            )

        ID = control.RELAY1_APPOINTMENTS[0].ID

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 25, epOff=now + 35, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 3600, epOff=now + 7200, relay='relay2'
            )

        time.sleep(15)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.remove_singleR1(str(ID))

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(7)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(6)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.LOW)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        time.sleep(10)

        self.assertEqual(GPIO.input(PINS.PIN1), GPIO.HIGH)
        self.assertEqual(GPIO.input(PINS.PIN2), GPIO.HIGH)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

    # tests if the reaper
    # daemon thread clears
    # past events properly
    def testReaper(self):
        control.clearAllR1()
        control.clearAllR2()
        if (GPIO.getmode() != 11):
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(PINS.PIN1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(PINS.PIN2, GPIO.OUT, initial=GPIO.HIGH)

        now = round(time.time())

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 10, epOff=now + 30, relay='relay1'
            )

        control.autoSwitchRelay(
            wordsOn='N/A', wordsOff='N/A', reversed=False,
            epOn=now + 25, epOff=now + 40, relay='relay2'
            )

        control.reaper.start()

        self.assertEqual(len(control.RELAY1_TIMERS), 2)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 1)

        self.assertEqual(len(control.RELAY2_TIMERS), 2)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 1)

        time.sleep(19)

        self.assertEqual(len(control.RELAY1_TIMERS), 1)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 1)

        self.assertEqual(len(control.RELAY2_TIMERS), 2)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 1)

        time.sleep(18)

        self.assertEqual(len(control.RELAY1_TIMERS), 0)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 0)

        self.assertEqual(len(control.RELAY2_TIMERS), 1)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 1)

        time.sleep(15)

        self.assertEqual(len(control.RELAY1_TIMERS), 0)
        self.assertEqual(len(control.RELAY1_APPOINTMENTS), 0)

        self.assertEqual(len(control.RELAY2_TIMERS), 0)
        self.assertEqual(len(control.RELAY2_APPOINTMENTS), 0)

        control.clearAllR1()
        control.clearAllR2()
        PINS.clean()

if __name__ == '__main__':
    aaa.login('admin','admin')
    unittest.main()
    GPIO.setmode(GPIO.BCM)
PINS.clean()