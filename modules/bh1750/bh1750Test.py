#
# Tries the different functions of the BHT1750 driver
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# U. Raich, May 2020
# This program is released under GPL

bh1750 = BH1750()
print(bh1750.isPresent())
while True:
    print("")
    print("One Time High Resolution:     ",bh1750.measureOneTimeHighRes())
    print("One Time High Resolution 2:   ",bh1750.measureOneTimeHighRes2())
    print("One Time High Resolution:     ",bh1750.measureOneTimeLowRes())
    print("Continuous High Resolution:   ",bh1750.measureContTimeHighRes())
    print("Continuous High Resolution 2: ",bh1750.measureContTimeHighRes2())
    print("Continuous Low Resolution:    ",bh1750.measureContTimeLowRes())
    time.sleep(2)
