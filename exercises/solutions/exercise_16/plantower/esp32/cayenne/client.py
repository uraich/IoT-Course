from umqtt.simple import MQTTClient
import network
import time

from wifi_connect import *
from cayenne import __version__
import ulogging as logging
import sys

# LOG
LOG_NAME = "CayenneMQTTClient"

# Data types
TYPE_BAROMETRIC_PRESSURE = "bp" # Barometric pressure
TYPE_BATTERY = "batt" # Battery
TYPE_LUMINOSITY = "lum" # Luminosity
TYPE_PROXIMITY = "prox" # Proximity
TYPE_RELATIVE_HUMIDITY = "rel_hum" # Relative Humidity
TYPE_TEMPERATURE = "temp" # Temperature
TYPE_VOLTAGE = "voltage" # Voltage
TYPE_DIGITAL_SENSOR = "digital_sensor" # digital sensor
TYPE_COUNTER = "counter" # counter

# Unit types
UNIT_UNDEFINED = "null"
UNIT_PASCAL = "pa" # Pascal
UNIT_HECTOPASCAL = "hpa" # Hectopascal
UNIT_PERCENT = "p" # % (0 to 100)
UNIT_RATIO = "r" # Ratio
UNIT_VOLTS = "v" # Volts
UNIT_LUX = "lux" # Lux
UNIT_CENTIMETER = "cm" # Centimeter
UNIT_METER = "m" # Meter
UNIT_DIGITAL = "d" # Digital (0/1)
UNIT_FAHRENHEIT = "f" # Fahrenheit
UNIT_CELSIUS = "c" # Celsius
UNIT_KELVIN = "k" # Kelvin
UNIT_MILLIVOLTS = "mv" # Millivolts

# Topics
COMMAND_TOPIC = "cmd"
DATA_TOPIC = "data"
RESPONSE_TOPIC = "response"

class CayenneMessage:
    """ This is a class that describes an incoming Cayenne message. It is
    passed to the on_message callback as the message parameter.

    Members:

    client_id : String. Client ID that the message was published on.
    topic : String. Topic that the message was published on.
    channel : Int. Channel that the message was published on.
    msg_id : String. The message ID.
    value : String. The message value.
    """
    def __init__(self, topic,payload):
        topic_tokens = topic.decode().split('/')
        self.client_id = topic_tokens[3]
        self.topic = topic_tokens[4]
        self.channel = int(topic_tokens[5])
        payload_tokens = payload.decode().split(',')
        self.msg_id = payload_tokens[0]
        self.value = payload_tokens[1]

    def __repr__(self):
        return str(self.__dict__)
    
class CayenneMQTTClient:
    """Cayenne MQTT Client class.

    This is the main client class for connecting to Cayenne and sending and receiving data.

    Standard usage:
    * Set on_message callback, if you are receiving data.
    * Connect to Cayenne using the begin() function.
    * Call loop() at intervals (or loop_forever() once) to perform message processing.
    * Send data to Cayenne using write functions: virtualWrite(), celsiusWrite(), etc.
    * Receive and process data from Cayenne in the on_message callback.

    The on_message callback can be used by creating a function and assigning it to CayenneMQTTClient.on_message member.
    The callback function should have the following signature: on_message(message)
    The message variable passed to the callback is an instance of the CayenneMessage class.
    """
    def __init__(self):
            
        self.client = None
        self.rootTopic = ""
        self.connected = False
        self.on_message = None
        
    """Initializes the client and connects to Cayenne.
    ssid     is WiFi ssid
    wifiPassword
    username is the Cayenne username.
    password is the Cayenne password.    
    clientID is the Cayennne client ID for the device.
    hostname is the MQTT broker hostname.
    port is the MQTT broker port. Use port 8883 for secure connections.
    logname is the name of the users log if they want the client to log to their logging setup.
    loglevel is the logging level that will be applied to logs.
    """

    def begin(self, username, password, clientid,
              hostname='mqtt.mydevices.com', port=1883,
              logname=LOG_NAME, loglevel=logging.WARNING):
        self.rootTopic = "v1/%s/things/%s" % (username, clientid)
        print("root topic: %s"%self.rootTopic);
        global wlan
        wlan=network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.disconnect()
        
        # try to connect to wlan
        connect()

        print("Connecting to %s"%hostname)        

        self.client = MQTTClient(clientid, hostname,0,username,password)
        self.client.connect()
        self.connected=True
        
        self.log = logging.getLogger(logname)
#        if logname == LOG_NAME:
#            logging.basicConfig(stream=sys.stdout, format='%(message)s', level=loglevel)
        self.log.info("Connecting to %s:%s"%(hostname, port))
        
        # subscribe to the cmd topic
        command_topic = self.getCommandTopic()
        self.client.set_callback(self.client_on_message)
        self.log.info("SUB %s"%command_topic)
        self.client.subscribe(command_topic)

    def client_on_message(self,topic,payload):
        # The callback for when a PUBLISH message is received from the server.
        self.log.info("RCV %s %s"%(topic, payload))
        self.message=CayenneMessage(topic,payload)
        # If there was no error, we send the new channel state, which should be the command value we received.
        self.virtualWrite(self.message.channel, self.message.value)
        # Send a response showing we received the message, along with any error from processing it.
        self.responseWrite(self.message.msg_id, None)
        if self.on_message:
            print("callback with %s %s"%(topic,payload))
            self.msg=(topic,payload)
            self.on_message(self.msg)
        else:
            print("No callback defined")              
        
    def getDataTopic(self, channel):
        """Get the data topic string.

        channel is the channel to send data to.
        """
        return "%s/%s/%s" % (self.rootTopic, DATA_TOPIC, channel)

    def getCommandTopic(self):
        """Get the command topic string."""
        return "%s/%s/+" % (self.rootTopic, COMMAND_TOPIC)

    def getResponseTopic(self):
        """Get the response topic string."""
        return "%s/%s" % (self.rootTopic, RESPONSE_TOPIC)

    def virtualWrite(self, channel, value, dataType="", dataUnit=""):
        """Send data to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        dataType is the type of data.
        dataUnit is the unit of the data.
        """
        if (self.connected):
            topic = self.getDataTopic(channel)
            if dataType:
                payload = "%s,%s=%s" % (dataType, dataUnit, value)
            else:
                payload = value
            self.mqttPublish(topic, payload)

    def responseWrite(self, msg_id, error_message):
        """Send a command response to Cayenne.

        This should be sent when a command message has been received.
        msg_id is the ID of the message received.
        error_message is the error message to send. This should be set to None if there is no error.
        """
        if (self.connected):
            topic = self.getResponseTopic()
            if error_message:
                payload = "error,%s=%s" % (msg_id, error_message)
            else:
                payload = "ok,%s" % (msg_id)
            self.mqttPublish(topic, payload)

    def counterWrite(self, channel, value):
        """Send a Counter value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_COUNTER, UNIT_UNDEFINED)
        
    def celsiusWrite(self, channel, value):
        """Send a Celsius value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_TEMPERATURE, UNIT_CELSIUS)
        
    def fahrenheitWrite(self, channel, value):
        """Send a Fahrenheit value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_TEMPERATURE, UNIT_FAHRENHEIT)

    def kelvinWrite(self, channel, value):
        """Send a kelvin value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_COUNTER, UNIT_KELVIN)
        
    def humidityWrite(self, channel, value):
        """Send a relative humidtys value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_RELATIVE_HUMIDITY, UNIT_PERCENT)
        
    def luxWrite(self, channel, value):
        """Send a lux value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_LUMINOSITY, UNIT_LUX)

    def pascalWrite(self, channel, value):
        """Send a pascal value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_BAROMETRIC_PRESSURE, UNIT_PASCAL)

    def hectoPascalWrite(self, channel, value):
        """Send a hectopascal value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        
        self.virtualWrite(channel, value, TYPE_BAROMETRIC_PRESSURE, UNIT_HECTOPASCAL)
        
    def voltageWrite(self, channel, value):
        """Send a voltage value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_VOLTAGE, UNIT_MILLIVOLTS)
        
    def digitalWrite(self, channel, value):
        """Send a voltage value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_DIGITAL_SENSOR, UNIT_DIGITAL)

    def mqttPublish(self, topic, payload):
        """Publish a payload to a topic

        topic is the topic string.
        payload is the payload data.
        """
        self.log.info("PUB %s %s" % (topic, payload))
        self.client.publish(topic, payload)
        
    def getClient(self):
        return self.client

    def loop(self):
        """Process Cayenne messages.

        This should be called regularly to ensure Cayenne messages are sent and received.
        To be implemented later
        """
        self.client.check_msg()
        return;

    def loop_forever(self):
        """Process Cayenne messages in a blocking loop that runs forever."""
        while True:
            self.client.wait_msg()
