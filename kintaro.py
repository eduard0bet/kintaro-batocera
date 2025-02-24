#!/usr/bin/python3
#                                      ▄▄= _╓_
#                                    ╓██▄▓██████▄_
#                                   j██████████████▄
#                                   ╫████████████▀"
#                                   ╫█████████╙
#                                 ,▄▓███████▓,
#                               ▄██████████████▄
#                              ª▀▀▀▀▀▀▀▀▀▀▀▀████H
#                         _,▄▄▓▓██████████▓▓████Ñ
#                     ,▄██████████████████████████▓▄_
#                  _▄█████████████████████████████████▄_
#                 ▄██████████████████████████████████████╓
#               ╓█████████████^╟██████████████████████████▓_
#              ╔█████████████  ▓████████████████████████████▄
#             ╔█████▀▀▀╙╙""`   ````""╙╙▀▀▀████████████╕'█████▄
#            ╓███,▄▄H                        └╙▀███████_▐█████╕
#            ██████▌  ▄▓▀▀▄╓          _╓▄▄▄▄╖_    ╙╙███▌ ██████_
#           ╫█████▌  ²╙  _ ╙▀       ▓▀╙"    '█H      _╙Ñ ▓█████▓
#          ▐██████      ▓██_ ,,        ▄█▌_  ``      ╟█▄|███████▒
#          ██████Ñ      `╙^_█╙╙▀▓▄    '███`          ╚███████████╕
#         ╟██████          `"    `                   [████████████
#        ╓██████▌     ▄▄▓█▓▀▀▀▀▀▀▓φ▄▄,_              [█████████████
#        ▓██████▌      ╟███▄╓,_____,,╠███▓▄▄▄        j██████████████
#       ║███████▌      '█████████████████▓           ▐███████████████╖
#      ╓█████████_      `████╙"]█▀╙"'╙██╜            ║█████████████████▄
#      ███████████_       ╙▓▄╓,╙`_,▄▓▀^              ╫█████████████```
#     ▓████████████_         '╙╙╙╙"                 _██████████████▌
#   _▓██████████████▄_     ª█      ,▄@            _▄████████████████H
#  »▓█████▀▀▀▀▀███████▌,    ╙▀▓▓▓▀▀╙`          _▄▓▀`╫████████▀╙▀▀▀▀██_
#              ╚█████▀╙╙▀▓▄,__           _,,▄▓▀▀"  ,██████▀"
# Copyright 2016 Kintaro Co.                                                                                                                                                     
# Copyright 2025 Eduardo Betancourt
# Kintaro Controller service script for batocera

import time
import os
import RPi.GPIO as GPIO
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='/tmp/kintaro.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SNES:
    def __init__(self):
        # GPIO pins
        self.led_pin = 7      # Pin 7 (BOARD) -> GPIO4
        self.fan_pin = 8      # Pin 8 (BOARD) -> GPIO14
        self.reset_pin = 3    # Pin 3 (BOARD) -> GPIO2
        self.power_pin = 5    # Pin 5 (BOARD) -> GPIO3
        self.check_pin = 10   # Pin 10 (BOARD) -> GPIO15

        # Variables
        self.fan_hysteresis = 20
        self.fan_starttemp = 60
        self.debounce_time = 0.1

        # Tracking for buttons
        self.prev_power_state = None
        self.prev_reset_state = None
        self.prev_check_state = None
        
        # Count button presses (for debugging)
        self.power_count = 0
        self.reset_count = 0

        # Path for temperature reading
        self.temp_command = 'cat /sys/class/thermal/thermal_zone0/temp'

        logging.info("Initializing Kintaro controller")
        
        # Ajustar permisos de gpiomem para permitir acceso
        try:
            os.system("chmod 666 /dev/gpiomem")
            logging.info("Changed permissions for /dev/gpiomem")
        except Exception as e:
            logging.error(f"Failed to change permissions: {e}")
        
        # Set up GPIO pins with error handling
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            
            # Setup outputs
            GPIO.setup(self.led_pin, GPIO.OUT)
            GPIO.setup(self.fan_pin, GPIO.OUT)
            
            # Setup inputs with pull-up/pull-down resistors
            GPIO.setup(self.power_pin, GPIO.IN)
            GPIO.setup(self.reset_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.check_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            logging.info("GPIO pins initialized successfully")
            
            # Read initial button states
            self.prev_power_state = GPIO.input(self.power_pin)
            self.prev_reset_state = GPIO.input(self.reset_pin)
            self.prev_check_state = GPIO.input(self.check_pin)
            
            logging.info(f"Initial button states - Power: {self.prev_power_state}, " +
                        f"Reset: {self.prev_reset_state}, Check: {self.prev_check_state}")
            
        except Exception as e:
            logging.error(f"GPIO initialization error: {e}")
            exit(1)
            
        # Initialize PWM for fan
        try:
            self.pwm = GPIO.PWM(self.fan_pin, 50)
            self.pwm.start(0)
            logging.info("PWM initialized")
        except Exception as e:
            logging.error(f"PWM initialization error: {e}")
            exit(1)

    def check_buttons(self):
        """Check all buttons for state changes"""
        self.check_power_button()
        self.check_reset_button()
        self.check_pcb_connection()

    def check_power_button(self):
        """Check if power button state has changed"""
        current_state = GPIO.input(self.power_pin)
        
        # Log every 10 seconds for debugging
        if self.power_count % 20 == 0:
            logging.debug(f"Power button state: {current_state}")
        self.power_count += 1
        
        # Check for state change
        if current_state != self.prev_power_state:
            logging.info(f"Power button changed: {self.prev_power_state} -> {current_state}")
            
            # If changed to HIGH (pressed) and PCB is connected
            if current_state == GPIO.HIGH and GPIO.input(self.check_pin) == GPIO.LOW:
                time.sleep(self.debounce_time)  # Debounce
                if GPIO.input(self.power_pin) == GPIO.HIGH:  # Still pressed
                    self.led(0)  # Turn off LED
                    logging.info('Power button pressed - shutting down')
                    try:
                        # Método específico de Batocera para apagar
                        GPIO.cleanup()  # Limpieza antes de apagar
                        os.system("batocera-es-swissknife --shutdown")
                        exit(0)  # Salir después de enviar el comando
                    except:
                        logging.error("Error during shutdown command")
            
            # Update previous state
            self.prev_power_state = current_state

    def check_reset_button(self):
        """Check if reset button state has changed"""
        current_state = GPIO.input(self.reset_pin)
        
        # Log every 10 seconds for debugging
        if self.reset_count % 20 == 0:
            logging.debug(f"Reset button state: {current_state}")
        self.reset_count += 1
        
        # Check for state change LOW means pressed (pull-up)
        if current_state != self.prev_reset_state:
            logging.info(f"Reset button changed: {self.prev_reset_state} -> {current_state}")
            
            # If changed to LOW (pressed)
            if current_state == GPIO.LOW:
                time.sleep(self.debounce_time)  # Debounce
                if GPIO.input(self.reset_pin) == GPIO.LOW:  # Still pressed
                    self.blink(3, 0.1)
                    logging.info('Reset button pressed - rebooting')
                    try:
                        # Método específico de Batocera para reiniciar
                        GPIO.cleanup()  # Limpieza antes de reiniciar
                        os.system("batocera-es-swissknife --reboot")
                        exit(0)  # Salir después de enviar el comando
                    except:
                        logging.error("Error during reboot command")
            
            # Update previous state
            self.prev_reset_state = current_state

    def check_pcb_connection(self):
        """Check if the PCB connection state has changed"""
        current_state = GPIO.input(self.check_pin)
        
        # Only log when state changes
        if current_state != self.prev_check_state:
            logging.info(f"PCB connection changed: {self.prev_check_state} -> {current_state}")
            
            # If changed to HIGH (disconnected)
            if current_state == GPIO.HIGH:
                logging.info("PCB disconnected - exiting")
                # Clean up and exit
                GPIO.cleanup()
                exit(0)
            
            # Update previous state
            self.prev_check_state = current_state

    def temp(self):  # Read temperature
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return float(f.read().strip()) / 1000.0
        except Exception as e:
            logging.error(f"Failed to read temperature: {e}")
            return 50.0  # Default fallback

    def pwm_fancontrol(self, hysteresis, starttemp, temp):
        # Calculate percentage based on temperature
        perc = 100.0 * ((temp - (starttemp - hysteresis)) /
                        (starttemp - (starttemp - hysteresis)))
        perc = min(max(perc, 0.0), 100.0)
        
        # Apply duty cycle to fan
        try:
            self.pwm.ChangeDutyCycle(float(perc))
            # Only log significant changes
            if perc % 10 < 0.5 or (perc > 0 and perc < 1):
                logging.debug(f"Fan duty cycle set to {perc:.1f}%")
        except Exception as e:
            logging.error(f"Failed to control fan: {e}")

    def led(self, status):  # Toggle the LED on or off
        try:
            if status == 0:  # The LED is inverted
                GPIO.output(self.led_pin, GPIO.LOW)
                logging.debug("LED turned off")
            if status == 1:
                GPIO.output(self.led_pin, GPIO.HIGH)
                logging.debug("LED turned on")
        except Exception as e:
            logging.error(f"Failed to control LED: {e}")

    def blink(self, amount, interval):  # Blink the LED
        for x in range(amount):
            self.led(1)
            time.sleep(interval)
            self.led(0)
            time.sleep(interval)

    def check_fan(self):
        temp_val = self.temp()
        # Log temperature less frequently to reduce log size
        if int(time.time()) % 30 == 0:  # Every 30 seconds
            logging.debug(f"Current temperature: {temp_val:.1f}°C")
        self.pwm_fancontrol(self.fan_hysteresis,
                            self.fan_starttemp, temp_val)

    def run(self):
        try:
            logging.info("Starting Kintaro controller loop")
            
            # Initial check for PCB
            if GPIO.input(self.check_pin) == GPIO.HIGH:
                logging.info("PCB not detected at startup - exiting")
                GPIO.cleanup()
                exit(1)
                
            # Initial check for power switch
            if GPIO.input(self.power_pin) == GPIO.HIGH:
                logging.info("Power switch in OFF position at startup - shutting down")
                os.system("batocera-es-swissknife --shutdown")  # Usando comando específico de Batocera
                GPIO.cleanup()
                exit(0)
                
            # Turn on LED at start
            self.led(1)
            
            # Main control loop
            while True:
                # Check all buttons
                self.check_buttons()
                
                # Check temperature and control fan
                self.check_fan()
                
                # Sleep to reduce CPU usage
                time.sleep(0.5)
        
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
        finally:
            GPIO.cleanup()
            logging.info("GPIO cleanup complete")

# Main program
if __name__ == "__main__":
    try:
        controller = SNES()
        controller.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        GPIO.cleanup()