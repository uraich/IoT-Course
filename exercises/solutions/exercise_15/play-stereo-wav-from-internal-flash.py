# The MIT License (MIT)
# Copyright (c) 2020 Mike Teachman
# https://opensource.org/licenses/MIT

# Purpose:
# - read 16-bit audio samples from a stereo formatted WAV file 
#   stored in the internal MicroPython filesystem
# - write audio samples to an I2S amplifier or DAC module 
#
# Sample WAV file in wav_files folder:
#   "side-to-side-8k-16bits-stereo.wav"
#
# Hardware tested:
# - PCM5102 stereo DAC module
#
# The WAV file will play continuously until a keyboard interrupt is detected or
# the ESP32 is reset
  
from machine import I2S
from machine import Pin
import sys

#======= USER CONFIGURATION =======
WAV_FILE = '/wav/side-to-side-8k-16bits-stereo.wav'
WAV_SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.STEREO
SAMPLE_RATE_IN_HZ = 8000

# ======= I2S CONFIGURATION =======
SCK_PIN = 26
WS_PIN  = 22
SD_PIN  = 21
I2S_ID  = 1

sck_pin = Pin(SCK_PIN)   # bck
ws_pin  = Pin(WS_PIN)    # lrclk  
sd_pin  = Pin(SD_PIN)    # din
I2S_ID  = 1
BUFFER_LENGTH_IN_BYTES = 40000

audio_out = I2S(
    I2S_ID,
    sck=sck_pin,
    ws=ws_pin,
    sd=sd_pin,
    mode=I2S.TX,
    bits=WAV_SAMPLE_SIZE_IN_BITS,
    format=FORMAT,
    rate=SAMPLE_RATE_IN_HZ,
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

try:
    wav = open(WAV_FILE,'rb')
except:
    print("Could not open /wav/side-to-side-8k-16bits-stereo.wav for reading")
    sys.exit()
    
# advance to first byte of Data section in WAV file
pos = wav.seek(44) 

# allocate sample arrays
#   memoryview used to reduce heap allocation in while loop
wav_samples = bytearray(10000)
wav_samples_mv = memoryview(wav_samples)

# continuously read audio samples from the WAV file 
# and write them to an I2S DAC

print("==========  START PLAYBACK ==========")
try:
    while True:
        num_read = wav.readinto(wav_samples_mv)
        # end of WAV file?
        if num_read == 0:
            # end-of-file, advance to first byte of Data section
            pos = wav.seek(44)
        else:
            num_written = audio_out.write(wav_samples_mv[:num_read])

except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))

# cleanup    
wav.close()
audio_out.deinit()
print('Done')
