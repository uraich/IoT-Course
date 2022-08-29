#!/opt/bin/lv_micropython

from circular_buffer import CircularBuffer
cb = CircularBuffer(6)

cb.write('1')
cb.write('2')
cb.write('3')
cb.write('4')
cb.write('5')
if cb.is_full():
    print('buffer is full')
else:
    print('buffer is not full')
    
if cb.available():
    print('buffer is not empty')
else:
    print('buffer is empty')

cb.write('6')

if cb.is_full():
    print('buffer is full')
else:
    print('buffer is not full')
        
print("read elements")
for i in range(5):
    print("element: %d: "%i,end=' ')
    print(cb.read())

cb.write('a')
cb.write('b')
cb.write('c')

for i in range(3):
    print("element: %d: "%i,end=' ')
    print(cb.read())

cb.write('d')
cb.write('e')
cb.write('f')

for i in range(3):
    print("element: %d: "%i,end=' ')
    print(cb.read())
