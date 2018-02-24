import logging
import serial
import traceback
import sys
import picamera
import picamera.array
import math

from time import sleep
import RPi.GPIO as GPIO

#set up GPIO
GPIO.setmode(GPIO.BOARD)

throttle_pin = 7
pitch_pin = 37
yaw_pin = 22
roll_pin = 32

GPIO.setup(throttle_pin, GPIO.OUT)
GPIO.setup(pitch_pin, GPIO.OUT)
GPIO.setup(yaw_pin, GPIO.OUT)
GPIO.setup(roll_pin, GPIO.OUT)

def _hex02(value):
    return "%02X" % value


class UavtalkDemo():
    def __init__(self):
        self.throttle_var = GPIO.PWM(throttle_pin, 50)
        self.throttle_var.start(0)
        self.yaw_var = GPIO.PWM(yaw_pin, 50)
        self.yaw_var.start(0)
        self.pitch_var = GPIO.PWM(pitch_pin, 50)
        self.pitch_var.start(0)
        self.roll_var = GPIO.PWM(roll_pin, 50)
        self.roll_var.start(0)

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

        # start up the rotors but not moving yet
        self.throttle(1100)

        #
        # self.throttle(1100)
        # sleep(2)
        # print "I am working so well : ",self.generator_working()
        #
        # # lift up for 1 sec
        # self.throttle(1700)
        # sleep(1)
        #
        # self.throttle(1500)
        # self.yaw(1000)
        # sleep(3)
        #
        # self.yaw(2000)
        # sleep(3)
        #
        # self.yaw(1000)
        # sleep(3)
        #
        # self.throttle(1700)
        # self.pitch(1400)
        # sleep(1)
        #
        # self.pitch(1600)
        # self.throttle(1000)
        # sleep(4)

    def calculateDc(self, value):
        return (value - 1000) / 10

    def throttle(self, value):
        self.throttle_var.ChangeDutyCycle(self.calculateDc(1100))  # where 0.0 <= dc <= 100.0

    def roll(self, value):
        GPIO.output()

    def pitch(self, value):
        GPIO.output()

    def yaw(self, value):
        GPIO.output()

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

    # Log everything, and send it to stderr.
    logging.basicConfig(level=logging.INFO)

    try:

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
