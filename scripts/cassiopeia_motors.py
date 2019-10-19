#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from collections import namedtuple
from math import cos
from math import pi
import Jetson.GPIO as GPIO

Motor = namedtuple("Motor", ["pin0", "pin1", "pwm_pin"])
motor_left = Motor(pin0 = 15, pin1 = 13, pwm_pin = 11)
motor_right = Motor(pin0 = 19, pin1 = 21, pwm_pin = 23)

def clamp(minimum, x, maximum):
    if x < minimum:
        return minimum
    elif x > maximum:
        return maximum
    else:
        return x

def normclamp(x):
    return clamp(-1, x, 1)

def outputs(pins, vals):
    for i in range(0, len(pins)):
        GPIO.output(pins[i], vals[i])

def set_speed(motor, speed):
    GPIO.output(motor.pwn_pin, 1)
    if -1 <= speed < -0.5:
        GPIO.output(motor.pin1, 0)
        GPIO.output(motor.pin0, 1)
    elif -0.5 <= speed <= 0:
        GPIO.output(motor.pin1, 0)
        GPIO.output(motor.pin0, 0)
    elif 0 < speed <= 1:
        GPIO.output(motor.pin1, 1)
        GPIO.output(motor.pin0, 0)

def callback(data):
    speed = data.linear.z
    direction = clamp(-1, data.angular.y, 1) * pi/2 + pi/2
    set_speed(0, normclamp(2*cos(direction)+1)*speed)
    set_speed(1, normclamp(-2*cos(direction)+1)*speed)

def listener():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor_left, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(motor_right, GPIO.OUT, initial=GPIO.LOW)

    rospy.init_node('cassiopeia_motors')

    rospy.Subscriber('cassiopeia/motors_control', Twist, callback)
    
    rospy.spin()

if __name__=='__main__':
    listener()
    GPIO.cleanup()