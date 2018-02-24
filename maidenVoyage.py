import logging
import argparse
import serial
import traceback
import sys
import picamera
import picamera.array
import math
import time

from time import sleep
import RPi.GPIO as GPIO

distance_pin1_trigger = 11
distance_pin2_trigger = 13
distance_pin3_trigger = 16
distance_pin4_trigger = 29
distance_pin5_trigger = 33

distance_pin1_read = 12
distance_pin2_read = 15
distance_pin3_read = 18
distance_pin4_read = 31
distance_pin5_read = 35

class UavtalkDemo():
    def __init__(self):
        #set up GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        throttle_pin = 36
        pitch_pin = 37
        yaw_pin = 40
        roll_pin = 38
        arm_pin = 32

        GPIO.setup(throttle_pin, GPIO.OUT)
        GPIO.setup(pitch_pin, GPIO.OUT)
        GPIO.setup(yaw_pin, GPIO.OUT)
        GPIO.setup(roll_pin, GPIO.OUT)
        GPIO.setup(arm_pin, GPIO.OUT)

        GPIO.setup(distance_pin1_trigger, GPIO.OUT)
        GPIO.setup(distance_pin2_trigger, GPIO.OUT)
        GPIO.setup(distance_pin3_trigger, GPIO.OUT)
        GPIO.setup(distance_pin4_trigger, GPIO.OUT)
        GPIO.setup(distance_pin5_trigger, GPIO.OUT)

        GPIO.setup(distance_pin1_read, GPIO.IN)
        GPIO.setup(distance_pin2_read, GPIO.IN)
        GPIO.setup(distance_pin3_read, GPIO.IN)
        GPIO.setup(distance_pin4_read, GPIO.IN)
        GPIO.setup(distance_pin5_read, GPIO.IN)

        GPIO.output(arm_pin, GPIO.HIGH)
        self.throttle_var = GPIO.PWM(throttle_pin, 50)
        self.throttle_var.start(7)
        self.yaw_var = GPIO.PWM(yaw_pin, 50)
        self.yaw_var.start(7)
        self.pitch_var = GPIO.PWM(pitch_pin, 50)
        self.pitch_var.start(7)
        self.roll_var = GPIO.PWM(roll_pin, 50)
        self.roll_var.start(7)

        GPIO.output(distance_pin1_trigger, GPIO.HIGH)
        GPIO.output(distance_pin2_trigger, GPIO.HIGH)
        GPIO.output(distance_pin3_trigger, GPIO.HIGH)
        GPIO.output(distance_pin4_trigger, GPIO.HIGH)
        GPIO.output(distance_pin5_trigger, GPIO.HIGH)

    def fullRun(self):

        # start up the rotors but not moving yet
        self.throttle(1000)

        # wait until lights are green
        while not self.generator_working():
            sleep(1)

        # for flying: whenever sensor < 40 - counteract. --> need for variables
        # for throttle, pitch etc which will be configured by those events

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

        print 'position1: ', self.generator_working()

        # 90 degree turn to the left
        self.yaw(1000)
        sleep(1)
        self.yaw(1500)

        # check generator 2
        print 'position2: ', self.generator_working()

        # 90 degree turn to the left
        self.yaw(1000)
        sleep(1)
        self.yaw(1500)

        # check generator 3
        print 'position3: ', self.generator_working()

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

        print "drive servo"
        # start up the rotors but not moving yet
        sleep(1)

        self.throttle(1000)
        sleep(1)

        self.throttle(1010)
        sleep(1)

        GPIO.output(distance_pin1_trigger, 0)
        GPIO.output(distance_pin2_trigger, 0)#
        GPIO.output(distance_pin3_trigger, 0)
        GPIO.output(distance_pin4_trigger, 0)
        GPIO.output(distance_pin5_trigger, 0)
        sleep(0.01)

        GPIO.output(distance_pin1_trigger, 1)
        GPIO.output(distance_pin2_trigger, 1)
        GPIO.output(distance_pin3_trigger, 1)
        GPIO.output(distance_pin4_trigger, 1)
        GPIO.output(distance_pin5_trigger, 1)
        sleep(0.0001)

        start1, start2, start3, start4, start5 = time.time(), time.time(), time.time(), time.time(), time.time()

        GPIO.output(distance_pin1_trigger, 0)
        while GPIO.input(distance_pin1_read) == 0:
            start1 = time.time()
        while GPIO.input(distance_pin1_read) == 1:
            stop1 = time.time()

        GPIO.output(distance_pin2_trigger, 0)#
        while GPIO.input(distance_pin2_read) == 0:
            start2 = time.time()
        while GPIO.input(distance_pin2_read) == 1:
            stop2 = time.time()

        GPIO.output(distance_pin3_trigger, 0)
        while GPIO.input(distance_pin3_read) == 0:
            start3 = time.time()
        while GPIO.input(distance_pin3_read) == 1:
            stop3 = time.time()

        GPIO.output(distance_pin4_trigger, 0)
        while GPIO.input(distance_pin4_read) == 0:
            start4 = time.time()
        while GPIO.input(distance_pin4_read) == 1:
            stop4 = time.time()

        GPIO.output(distance_pin5_trigger, 0)
        while GPIO.input(distance_pin5_read) == 0:
            start5 = time.time()
        while GPIO.input(distance_pin5_read) == 1:
            stop5 = time.time()

        distance1 = (stop1 - start1) * 34000 / 2
        print(distance1)

        distance2 = (stop2 - start2) * 34000 / 2
        print(distance2)
        distance3 = (stop3 - start3) * 34000 / 2
        print(distance3)
        distance4 = (stop4 - start4) * 34000 / 2
        print(distance4)
        distance5 = (stop5 - start5) * 34000 / 2
        print(distance5)

        self.throttle(1050)
        sleep(1)

        self.throttle(1100)
        sleep(1)
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
        return ((value - 1000) / 10)

    def throttle(self, value):
        print "called throttle"
        print self.throttle_var
        self.throttle_var.ChangeDutyCycle(self.calculateDc(value))  # where 0.0 <= dc <= 100.0

    def roll(self, value):
        self.roll_var.ChangeDutyCycle(self.calculateDc(value))  # where 0.0 <= dc <= 100.0

    def pitch(self, value):
        self.pitch_var.ChangeDutyCycle(self.calculateDc(value))  # where 0.0 <= dc <= 100.0

    def yaw(self, value):
        self.yaw_var.ChangeDutyCycle(self.calculateDc(value))  # where 0.0 <= dc <= 100.0

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

    def startup():
        return False

    def move():
        return False

    def phhoto():
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


def main(args):

    # Log everything, and send it to stderr.
    #logging.basicConfig(level=logging.INFO)

    try:
        demo = UavtalkDemo()
        if args.action is "1":
            demo.startup()
        elif args.action is "2":
            demo.move()
        elif args.action is "3":
            demo.photo()
        elif args.action is "run_routine":
            demo.driveServo()  # will not return

    demo.throttle_var.stop()
    demo.pitch_var.stop()
    demo.yaw_var.stop()
    demo.roll_var.stop()
    GPIO.cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', help='throttle, pitch, yaw, run_routine')
    parser.add_argument('--value')
    args = parser.parse_args()
    main(parser.parse_args())
