#!/usr/bin/env python3

import sys

import adafruit_bme280
import board
import busio

print(sys.version)

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25


def get_humidity():
    return bme280.humidity


def get_temperature():
    return bme280.temperature


def get_pressure():
    return bme280.pressure


def get_altitude():
    return bme280.altitude