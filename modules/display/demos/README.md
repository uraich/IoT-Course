# Instructions to run the demo programs
To make demo_images and the demo_sprites work you must first transfer the raw
images to the images directory on the ESP32:

ampy put images
This will take quite some time (a few minutes) so, please be patient!
## Playing the Arkanoid game
In addition to the images you must load the game levels:

ampy put levels
The linear potentiometer must be connected:

pot    ESP32
GND <> GND
Vcc <> 3.3V
DTB <> A0 == GPIO 36

