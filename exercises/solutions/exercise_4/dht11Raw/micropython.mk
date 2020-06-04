DHT11RAW_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(DHT11RAW_MOD_DIR)/dht11Raw.c

# We can add our module folder to include paths if needed
# This is not actually needed in this example.
CFLAGS_USERMOD += -I$(DHT11RAW_MOD_DIR)
