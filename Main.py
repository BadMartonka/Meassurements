import time
import Dht11
import RPi.GPIO as GPIO
import sys
import struct
import psycopg2

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


conn = psycopg2.connect(host="192.168.0.157",database="postgres", user="postgres", password="admin")
print("Connected...")
cursor = conn.cursor()


def main():

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    instance = Dht11.DHT11(pin = Temp_sensor)

    while True:

        #get DHT11 sensor value
        result = instance.read()

        if result.temperature != 0:
            #data = (result.temperature)
            cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('TEMPERATURE', %s, current_timestamp);", [result.temperature])
            cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('HUMIDITY', %s, current_timestamp);", [result.humidity])
            conn.commit()

        print"Temperature = ",result.temperature,"C"," Humidity = ",result.humidity,"%"
        time.sleep(10)

#Here begins the vibration sensor meassurement
def callback(channel):
    if GPIO.input(channel):
        print "EARTQUAKE Detected!"
        cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('EARTQUAKE', NULL, current_timestamp);")
        conn.commit()
    else:
        print "EARTQUAKE Detected!"
        cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('EARTQUAKE', NULL, current_timestamp);")
        conn.commit()

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)
#Here ends the vibration sensor meassurement

#Here begins the rain sensor meassurement
while True:
    if not no_rain.is_active:
        print "RAIN Detected!"
        cursor.execute("INSERT INTO public.\"MEASSUREMENT\"(\"MEASSUREMENT_TYPE\", \"MEASSUREMENT_DATA\", \"MEASSUREMENT_DATE\") VALUES ('RAIN', NULL, current_timestamp);")
        conn.commit()
        time.sleep(1)
#Here ends the rain sensor meassurement


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
