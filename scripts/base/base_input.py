#!/usr/bin/env python3

import pygame
import pygame.joystick
from pygame.joystick import Joystick
import rospy
from cassiopeia.msg import Vector2
from cassiopeia.msg import CameraPosition
from cassiopeia.msg import Trit


# Configuration
use_wii_joy = True
use_dualshock_joy = False

wii_joy_index = 1
dualshock_joy_index = 0


camera_pub = None
direction_pub = None
shovel_pub = None
arm_pub = None

wii_joy_detected = True
dualshock_joy_detected = True


past_dir = (0, 0)
past_shovel = 0
past_arm = 0
past_camera = (0, 0)




def clamp(val, lower_bound, upper_bound):
    if val > upper_bound:
        return upper_bound
    if val < lower_bound:
        return lower_bound
    return val


def to_trit(val):
    return clamp(val, -1, 1)


def to_trit_msg(val):
    negative = val < 0
    magnitude = abs(val) > 0
    return Trit(negative=negative, magnitude=magnitude)


def setup():
    global camera_pub
    global direction_pub
    global shovel_pub
    global arm_pub
    pygame.init()
    camera_pub = rospy.Publisher('cassiopeia/control/camera/twist', CameraPosition, queue_size=1)
    direction_pub = rospy.Publisher('cassiopeia/control/direction', Vector2, queue_size=1)
    shovel_pub = rospy.Publisher('cassiopeia/control/shovel', Trit, queue_size=1)
    arm_pub = rospy.Publisher('cassiopeia/control/arm', Trit, queue_size=1)

    rospy.init_node('base_input', anonymous=False)


def loop():
    for event in pygame.event.get():
        pass

    global wii_joy_detected
    global dualshock_joy_detected
    joy_count = pygame.joystick.get_count()

    if use_wii_joy:
        if wii_joy_index <= joy_count - 1:
            if not wii_joy_detected:
                rospy.loginfo("Wiimote detected! Joy index: {}".format(wii_joy_index))
                wii_joy_detected = True
            wiimote_handler()
        elif wii_joy_detected:
            rospy.logwarn("Wiimote not detected. Joy index: {}".format(wii_joy_index))
            wii_joy_detected = False

    if use_dualshock_joy:
        if dualshock_joy_index <= joy_count - 1:
            if not dualshock_joy_detected:
                rospy.loginfo("Dualshock detected! Joy index: {}".format(dualshock_joy_index))
                dualshock_joy_detected = True
            dualshock_handler()
        elif dualshock_joy_detected:
            rospy.logwarn("Dualshock not detected. Joy index: {}".format(dualshock_joy_index))
            dualshock_joy_detected = False


def pub_direction(direction):
    global past_dir
    if direction == past_dir:
        return
    x = direction[0]
    y = direction[1]
    msg = Vector2(x=x, y=y)
    direction_pub.publish(msg)
    past_dir = direction


def pub_shovel(val):
    global past_shovel
    if val == past_shovel:
        return
    msg = to_trit_msg(val)
    shovel_pub.publish(msg)
    past_shovel = to_trit(val)


def pub_arm(val):
    global past_arm
    if val == past_arm:
        return
    msg = to_trit_msg(val)
    arm_pub.publish(msg)
    print(val)
    past_arm = to_trit(val)


def pub_camera(pitch, yaw):
    global past_camera
    camera = (pitch, yaw)
    if camera == past_camera:
        return
    msg = CameraPosition(yaw=yaw, pitch=pitch)
    camera_pub.publish(msg)
    past_camera = camera


def wiimote_handler():
    joystick = pygame.joystick.Joystick(wii_joy_index)
    joystick.init()

    joy_x = joystick.get_axis(0)
    joy_y = joystick.get_axis(1)

    joy_buttons = list()
    for i in range(0, 8):
        joy_button = joystick.get_button(i)
        joy_buttons.append(joy_button)

    pub_direction((joy_x, joy_y))
    pub_arm(joy_buttons[0] - joy_buttons[1])
    pub_shovel(joy_buttons[2] - joy_buttons[3])
    pitch = joy_buttons[4] - joy_buttons[5]
    yaw = joy_buttons[6] - joy_buttons[7]
    pub_camera(pitch, yaw)



def dualshock_handler():
    joystick = Joystick(wii_joy_index)
    joystick.init()

    joy_x1 = joystick.get_axis(0)
    joy_y1 = joystick.get_axis(1)
    joy_x2 = joystick.get_axis(2)
    joy_y2 = joystick.get_axis(3)
    axes = [joy_x1, joy_y1, joy_x2, joy_y2]
    for axis in axes:
        print(axis)


if __name__ == '__main__':
    setup()
    clock = pygame.time.Clock()
    while not rospy.is_shutdown():
        clock.tick(60)
        loop()
