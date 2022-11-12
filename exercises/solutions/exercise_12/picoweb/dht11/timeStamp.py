#
# Creating the time stamp
#
import time

monthTable ={ 1: 'January',
              2: 'February',
              3: 'March',
              4: 'April',
              5: 'May',
              6: 'June',
              7: 'July',
              8: 'August',
              9: 'September',
              10: 'October',
              11: 'November',
              12: 'December'}

now = time.time()
tm=time.localtime(now)
print(tm)
timeStamp = '{0:02d} {1} {2:04d} {3:02d}:{4:02d}:{5:02d}'.format(tm[2],monthTable[tm[1]],tm[0],tm[3],tm[4],tm[5])
print(timeStamp)