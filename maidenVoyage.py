import logging
import serial
import traceback
import sys
import picamera
import picamera.array
import math

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

    def fullRun(self):
        print "Taking control of self.actuatorCmd"
        self.objMan.ActuatorCommand.metadata.access = UAVMetaDataObject.Access.READONLY
        self.objMan.ActuatorCommand.metadata.updated()

        # start up the rotors but not moving yet
        self.throttle(1000)

        # wait until lights are green
        while !self.generator_working():
            sleep(1)

        # move up to comfortable height
        self.throttle(1800)
        sleep(1)
        self.throttle(1500)

        # move forward until distance is halved, count the seconds
        self.pitch(1300)
        self.throttle(1700)
        start_time = time.time()
            # check when we reach the half way point - count seconds
        elapsed_time = 2 #time.time() - start_time

        # stop
        self.pitch(1500)
        self.throttle(1500)

        # move left for twice the seconds
        self.row(1300)
        self.throttle(1700)
        sleep(elapsed_time * 2)

        # check generator
        self.row(1500)
        self.throttle(1500)

        print 'position1: ' self.generator_working()

        # 90 degree turn to the left
        self.yaw(1000)
        sleep(1)
        self.yaw(1500)

        # check generator 2
        print 'position2: ' self.generator_working()

        # 90 degree turn to the left
        self.yaw(1000)
        sleep(1)
        self.yaw(1500)

        # check generator 3
        print 'position3: ' self.generator_working()

        # move left for twice the seconds
        self.row(1300)
        self.throttle(1700)
        sleep(elapsed_time * 2)

        # move forward for the seconds
        self.pitch(1300)
        self.throttle(1700)
        sleep(elapsed_time)

        # drop down
        self.throttle(1000)
        sleep(10)

    def driveServo(self):
        print "Taking control of self.actuatorCmd"
        self.objMan.ActuatorCommand.metadata.access = UAVMetaDataObject.Access.READONLY
        self.objMan.ActuatorCommand.metadata.updated()

        # start up the rotors but not moving yet
        self.throttle(1100)
        sleep(2)
        print "I am working so well : ",self.generator_working()

        # lift up for 1 sec
        self.throttle(1700)
        sleep(1)

        self.throttle(1500)
        self.yaw(1000)
        sleep(3)

        self.yaw(2000)
        sleep(3)

        self.yaw(1000)
        sleep(3)

        self.throttle(1700)
        self.pitch(1400)
        sleep(1)

        self.pitch(1600)
        self.throttle(1000)
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

    def generator_working(self):
        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (400, 400)
                camera.start_preview()
                time.sleep(2)
                camera.capture(stream, 'rgb')
                # Show size of RGB data
                print(stream.array.shape)
                red_green_balance=0
                for i in range(0,stream.array.shape[0]/3):
                    h,s,v = self.rgb2hsv(stream.array[i],stream.array[i+1],stream.array[i+2])
                    if v <50:
                        if h<60 or h>300:
                            red_green_balance-=1
                        elif h>60 and h<180:
                            red_green_balance+=1

                if red_green_balance>0:
                    return True
                else:
                    return False



    def rgb2hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df / mx
        v = mx
        return h, s, v



def printUsage():
    appName = os.path.basename(sys.argv[0])


if __name__ == '__main__':

    if len(sys.argv) > 2:
        print "ERROR: Incorrect number of arguments"
        printUsage()
        sys.exit(2)

    port = sys.argv[1] or "/dev/ttyAMA0"

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
