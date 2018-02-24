import logging
import serial
import traceback
import sys

from time import sleep
from librepilot.uavtalk.uavobject import *
from librepilot.uavtalk.uavtalk import *
from librepilot.uavtalk.objectManager import *
from librepilot.uavtalk.connectionManager import *


def _hex02(value):
    return "%02X" % value


class UavtalkDemo():
    def __init__(self):
        self.nbUpdates = 0
        self.lastRateCalc = time.time()
        self.updateRate = 0
        self.objMan = None
        self.connMan = None

    def setup(self, port):
        print "Opening Port \"%s\"" % port
        if port[:3].upper() == "COM":
            _port = int(port[3:]) - 1
        else:
            _port = port
        serPort = serial.Serial(_port, 57600, timeout=.5)
        if not serPort.isOpen():
            raise IOError("Failed to open serial port")

        print "Creating UavTalk"
        self.uavTalk = UavTalk(serPort, None)

        print "Starting ObjectManager"
        self.objMan = ObjManager(self.uavTalk)
        self.objMan.importDefinitions()

        print "Starting UavTalk"
        self.uavTalk.start()

        print "Starting ConnectionManager"
        self.connMan = ConnectionManager(self.uavTalk, self.objMan)

        print "Connecting...",
        self.connMan.connect()
        print "Connected"

        print "Getting all Data"
        self.objMan.requestAllObjUpdate()

    # print "SN:",
    # sn = self.objMan.FirmwareIAPObj.CPUSerial.value
    # print "".join(map(_hex02, sn))

    def stop(self):
        if self.uavTalk:
            print "Stopping UavTalk"
            self.uavTalk.stop()

    def showAttitudeViaObserver(self):
        print "Request fast periodic updates for AttitudeState"
        self.objMan.AttitudeState.metadata.telemetryUpdateMode = UAVMetaDataObject.UpdateMode.PERIODIC
        self.objMan.AttitudeState.metadata.telemetryUpdatePeriod.value = 50
        self.objMan.AttitudeState.metadata.updated()

        print "Install Observer for AttitudeState updates\n"
        self.objMan.regObjectObserver(self.objMan.AttitudeState, self, "_onAttitudeUpdate")
        # Spin until we get interrupted
        while True:
            time.sleep(1)

    def showAttitudeViaWait(self):
        print "Request fast periodic updates for AttitudeState"
        self.objMan.AttitudeState.metadata.telemetryUpdateMode = UAVMetaDataObject.UpdateMode.PERIODIC
        self.objMan.AttitudeState.metadata.telemetryUpdatePeriod.value = 50
        self.objMan.AttitudeState.metadata.updated()

        while True:
            self.objMan.AttitudeState.waitUpdate()
            self._onAttitudeUpdate(self.objMan.AttitudeState)

    def showAttitudeViaGet(self):
        while True:
            self.objMan.AttitudeState.getUpdate()
            self._onAttitudeUpdate(self.objMan.AttitudeState)

    def _onAttitudeUpdate(self, args):
        self.nbUpdates += 1

        now = time.time()
        if now - self.lastRateCalc > 1:
            self.updateRate = self.nbUpdates / (now - self.lastRateCalc)
            self.lastRateCalc = now
            self.nbUpdates = 0

        if self.nbUpdates & 1:
            dot = "."
        else:
            dot = " "

        print " %s Rate: %02.1f Hz  " % (dot, self.updateRate),

        roll = self.objMan.AttitudeState.Roll.value
        print "RPY: %f %f %f " % (self.objMan.AttitudeState.Roll.value, self.objMan.AttitudeState.Pitch.value,
                                  self.objMan.AttitudeState.Yaw.value) + " "

    # return
    #    print "Roll: %f " % roll,
    #    i = roll/90
    #    if i<-1: i=-1
    #    if i>1: i= 1
    #    i = int((i+1)*15)
    #    print "-"*i+"*"+"-"*(30-i)+" \r",

    def driveServo(self):
        print "Taking control of self.actuatorCmd"
        self.objMan.ActuatorCommand.metadata.access = UAVMetaDataObject.Access.READONLY
        self.objMan.ActuatorCommand.metadata.updated()

        while True:
            throttle(1100)
            sleep(2)

            throttle(1700)
            sleep(1)

            throttle(1500)
            yaw(1000)
            sleep(3)

            yaw(2000)
            sleep(3)

            yaw(1000)
            sleep(3)

            throttle(1700)
            pitch(1400)
            sleep(1)

            pitch(1600)
            throttle(1000)
            sleep(4)

    def throttle(self, value):
        self.objMan.ActuatorCommand.Channel.value[0] = value
        self.objMan.ActuatorCommand.updated()

    def roll(self, value):
        self.objMan.ActuatorCommand.Channel.value[1] = value
        self.objMan.ActuatorCommand.updated()

    def pitch(self, value):
        self.objMan.ActuatorCommand.Channel.value[2] = value
        self.objMan.ActuatorCommand.updated()

    def yaw(self, value):
        self.objMan.ActuatorCommand.Channel.value[3] = value
        self.objMan.ActuatorCommand.updated()

def printUsage():
    appName = os.path.basename(sys.argv[0])


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "ERROR: Incorrect number of arguments"
        printUsage()
        sys.exit(2)

    port = sys.argv[1]

    # Log everything, and send it to stderr.
    logging.basicConfig(level=logging.INFO)

    try:
        demo = UavtalkDemo()
        demo.setup(port)

        demo.driveServo()  # will not return

    except KeyboardInterrupt:
        pass
    except Exception, e:
        print
        print "An error occured: ", e
        print
        traceback.print_exc()

    print

    try:
        demo.stop()
    except Exception:
        pass
