import time
import DHT11
import RPi.GPIO as GPIO
import sys
import struct
import psycopg2

from Adafruit_BMP085 import BMP085
from gpiozero import Buzzer, InputDevice

#temperature sensor setup
Temp_sensor=14
#temperature sensor setup

#vibration sensor setup
channel = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
#vibration sensor setup

#rain sensor setup
no_rain = InputDevice(27)
#rain sensor setup

bmp = BMP085(0x77)

conn = psycopg2.connect(host="192.168.0.157",database="postgres", user="postgres", password="admin")
print("Connected...")
cursor = conn.cursor()
cursor.execute("INSERT INTO meassurement.\"MEASSUREMENTS_EVENT_LOG\"(\"LOGGED_EVENT\", \"CRD\", \"CRU\") VALUES ('Connection started...', current_timestamp, 'Admin');")
conn.commit()

def main():

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    instance = DHT11.DHT11(pin = Temp_sensor)

    while True:

        # #Here begins the rain sensor meassurement
        if not no_rain.is_active:
            print "RAIN Detected!"
        cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('RAIN', NULL, current_timestamp);")
        conn.commit()
        time.sleep(1)
        # #Here ends the rain sensor meassurement


        #Here begins the vibration sensor meassurement
        if GPIO.input(channel):
            print "EARTQUAKE detected!"
            cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('EARTQUAKE', NULL, current_timestamp);")
            conn.commit()
        else:
            print "EARTQUAKE not detected!"
            # cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('EARTQUAKE', NULL, current_timestamp);")
            # conn.commit()
            # GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
            # GPIO.add_event_callback(channel, callback)
        #Here ends the vibration sensor meassurement

        #get DHT11 sensor value
        result = instance.read()

        #get BMP085 data
        temp = bmp.readTemperature()
        pressure = bmp.readPressure()
        altitude = bmp.readAltitude()

        if result.temperature != 0:
            #data = (result.temperature)
            cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('TEMPERATURE', %s, current_timestamp);", [result.temperature])
            cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('HUMIDITY', %s, current_timestamp);", [result.humidity])
            conn.commit()

        print"Temperature = ",result.temperature,"C"," Humidity = ",result.humidity,"%"

        print "Temperature: %.2f C" % temp
        print "Pressure:    %.2f hPa" % (pressure / 100.0)
        print "Altitude:    %.2f" % altitude
        time.sleep(10)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        cursor.execute("INSERT INTO meassurement.\"MEASSUREMENTS_EVENT_LOG\"(\"LOGGED_EVENT\", \"CRD\", \"CRU\") VALUES ('Connection ended...', current_timestamp, 'Admin');")
        conn.commit()
        pass
