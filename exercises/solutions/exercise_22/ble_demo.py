from machine import Pin
from neopixel import NeoPixel
from machine import Timer
from time import sleep_ms
import bluetooth
from ble_advertising import advertising_payload

LED_PIN = 47
LED_INTENSITY = 0x1f

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# Nordic UART Service (NUS)
_NUS_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
_BLE_TX   = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_NOTIFY,
)
_BLE_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE,
)    
_NUS_SERVICE = (
    _NUS_UUID,
    (_BLE_TX, _BLE_RX),
)
    
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

class BLE_led():
    
    def __init__(self):
        self.state = False
        self.led = NeoPixel(Pin(LED_PIN),1)

    def off(self):
        # switch LED off
        self.led[0] = (0,0,0)
        self.led.write()
        self.state = False

    def on(self):
        # switch LED on (blue color)
        self.led[0] = (0,0,LED_INTENSITY)
        self.led.write()
        self.state = True

    def toggle(self):
        if self.state:
            self.off()
        else:
            self.on()
            
    def state(self):
        return self.state

class ESP32_BLE():
    def __init__(self,ble,name="ESP32BLE",_rxbuf=100):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.timer1 = Timer(0)
        self.led = BLE_led()
             
        self._ble = ble
        self._name = name
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_NUS_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, _rxbuf, True)        
        self._connections = set()
        self.ble_msg=""
        self._tmp_msg=bytearray()
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(name=self._name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)        

        # get the device address and print it
        addr = self._ble.config("mac")
        mac = addr[1]
        print("Device address: ",end="")
        for i in range(len(mac)-1):
            print("{:02x}:".format(mac[i]),end="")
        print("{:02x}".format(mac[len(mac)-1]))
        self.disconnected()
        self._advertise()

    def irq(self,handler):
        self._handler = handler

    def _irq(self,event,data):
        # Track connections so we can send notifications.
        # print("irq! event = {:d}".format(event))

        if event == _IRQ_CENTRAL_CONNECT :     # IRQ_CENTRAL_CONNECT
            conn_handle, _, _ = data      # A central has connected
            print("A central has connected")
            self._connections.add(conn_handle)
            self.connected()
            
        elif event == _IRQ_CENTRAL_DISCONNECT: # IRQ_CENTRAL_DISCONNECTED
                                               # a central has diconnected
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            print("The central has disconnected")
            self.disconnected()
            # Start advertising again to allow a new connection.
            self._advertise()
            
        elif event == _IRQ_GATTS_WRITE:        # IRQ_GATTS_WRITE
                                               # A central has written a message
            # print("write event")
            conn_handle, value_handle = data
            # if conn_handle in self._connections:
            #     print("connection found")
            # if value_handle == self._rx_handle:
            #     print("rx handle found")
            if conn_handle in self._connections and value_handle == self._rx_handle:
                # print("reading ble")
                self._tmp_msg +=self._ble.gatts_read(self._rx_handle).decode()
                # print("buffer after read: ",self._tmp_msg)
                if '\r' in self._tmp_msg or '\n' in self._tmp_msg:
                    self.ble_msg = self._tmp_msg.strip()
                    print("Message received from central: ",self.ble_msg)
                    self._tmp_msg = ""

    def any(self):
        if len(self.ble_msg):
            return True
        else:
            return False
        
    def write(self,data):
        for conn_handle in self._connections:
            print("Sending " + data)
            self._ble.gatts_notify(conn_handle, self._tx_handle, data + '\n')
        
    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()
        
    def _advertise(self, interval_us=500000):
        print("advertising " + self._name)
        print("Advertising data: ",self._payload)
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
        
    def connected(self):
        self.timer1.deinit()
        self.led.on()
        print("LED switched to steady on")
        
    def disconnected(self):
        self.timer1.init(period=100,mode=Timer.PERIODIC, callback = lambda src : self.led.toggle())
        
def demo():
    import time
    ble = bluetooth.BLE()
    led_ble = ESP32_BLE(ble)

    button = Pin(0,Pin.IN)

    def buttons_irq(pin):
        led_ble.led.toggle()
        led_ble.write('LED state will be toggled\r\n')
        print('LED state will be toggled')

    button.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)

    try:
        while True:
            # if led_ble.ble_msg != "":
            #     print("new message: ",led_ble.ble_msg)
            if led_ble.any():
                if led_ble.ble_msg == 'read_LED':
                    print("LED is on" if led_ble.led.state else "LED is off")
                    led_ble.write("LED is on\r\n" if led_ble.led.state else "LED is off\r\n")
                else:
                    print("Unknown command! Skipping")
                led_ble.ble_msg = ""
            sleep_ms(100)
        
    except KeyboardInterrupt:
        led_ble.close()

if __name__ == "__main__":
    demo()
