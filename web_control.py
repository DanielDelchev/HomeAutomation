from bottle import Bottle, template, static_file, response, request, app
import bottle
import RPi.GPIO as GPIO
import pin_controls as PINS
import threading
import json
import sys
import time
import uuid
from datetime import datetime as mytime
import datetime
from beaker.middleware import SessionMiddleware
from cork import Cork
import logging


logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)



# Use users.json and roles.json in the local conf directory
aaa = Cork('conf', email_sender='email@gmail.com', smtp_url='www.example.com')

# alias the authorization decorator with defaults
authorize = aaa.make_auth_decorator(fail_redirect="/login", role="user")


app = bottle.app()

session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': 'please use a random key and keep it secret!',
    'session.httponly': True,
    'session.timeout': 3600*1, # 1 hour
    'session.type': 'cookie',
    'session.validate_key': True,
}

app = SessionMiddleware(app, session_opts)


# #  Bottle methods  # #

def postd():
    return bottle.request.forms


def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()


@bottle.post('/login')
def login():
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')

@bottle.route('/logout')
def logout():
    aaa.logout(success_redirect='/login')    


@bottle.route('/')
@authorize()
def index():
    return home()

# Admin-only pages

@bottle.route('/admin')
@authorize(role="admin", fail_redirect='/sorry_page')
@bottle.view('admin_page.tpl')
def admin():
    return dict(
        current_user = aaa.current_user,
        users = aaa.list_users(),
        roles = aaa.list_roles()
    )


@bottle.post('/create_user')
@authorize(role="admin", fail_redirect='/sorry_page')
def create_user():
    try:
        aaa.create_user(postd().username, postd().role, postd().password)
        return admin()
    except Exception as e:
        print (repr(e))        
        return admin()


@bottle.post('/delete_user')
@authorize(role="admin", fail_redirect='/sorry_page')
def delete_user():
    try:
        aaa.delete_user(post_get('username'))
        return admin()
    except Exception as e:
        print (repr(e))
        return admin()


# Static pages

@bottle.route('/login')
def login_form():
    return template('login.tpl')


@bottle.route('/sorry_page')
def sorry_page():
    return template('sorry_page.tpl') 


    
##############################################################################################################################################################################################3    

lock = threading.Lock()
'''monitor'''

lockLists = threading.Lock()
'''monitor'''

RELAY1_TIMERS = []
RELAY2_TIMERS = []

RELAY1_APPOINTMENTS = []
RELAY2_APPOINTMENTS = []


def getStatus(relay):
    # to avoid error if refresh is done
    # while server is shutting down
    # check if mode is still 11 (BCM=11)
    if (GPIO.getmode() != 11):
        GPIO.setmode(GPIO.BCM)
    if(PINS.getState(relay) == 0):
        return "on"
    else:
        return "off"
'''checks if a relay is on'''


@bottle.get('/state')
@bottle.get('state')
@authorize()
def state():
    with lock:
        pyDict = {
            'relay1': getStatus(PINS.PIN1),
            'relay2': getStatus(PINS.PIN2)
        }
        response.content_type = 'application/json'
        return json.dumps(pyDict)


@bottle.route('/home_page')
@bottle.route('home_page')
@bottle.view('home_page.tpl')
@authorize()
def home():
    return dict(
        current_user = aaa.current_user
    )
    

@bottle.route('/static/<filepath:path>')
def serverStatic(filepath):
    return static_file(filepath, root='./static/')
'''where & how to get static files (boolstrap.js.css, pictures etc.)'''


@bottle.get('/server_time')
@bottle.get('server_time')
@authorize()
def timer():
    serverTime = mytime.now()
    parsedTime = serverTime.strftime("%Y, %B, %d, %H:%M:%S")
    pyDict = {
        'time': parsedTime
    }
    response.content_type = 'application/json'
    return json.dumps(pyDict)


@bottle.get('/epoch_time')
@bottle.get('epoch_time')
@authorize()
def epoch_time():
    now = round(time.time())
    pyDict = {
        'epoch': now
    }
    response.content_type = 'application/json'
    return json.dumps(pyDict)


@bottle.get('/stop')
@bottle.get('stop')
@authorize()
def stop():
    with lock:
        PINS.clean()
    clearAllR1()
    clearAllR2()


@bottle.get('/shut_down')
@bottle.get('shut_down')
@authorize()
def shutDown():
    with lock:
        sys.stderr.close()


@bottle.get('/show_R1')
@bottle.get('show_R1')
@authorize()
def showR1():
    return template('show_relay1.tpl')


@bottle.get('/show_R2')
@bottle.get('show_R2')
@authorize()
def showR2():
    return template('show_relay2.tpl')


@bottle.get('/appoint')
@bottle.get('appoint')
@authorize()
def appoint():
    return template('make')


@bottle.get('/get_R1_appointments')
@bottle.get('get_R1_appointments')
@authorize()
def getAppointmentsR1():
    result = ""
    with lockLists:
        for i in sorted(RELAY1_APPOINTMENTS):
            result += str(i)
    result = result.replace("\r\n", "\n")
    result = result.replace("\n", "<br />\n")
    pyDict = {
            'content': result
        }
    response.content_type = 'application/json'
    return json.dumps(pyDict)
'''returns a formated string of all appointments for relay'''


@bottle.get('/get_R2_appointments')
@bottle.get('get_R2_appointments')
@authorize()
def getAppointmentsR2():
    result = ""
    with lockLists:
        for i in sorted(RELAY2_APPOINTMENTS):
            result += str(i)
    result = result.replace("\r\n", "\n")
    result = result.replace("\n", "<br />\n")
    pyDict = {
            'content': result
        }
    response.content_type = 'application/json'
    return json.dumps(pyDict)
'''returns a formated string of all appointments for relay'''


# used only for display
# first two arguments of init are strings representing datetime for the
# start and end of the appointment, third $ fourth are
# the epoch times for the start and end
# the _rev argument refers to whether the off time comes first
# _ID code is a uuid4 code for the appointment
class Appointment:
    def __init__(self, _start, _end, _epOn, _epOff, _rev, _IDcode):
        self.start = _start
        self.end = _end
        self.onTime = _epOn
        self.offTime = _epOff
        self.reversed = _rev
        self.ID = _IDcode

    def __repr__(self):
        if self.reversed:
            stringForm = "Appointment with ID:\n{0}\n(OFF) at: {1}\n".format(
                self.ID, self.end)
            stringForm += "(ON) at: {0}\n\n".format(self.start)
        else:
            stringForm = "Appointment with ID:\n{0}\n(ON) at: {1}\n".format(
                self.ID, self.start)
            stringForm += "(OFF) at: {0}\n\n".format(self.end)
        return stringForm

    def __str__(self):
        if self.reversed:
            stringForm = "Appointment with ID:\n{0}\n(OFF) at: {1}\n".format(
                self.ID, self.end)
            stringForm += "(ON) at: {0}\n\n".format(self.start)
        else:
            stringForm = "Appointment with ID:\n{0}\n(ON) at: {1}\n".format(
                self.ID, self.start)
            stringForm += "(OFF) at: {0}\n\n".format(self.end)
        return stringForm

    def __lt__(self, other):
        if self.reversed:
            one = self.offTime
        else:
            one = self.onTime

        if other.reversed:
            two = other.offTime
        else:
            two = other.onTime

        return one < two

    def expired(self):
        now = round(time.time())
        if (self.onTime < now) and (self.offTime < now):
            return True
        return False


class TimerID():
    def __init__(self, createdTimer, _ID):
        self.Timer = createdTimer
        self.ID = _ID


def relay1_private(data=None):
    if data is None:
        data = request.json['op']
    with lock:
        if data == 'on':
            PINS.switchState(PINS.PIN1, PINS.ON)
            return getStatus(PINS.PIN1)
        else:
            PINS.switchState(PINS.PIN1, PINS.OFF)
            return getStatus(PINS.PIN1)

def relay2_private(data=None):
    if data is None:
        data = request.json['op']
    with lock:
        if data == 'on':
            PINS.switchState(PINS.PIN2, PINS.ON)
            return getStatus(PINS.PIN2)
        else:
            PINS.switchState(PINS.PIN2, PINS.OFF)
            return getStatus(PINS.PIN2)
        
        
@bottle.post('/relay1')
@bottle.post('relay1')
@authorize()
def relay1(data=None):
    '''changes state of relay 1 "manually" (on click)'''
    return relay1_private(data)



@bottle.post('/relay2')
@bottle.post('relay2')
@authorize()
def relay2(data=None):
    '''changes state of relay 2 "manually" (on click)'''
    return relay2_private(data)



# this function sets up an event for a relay to occur
# in the future.It uses thread.Timer objects
# waiting time for Times is limited to nearly 45 days
# first two parameters in constructor are
# strings for the datetimes for turning on/off
# reversed is true if off time preceeds on time
# epOn and epOff are the epoch time of turning on/off
# relay - string representing which relay is refered
@bottle.post('/auto_relay')
@bottle.post('auto_relay')
@authorize()
def autoSwitchRelay(
    wordsOn=None, wordsOff=None, reversed=None,
    epOn=None, epOff=None, relay=None
        ):
    if wordsOn is None:
        wordsOn = request.json['str_on']
        wordsOff = request.json['str_off']
        reversed = request.json['rev']
        epOn = request.json['epoch_on']
        epOff = request.json['epoch_off']
        relay = request.json['rel_number']

    now = round(time.time())

    TimeUntilOn = epOn - now
    TimeUntilOff = epOff - now

    #  front_end does not allow such cases this is just in case
    if (TimeUntilOn <= 7 or TimeUntilOff <= 7):
        print("Backend ignored request.Interval shorter than 8 sec!")
        return 1

    _ID = uuid.uuid4()
    if relay == 'relay1':
        T = threading.Timer(TimeUntilOn, relay1_private, args=['on'])
        T.setDaemon(True)
        T2 = threading.Timer(TimeUntilOff, relay1_private, args=['off'])
        T2.setDaemon(True)

    if relay == 'relay2':
        T = threading.Timer(TimeUntilOn, relay2_private, args=['on'])
        T.setDaemon(True)
        T2 = threading.Timer(TimeUntilOff, relay2_private, args=['off'])
        T2.setDaemon(True)

    Apnt = Appointment(wordsOn, wordsOff, epOn, epOff, reversed, _ID)

    TimerID_ON = TimerID(T, _ID)
    TimerID_OFF = TimerID(T2, _ID)

    if relay == 'relay1':
        with lockLists:
            RELAY1_TIMERS.append(TimerID_ON)
            RELAY1_TIMERS.append(TimerID_OFF)
            RELAY1_APPOINTMENTS.append(Apnt)

    if relay == 'relay2':
        with lockLists:
            RELAY2_TIMERS.append(TimerID_ON)
            RELAY2_TIMERS.append(TimerID_OFF)
            RELAY2_APPOINTMENTS.append(Apnt)

    TimerID_ON.Timer.start()
    TimerID_OFF.Timer.start()

    return 0


def clearAllR1():
    with lockLists:
        for i in RELAY1_TIMERS:
            if i.Timer.is_alive():
                i.Timer.cancel()

        RELAY1_APPOINTMENTS[:] = []
        RELAY1_TIMERS[:] = []


def clearAllR2():
    with lockLists:
        for i in RELAY2_TIMERS:
            if i.Timer.is_alive():
                i.Timer.cancel()

        RELAY2_APPOINTMENTS[:] = []
        RELAY2_TIMERS[:] = []


@bottle.get('/eraseR1')
@bottle.get('eraseR1')
@authorize()
def eraseR1():
    clearAllR1()


@bottle.get('/eraseR2')
@bottle.get('eraseR2')
@authorize()
def eraseR2():
    clearAllR2()


# remove a single appointment for this relay
# identified through uuid code
# the code for the appointment and its two timers
# is the same
@bottle.post('/remove_singleR1')
@bottle.post('remove_singleR1')
@authorize()
def remove_singleR1(IDcode=None):
    if IDcode is None:
        IDcode = request.json['ID']
    IDcode = uuid.UUID(IDcode)
    with lockLists:
        for i in RELAY1_TIMERS:
            if i.ID == IDcode and i.Timer.is_alive():
                i.Timer.cancel()
        filtered = [x for x in RELAY1_TIMERS if x.ID != IDcode]
        RELAY1_TIMERS[:] = filtered
        filteredApnt = [x for x in RELAY1_APPOINTMENTS if x.ID != IDcode]
        RELAY1_APPOINTMENTS[:] = filteredApnt
    return 0


# remove a single appointment for this relay
# identified through uuid code
# the code for the appointment and its two timers
# is the same
@bottle.post('/remove_singleR2')
@bottle.post('remove_singleR2')
@authorize()
def remove_singleR2(IDcode=None):
    if IDcode is None:
        IDcode = request.json['ID']
    IDcode = uuid.UUID(IDcode)
    with lockLists:
        for i in RELAY2_TIMERS:
            if i.ID == IDcode and i.Timer.is_alive():
                i.Timer.cancel()
        filtered = [x for x in RELAY2_TIMERS if x.ID != IDcode]
        RELAY2_TIMERS[:] = filtered
        filteredApnt = [x for x in RELAY2_APPOINTMENTS if x.ID != IDcode]
        RELAY2_APPOINTMENTS[:] = filteredApnt
    return 0


# daemon thread periodically clearing the lists
# removing appointments that are outdated
# and threads that are no longer alive
def daemon():

    with lockLists:

        Temp1 = [x for x in RELAY1_TIMERS if x.Timer.is_alive() == True]
        RELAY1_TIMERS[:] = Temp1

        Temp2 = [x for x in RELAY2_TIMERS if x.Timer.is_alive() == True]
        RELAY2_TIMERS[:] = Temp2

        Temp3 = [x for x in RELAY1_APPOINTMENTS if x.expired() == False]
        RELAY1_APPOINTMENTS[:] = Temp3

        Temp4 = [x for x in RELAY2_APPOINTMENTS if x.expired() == False]
        RELAY2_APPOINTMENTS[:] = Temp4

    time.sleep(6)
    daemon()

reaper = threading.Thread(name='daemon', target=daemon)
reaper.setDaemon(True)


if __name__ == '__main__':
    PINS.init(PINS.PIN1, PINS.PIN2)
    reaper.start()
# bottle.debug(True); ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    bottle.run(app=app, quiet=False, reloader=True,host='192.168.137.1',port=8888);
    PINS.clean()
# localhost on cpu
# 192.168.0.103:8888 wireless home
# 192.168.137.1:8888 lan
