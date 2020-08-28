from micropyGPS import MicropyGPS
import machine
import time
u2=machine.UART(2, baudrate=9600, rx=21, tx=22)

my_gps = MicropyGPS(local_offset=2)          # CET summer time
my_gps.start_logging("gps.log")

while True:
    try:
        line = u2.readline().decode('utf8')
        if line[0] != '$':
            continue
        sentence = line.rstrip()
        #phrase = sentence.split(",")
        #print(phrase[0][1:])
        #print(sentence)
        for x in sentence:
            my_gps.update(x)
            
        if my_gps.valid:
            print("latitude:",my_gps.latitude_string())
            print("longitude: ",my_gps.longitude_string())
            print("altitude: ",my_gps.altitude)
            print("speed: ",my_gps.speed_string())
            print("date: ",my_gps.date_string('long'))
            timeStamp=my_gps.timestamp
            print("time: {:d}:{:d}:{:d} CET".format(timeStamp[0],timeStamp[1],int(timeStamp[2])))
            print("satellites in view: ",my_gps.satellites_in_view)
            print("Clean sentences: ", my_gps.clean_sentences)
            print("Parsed sentences: ",my_gps.parsed_sentences)
            print("crc errors: ", my_gps.crc_fails)
            print("\n")
        else:
            print("Invalid sentence")

    except:        
        pass
    time.sleep(2)
