#
# read out the plantower pms5003 dust sensor
# U. Raich, March 2021
#
# it is connected to
# Rx: D2 GPIO 21
# Tx: D1 GPIO 22

from plantower import PlanTower
print("Starting PlanTower readout...")
plantower = PlanTower()
while True:
    if plantower.count == 0:
        print("Measuring for 1 min...")
    plantower.read_raw()
    plantower.decode()
    # plantower.print_results()
    plantower.sum()
    if plantower.count >59:
        plantower.print_avr_results()
        plantower.clear_sums()
