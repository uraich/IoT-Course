#include <stdio.h>

#include "py/runtime.h"
#include "py/mperrno.h"
#include "py/mphal.h"
#include "extmod/machine_pulse.h"
#include "drivers/dht/dht.h"

// Allow the open-drain-high call to be DHT specific for ports that need it
#ifndef mp_hal_pin_od_high_dht
#define mp_hal_pin_od_high_dht mp_hal_pin_od_high
#endif

STATIC mp_obj_t dht11Raw_dht11ReadRaw(mp_obj_t pin_in, mp_obj_t buf_in) {

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf_in, &bufinfo, MP_BUFFER_WRITE);
    mp_printf(&mp_plat_print, "buffer length: %d\n",bufinfo.len);
    mp_printf(&mp_plat_print, "buffer type: \'%c\'\n",bufinfo.typecode);
    if (bufinfo.typecode != 'I')
      mp_raise_ValueError(MP_ERROR_TEXT("Expecting unsigned integer array"));
    if (bufinfo.len != 32*4)
      mp_raise_ValueError(MP_ERROR_TEXT("Expecting array of length of 32"));
    /* fill the buffer */
    unsigned int *buf = bufinfo.buf;

    /* define gpio pin */
    mp_hal_pin_obj_t pin = mp_hal_get_pin_obj(pin_in);
    mp_printf(&mp_plat_print, "dht11 pin number: %d\n",pin);

    mp_hal_pin_open_drain(pin);
    
    /* issue start command */
    mp_hal_pin_od_high_dht(pin);
    mp_hal_delay_ms(250);
    mp_hal_pin_od_low(pin);
    mp_hal_delay_ms(18);

    /* enter time critical section */
    mp_uint_t irq_state = mp_hal_quiet_timing_enter();

    /* release the line so the device can respond */
    mp_hal_pin_od_high_dht(pin);
    mp_hal_delay_us_fast(10);

    /* wait for device to respond */
   
    mp_uint_t ticks = mp_hal_ticks_us();
    while (mp_hal_pin_read(pin) != 0) {
        if ((mp_uint_t)(mp_hal_ticks_us() - ticks) > 100) {
            goto timeout;
        }
    }
   
    /* time pulse, should be 80us */
    ticks = machine_time_pulse_us(pin, 1, 150);
    if ((mp_int_t)ticks < 0) {
        goto timeout;
    }

    /* read the data from the dht pin every 4 us and pack the result
       into the data buffer of 32 bit words
       The buffer has space for 32*32 = 1024 data bits
     */
       
    for (int i=0; i<32;i++) {
      *buf = 0;
      for (int j=0; j<32; j++) {
	*buf = *buf << 1 | mp_hal_pin_read(pin);
	mp_hal_delay_us_fast(4);
      }
      buf++;
    }

    mp_hal_quiet_timing_exit(irq_state);
    return mp_const_none;
  
timeout:
    mp_hal_quiet_timing_exit(irq_state);
    mp_raise_OSError(MP_ETIMEDOUT);

}

MP_DEFINE_CONST_FUN_OBJ_2(dht11Raw_dht11ReadRaw_obj, dht11Raw_dht11ReadRaw);
  
// Define all properties of the dht11Raw module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t dht11Raw_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_dht11Raw) },
    { MP_ROM_QSTR(MP_QSTR_dht11ReadRaw), MP_ROM_PTR(&dht11Raw_dht11ReadRaw_obj) },
};
STATIC MP_DEFINE_CONST_DICT(dht11Raw_module_globals, dht11Raw_module_globals_table);

// Define module object.
const mp_obj_module_t dht11Raw_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&dht11Raw_module_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_dht11Raw, dht11Raw_user_cmodule, MODULE_DHT11RAW_ENABLED);
