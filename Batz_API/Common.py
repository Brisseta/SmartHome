import threading
from datetime import date
import time
# import RPi.GPIO as GPIO
import huaweisms.api.sms
import huaweisms.api.user
import huaweisms.api.wlan
import win32timezone
from rest_framework.utils import json

import Batz_API
from Batz_API import models
from Batz_API.models import TriggerLog

with open('../ressouces.json', 'r') as f:
    ressource_json = json.load(f)


def just_log(some_text):
    return win32timezone.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + some_text


def commit(trigger):
    to_commit = TriggerLog(trigger_name=trigger.__getattribute__("trigger_name"),
                           trigger_data=trigger.__getattribute__("trigger_data"),
                           trigger_date=trigger.__getattribute__("trigger_date"))
    to_commit.save()


def change_trigger_status(trigger, value):
    trigger = models.Trigger.objects.get(trigger_name=trigger)
    trigger.trigger_data = value
    trigger.save(force_update=True)
    commit(trigger)


class CheckTemperature(threading.Thread):

    def __init__(self, room1, room2, room3):
        threading.Thread.__init__(self)
        self.room1 = room1
        self.roo2 = room2
        self.roo3 = room3
        # initialisation de la variable qui portera le résultat
        self.result = None

    def run(self):
        """Lance le check status en tâche de fond et stocke le résultat en BDD dans la table trigger"""

    def result(self):
        """Renvoie le résultat lorsqu'il est connu"""
        return self.result


class BinaryInput(threading.Thread):

    def __init__(self, room1, room2, room3):
        threading.Thread.__init__(self)
        self.room1 = room1
        self.roo2 = room2
        self.roo3 = room3
        # initialisation de la variable qui portera le résultat
        self.result = None

    def run(self):
        """Lance le check status en tâche de fond et stocke le résultat en BDD dans la table trigger"""

    def result(self):
        """Renvoie le résultat lorsqu'il est connu"""
        return self.result


class BinaryOutput(threading.Thread):

    def __init__(self, gpio, state, lib):
        threading.Thread.__init__(self)
        self.gpio = gpio
        self.state = state
        self.lib = lib

    def run(self):
        # GPIO.cleanup()
        # self.setmode(GPIO.BCM)
        # GPIO.setup(self.gpio,GPIO.OUT)
        # if self.state == 0:
        #     GPIO.output(self.gpio,GPIO.LOW)
        # elif self.state == 1
        #     GPIO.output(self.gpio, GPIO.HIGH)
        # time.sleep(1)
        # GPIO.cleanup()
        self.notify()
        return 0

    def notify(self):
        event_du_log = threading.Event()  # on crée un objet de type Event
        event_du_log.clear()  # simple clear de précaution
        thread_du_log = SendToLog(event_du_log, severity="INFO",
                                  content=just_log("Set state to " + self.state + " for " + self.lib))
        thread_du_log.start()  # démarre le thread,
        event_du_log.wait()  # on attend la fin du get
        #         Testing
        print(just_log("Set state to " + self.state + " for " + self.lib))


class SendSMS(threading.Thread, ):
    def __init__(self, connetivity_context, event, contact, text):  # event = objet Event
        threading.Thread.__init__(self)  # = donnée supplémentaire
        self.connetivity_context = None
        self.event = event  # on garde un accès à l'objet Event
        self.contact = contact
        self.text = text
        self.connectivity = connetivity_context

    def run(self, ):
        # -*-coding:Latin-1 -*
        if not self.connetivity_context:
            print(just_log("SENDSMS function failed because 4G dongle cannot be reached"))
        else:
            try:
                ctx = huaweisms.api.user.quick_login("admin", ressource_json["MODEM_PASSWD"])
                try:
                    # sending sms
                    huaweisms.api.sms.send_sms(
                        ctx, Batz_API.models.Contact.objects.get(
                            contact_phonenumber=self.contact).contact_phonenumber,
                        self.text
                    )
                    event_du_log = threading.Event()  # on crée un objet de type Event
                    event_du_log.clear()  # simple clear de précaution
                    thread_du_log = SendToLog(event_du_log, severity="INFO",
                                              content="sending to" + Batz_API.models.Contact.objects.get(
                                                  contact_phonenumber=self.contact).contact_phonenumber + " \n text : " + self.text)
                    thread_du_log.start()  # démarre le thread,
                    event_du_log.wait()  # on attend la fin du get
                except EOFError:
                    print("Error")
            except ConnectionError:
                event_du_log = threading.Event()  # on crée un objet de type Event
                event_du_log.clear()  # simple clear de précaution
                thread_du_log = SendToLog(event_du_log, severity="ERROR", content=
                "Connection au dongle interrompue")
                thread_du_log.start()  # démarre le thread,
                event_du_log.wait()  # on attend la fin du get

        self.event.set()


class SendToLog(threading.Thread, ):
    def __init__(self, event, severity, content):  # event = objet Event
        threading.Thread.__init__(self)  # = donnée supplémentaire
        self.event = event  # on garde un accès à l'objet Event
        self.severity = severity
        self.content = content

    def run(self):
        tempLog = Batz_API.models.Log.create(log_severity=self.severity, log_date=date.today(), log_data=self.content)
        tempLog.save()
        self.event.set()