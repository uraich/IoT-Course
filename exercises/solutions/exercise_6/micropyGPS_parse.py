from micropyGPS import MicropyGPS
import machine
import time
u2=machine.UART(2, baudrate=115200, rx=21, tx=22, timeout=10000)

my_gps = MicropyGPS(local_offset=2)          # CET summer time
#my_gps.start_logging("gps.log")
sentence_count = 0
valid_sentences = 0
while valid_sentences < 50:
    sentence_count +=1
    try:
        #print("count: ",sentenceCount)
        line = u2.readline().decode('utf8')
        if line[0] != '$':
            continue
        if not '*' in line:
            continue
        sentence = line.rstrip()
        phrase = sentence.split(",")
        sentenceType=phrase[0][1:]
        #print(sentenceType)
        for x in sentence:
            my_gps.update(x)
            
        if sentenceType == 'GPGSA':
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print('Sentence CRC Value:', hex(my_gps.crc_xor))
            print('Satellites Used', my_gps.satellites_used)
            print('Fix Type Code:', my_gps.fix_type)
            print('Horizontal Dilution of Precision:', my_gps.hdop)
            print('Vertical Dilution of Precision:', my_gps.vdop)
            print('Position Dilution of Precision:', my_gps.pdop)
            print('')
            
        elif sentenceType == 'GPRMC':
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print("Sentence CRC value: ",hex(my_gps.crc_xor))
            print('Longitude:', my_gps.longitude)
            print('Latitude', my_gps.latitude)
            print('Timestamp:', my_gps.timestamp)
            print('Speed:', my_gps.speed)
            print('Date Stamp:', my_gps.date)
            print('Course', my_gps.course)
            print('Data is Valid:', my_gps.valid)
            print('Compass Direction:', my_gps.compass_direction())
            print('')
            
        elif sentenceType == 'GPVTG':
            for x in sentence:
                my_gps.update(x)
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print("Sentence CRC value: ",hex(my_gps.crc_xor))
            print('Speed:', my_gps.speed)
            print('Course', my_gps.course)
            print('Compass Direction:', my_gps.compass_direction())
            print('Data is Valid:', my_gps._valid) 
            print('')
            
        elif sentenceType == 'GPGGA':
            for x in sentence:
                my_gps.update(x)
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print("Sentence CRC value: ",hex(my_gps.crc_xor))
            print('Longitude', my_gps.longitude)
            print('Latitude', my_gps.latitude)
            print('Timestamp:', my_gps.timestamp)
            print('Fix Status:', my_gps.fix_stat)
            print('Altitude:', my_gps.altitude)
            print('Height Above Geoid:', my_gps.geoid_height)
            print('Horizontal Dilution of Precision:', my_gps.hdop)
            print('Satellites in Use by Receiver:', my_gps.satellites_in_use)
            print('Data is Valid:', my_gps._valid)           
            print('')

        elif sentenceType == 'GPSGA':
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print('Sentence CRC Value:', hex(my_gps.crc_xor))
            print('Satellites Used', my_gps.satellites_used)
            print('Fix Type Code:', my_gps.fix_type)
            print('Horizontal Dilution of Precision:', my_gps.hdop)
            print('Vertical Dilution of Precision:', my_gps.vdop)
            print('Position Dilution of Precision:', my_gps.pdop)
            print('Data is Valid:', my_gps._valid)
            print('')
            
        elif sentenceType == 'GPGSV':
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print('Sentence CRC Value:', hex(my_gps.crc_xor))
            print('SV Sentences Parsed', my_gps.last_sv_sentence)
            print('SV Sentences in Total', my_gps.total_sv_sentences)
            print('# of Satellites in View:', my_gps.satellites_in_view)
            data_valid = my_gps.satellite_data_updated()
            print('Is Satellite Data Valid?:', data_valid)
            if data_valid:
                print('Complete Satellite Data:', my_gps.satellite_data)
                print('Complete Satellites Visible:', my_gps.satellites_visible())
            else:
                print('Current Satellite Data:', my_gps.satellite_data)
                print('Current Satellites Visible:', my_gps.satellites_visible())
                print("visible satellites:",my_gps.satellites_visible())
            print('')
                
        elif sentenceType == 'GPGLL':
            print("--------------------------------------------------")
            print('Parsed a', sentenceType, 'Sentence')
            print("--------------------------------------------------")
            print('Parsed Strings', my_gps.gps_segments)
            print('Sentence CRC Value:', hex(my_gps.crc_xor))
            print('Longitude:', my_gps.longitude)
            print('Latitude', my_gps.latitude)
            print('Timestamp:', my_gps.timestamp)
            print('Data is Valid:', my_gps.valid)
            print('')
            
        else:
            print("Sentence ",sentence," not known")
            print('')
        if my_gps.valid:
            valid_sentences += 1
    except:        
        pass
    #time.sleep(1)
    
print("Pretty Print Examples:")
print('Latitude (ddm):', my_gps.latitude_string())
print('Longitude (ddm):', my_gps.longitude_string())
my_gps.coord_format = 'dms'
print('Latitude (dds):', my_gps.latitude_string())
print('Longitude (dds):', my_gps.longitude_string())
my_gps.coord_format = 'dd'
print('Latitude (dd):', my_gps.latitude_string())
print('Longitude (dd):', my_gps.longitude_string())

print('Speed:', my_gps.speed_string('kph'), 'or',
      my_gps.speed_string('mph'), 'or',
      my_gps.speed_string('knot'))
print('Date (Long Format):', my_gps.date_string('long'))
print('Date (Short D/M/Y Format):', my_gps.date_string('s_dmy'))
print('Date (Short M/D/Y Format):', my_gps.date_string('s_mdy'))
print('Time: {:02d}:{:02d}:{:02d} CET summer time'.format(my_gps.timestamp[0],my_gps.timestamp[1],int(my_gps.timestamp[2])))
print()

print('### Final Results ###')
print('Sentences Attempted:', sentence_count)
print('Sentences Found:', my_gps.clean_sentences)
print('Sentences Parsed:', my_gps.parsed_sentences)
print('CRC_Fails:', my_gps.crc_fails)
