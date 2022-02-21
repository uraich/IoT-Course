# MPU6050 offset-finder, based on Jeff Rowberg's MPU6050_RAW
# 2016-10-19 by Robert R. Fenichel (bob@fenichel.net)

# I2C device class (I2Cdev) demonstration Arduino sketch for MPU6050 class
# 10/7/2011 by Jeff Rowberg <jeff@rowberg.net>
# Updates should (hopefully) always be available at https://github.com/jrowberg/i2cdevlib

# Changelog:
#      2022-02-08 - ported to MicroPython by U. Raich
#      2019-07-11 - added PID offset generation at begninning Generates first offsets 
#                 - in @ 6 seconds and completes with 4 more sets @ 10 seconds
#                 - then continues with origional 2016 calibration code.
#      2016-11-25 - added delays to reduce sampling rate to ~200 Hz
#                   added temporizing printing during long computations
#      2016-10-25 - requires inequality (Low < Target, High > Target) during expansion
#                   dynamic speed change when closing in
#      2016-10-22 - cosmetic changes
#      2016-10-19 - initial release of IMU_Zero
#      2013-05-08 - added multiple output formats
#                 - added seamless Fastwire support
#      2011-10-07 - initial release of MPU6050_RAW

# ============================================
'''
I2Cdev device library code is placed under the MIT license
Copyright (c) 2011 Jeff Rowberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

  If an MPU6050 
      * is an ideal member of its tribe, 
      * is properly warmed up, 
      * is at rest in a neutral position, 
      * is in a location where the pull of gravity is exactly 1g, and 
      * has been loaded with the best possible offsets, 
then it will report 0 for all accelerations and displacements, except for 
Z acceleration, for which it will report 16384 (that is, 2^14).  Your device 
probably won't do quite this well, but good offsets will all get the baseline 
outputs close to these target values.

  Put the MPU6050 on a flat and horizontal surface, and leave it operating for 
5-10 minutes so its temperature gets stabilized.

  Run this program.  A "----- done -----" line will indicate that it has done its best.
With the current accuracy-related constants (NFast = 1000, NSlow = 10000), it will take 
a few minutes to get there.

  Along the way, it will generate a dozen or so lines of output, showing that for each 
of the 6 desired offsets, it is 
      * first, trying to find two estimates, one too low and one too high, and
      * then, closing in until the bracket can't be made smaller.

  The line just above the "done" line will look something like
    [567,567] --> [-1,2]  [-2223,-2223] --> [0,1] [1131,1132] --> [16374,16404] [155,156] --> [-1,1]  [-25,-24] --> [0,3] [5,6] --> [0,4]
As will have been shown in interspersed header lines, the six groups making up this
line describe the optimum offsets for the X acceleration, Y acceleration, Z acceleration,
X gyro, Y gyro, and Z gyro, respectively.  In the sample shown just above, the trial showed
that +567 was the best offset for the X acceleration, -2223 was best for Y acceleration, 
and so on.

  The need for the delay between readings (usDelay) was brought to my attention by Nikolaus Doppelhammer.
===============================================
'''
import sys
from utime import sleep_ms, sleep_us 
from machine import Pin,I2C 
from MPU6050_const import *
from MPU6050 import MPU6050
from micropython import const

# class default I2C address is 0x68
# specific I2C addresses may be passed as a parameter here
# AD0 low = 0x68 (default for InvenSense evaluation board)
# AD0 high = 0x69

class MPU6050_Calibration:

    iAx = const(0)
    iAy = const(1)
    iAz = const(2)
    iGx = const(3)
    iGy = const(4)
    iGz = const(5)

    usDelay = const(3150)   # empirical, to hold sampling to 200 Hz
    NFast   = const(1000)   # the bigger, the better (but slower)
    NSlow   = const(10000)  # ..

    LinesBetweenHeaders = 5
    def __init__(self,debug=False):
        self.debug      = debug
        self.LowValue   = [None]*6
        self.HighValue  = [None]*6
        self.Smoothed   = [None]*6
        self.LowOffset  = [0]*6
        self.HighOffset = [0]*6
        self.Target     = [0]*6
        self.Target[self.iAx] = 16384 # 1 g on x axis
        if self.debug:
            print("Target values: ",self.Target)

    def setDebug(onOff):
        self.debug = onOff
        
    def ForceHeader(self) :
        self.LinesOut = 99
    
    def GetSmoothed(self) :
        Sums     = [0]*6
        # unsigned long Start = micros();
        for i in range(1,self.N+1) :
            # get sums
            RawValue = list(self.accelgyro.getMotion6())
            if not i % 500:
                print('.',end='')
            sleep_us(usDelay)
            for j in range(self.iAx,self.iGz+1):
                Sums[j] = Sums[j] + RawValue[j]

            # unsigned long usForN = micros() - Start;
            # print(" reading at ",end='')
            # print(1000000/((usForN+N/2)/N),end='')
            # print(" Hz")

        for i in range(self.iAx,self.iGz+1):
            self.Smoothed[i] = (Sums[i] + (self.N)/2) / self.N
        
        if self.debug:
            print("\nSmoothed: ax={:.2f}, ay={:.2f},az={:.2f},gx:{:.2f},gy:{:.2f},gz={:.2f}".format(self.Smoothed[0],
                                                                                                    self.Smoothed[1],
                                                                                                    self.Smoothed[2],
                                                                                                    self.Smoothed[3],
                                                                                                    self.Smoothed[4],
                                                                                                    self.Smoothed[5]))

    def Initialize(self) :

        # initialize device
        print("Initializing I2C devices...")
        self.accelgyro = MPU6050()
        # accelgyro = MPU6050(0x69); // <-- use for AD0 high

        # verify connection
        print("Testing device connections...")
        if self.accelgyro.testConnection():
            print("MPU6050 connection successful")
        else:
            print("MPU6050 connection failed")
            sys.exit(-1)
        
        print("PID tuning Each Dot = 100 readings");
        # A tidbit on how PID (PI actually) tuning works. 
        # When we change the offset in the MPU6050 we can get instant results. This allows us to use Proportional and 
        # integral of the PID to discover the ideal offsets. Integral is the key to discovering these offsets, Integral 
        # uses the error from set-point (set-point is zero), it takes a fraction of this error (error * ki) and adds it 
        # to the integral value. Each reading narrows the error down to the desired offset. The greater the error from 
        # set-point, the more we adjust the integral value. The proportional does its part by hiding the noise from the 
        # integral math. The Derivative is not used because of the noise and because the sensor is stationary. With the 
        # noise removed the integral value lands on a solid offset after just 600 readings. At the end of each set of 100 
        # readings, the integral value is used for the actual offsets and the last proportional reading is ignored due to 
        # the fact it reacts to any noise.

        self.accelgyro.CalibrateAccel(6)
        self.accelgyro.CalibrateGyro(6)
        print("\nat 600 Readings")
        self.accelgyro.PrintActiveOffsets()
        print()
        self.accelgyro.CalibrateAccel(1)
        self.accelgyro.CalibrateGyro(1)
        print("700 Total Readings")
        self.accelgyro.PrintActiveOffsets()
        print()
        self.accelgyro.CalibrateAccel(1)
        self.accelgyro.CalibrateGyro(1)
        print("800 Total Readings")
        self.accelgyro.PrintActiveOffsets()
        print()
        self.accelgyro.CalibrateAccel(1)
        self.accelgyro.CalibrateGyro(1)
        print("900 Total Readings")
        self.accelgyro.PrintActiveOffsets()
        print()
        self.accelgyro.CalibrateAccel(1)
        self.accelgyro.CalibrateGyro(1)
        print("1000 Total Readings")
        self.accelgyro.PrintActiveOffsets()

        print("\n\nAny of the above offsets will work nicely\n\nLets proof the PID tuning using another method:")


    def SetOffsets(self,TheOffsets):
        self.accelgyro.setXAccelOffset(TheOffsets [iAx])
        self.accelgyro.setYAccelOffset(TheOffsets [iAy])
        self.accelgyro.setZAccelOffset(TheOffsets [iAz])
        self.accelgyro.setXGyroOffset (TheOffsets [iGx])
        self.accelgyro.setYGyroOffset (TheOffsets [iGy])
        self.accelgyro.setZGyroOffset (TheOffsets [iGz])

    def ShowProgress(self) :
        if self.LinesOut >= self.LinesBetweenHeaders:
            # show header
            print("\n\tXAccel\t\t\tYAccel\t\t\tZAccel\t\t\tXGyro\t\t\tYGyro\t\t\tZGyro")
            LinesOut = 0;

        for i in range(iAx,iGz+1):
            print("[{:d},{:d}] --> [{:d},{:d}]\t".format(int(self.LowOffset[i]),
                                                        int(self.HighOffset[i]),
                                                        int(self.LowValue[i]),
                                                        int(self.HighValue[i])),end='')
            if i == iGz:
                print()
            else:
                print('\t',end='')

        LinesOut += 1


    def PullBracketsIn(self):
        # boolean AllBracketsNarrow;
        # boolean StillWorking;
        NewOffset = [None]*6
  
        print("\nclosing in:")
        AllBracketsNarrow = False
        self.ForceHeader()
        StillWorking = True
        while StillWorking :
            StillWorking = False
            if AllBracketsNarrow and self.N == self.NFast:
                self.SetAveraging(NSlow)
            else :
                AllBracketsNarrow = True # tentative
            for i in range(self.iAx, self.iGz+1):
                if self.HighOffset[i] <= self.LowOffset[i]+1 :
                    NewOffset[i] = self.LowOffset[i]
                else :
                    # binary search
                    StillWorking = True
                    NewOffset[i] = (self.LowOffset[i] + self.HighOffset[i]) // 2
                    if self.HighOffset[i] > self.LowOffset[i] + 10 :
                        AllBracketsNarrow = False

            self.SetOffsets(NewOffset)
            if self.debug:
                print("PullBracketsIn: Setting Offsets: ",NewOffset)
            self.GetSmoothed()
            for i in range(self.iAx,self.iGz+1) :
                # closing in
                if self.Smoothed[i] > self.Target[i] :
                    # use lower half
                    self.HighOffset[i] = NewOffset[i]
                    self.HighValue[i] = self.Smoothed[i]
                else :
                    # use upper half
                    self.LowOffset[i] = NewOffset[i]
                    self.LowValue[i] = self.Smoothed[i]
            self.ShowProgress()

    def PullBracketsOut(self) :
        Done = False
        NextLowOffset  = [None]*6
        NextHighOffset = [None]*6

        print("expanding:")
        self.ForceHeader()
 
        while not Done :
            Done = True
            if self.debug:
                print("PullBracketsOut: setting low offsets: ",self.LowOffset)
            self.SetOffsets(self.LowOffset)
            self.GetSmoothed()
            if self.debug:
                print("\nPullBracketsOut: Smoothed with LowOffsets",self.Smoothed) 
            for i in range(self.iAx,self.iGz+1) :
                # got low values
                self.LowValue[i] = self.Smoothed[i]
                if self.LowValue[i] >= self.Target[i] :
            
                    Done = False
                    NextLowOffset[i] = self.LowOffset[i] - 1000
                else :
                    NextLowOffset[i] = self.LowOffset[i]
                    
            if self.debug:
                print("PullBracketsOut: Setting high offsets: ",self.HighOffset) 
            self.SetOffsets(self.HighOffset)
            if self.debug:
                print("\nPullBracketsOut: Smoothed with HighOffsets",self.Smoothed) 
            self.GetSmoothed()
            for i in range(self.iAx,self.iGz+1):
                # got high values
                self.HighValue[i] = self.Smoothed[i]
                if self.HighValue[i] <= self.Target[i] :
                    Done = False;
                    NextHighOffset[i] = self.HighOffset[i] + 1000
                else :
                    NextHighOffset[i] = self.HighOffset[i]

            self.ShowProgress()
            for i in range(self.iAx,self.iGz+1) :
                self.LowOffset[i]  = NextLowOffset[i]   # had to wait until ShowProgress done
                self.HighOffset[i] = NextHighOffset[i]  # ..
            if self.debug:
                print("PullBracketsOut: new LowOffset: ",self.LowOffset)
                print("PullBracketsOut: new HighOffset: ",self.HighOffset)
                
    def SetAveraging(self,NewN):
        self.N = NewN;
        if self.debug:
            print("averaging {:d} readings each time".format(self.N))

# --------------- main ---------------- 
calib = MPU6050_Calibration()
calib.Initialize()
calib.SetAveraging(NFast)
calib.PullBracketsOut()
calib.PullBracketsIn()
   
print("-------------- done --------------");

 
