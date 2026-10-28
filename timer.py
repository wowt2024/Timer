import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
from gpiozero import LED

# Hardware Pin Definitions
buzzer_pin = 17
button_pin = 27
touch_pin = 4

red_led = LED(19)
blue_led = LED(26)

# Setting up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Internal pull-up for button
GPIO.setup(buzzer_pin, GPIO.OUT)

# Initialize I2C LCD
lcd = CharLCD('PCF8574', 0x27, cols=20, rows=4, charmap='A00')

def sound_buzzer(duration=0.1):
	"""Helper function to beep the buzzer."""
	GPIO.output(buzzer_pin, GPIO.HIGH)
	time.sleep(duration)
	GPIO.output(buzzer_pin, GPIO.LOW)

try:
	lcd.clear()
	lcd.cursor_pos = (0,0)
	lcd.write_string("Pi 3 Stopwatch")
	elapsed_time = 0.0
	start_time = 0.0
	running = True

	while True:
	# 1. Check Touch Sensor (Starts or Pauses the timer)
		if GPIO.input(touch_pin) == GPIO.HIGH:
			running = not running # Toggle state
			sound_buzzer(0.1)
			if running:
				# Offest start_time so it resumes accurately from where it paused
				start_time = time.time() - elapsed_time
			time.sleep(0.3) # Debounce delay

	# 2. Check Tactile Button (Resets the timer to 0)
	if GPIO.input(button_pin) == GPIO.LOW:
		elapsed_time = 0
		running = False
		sound_buzzer(0.2)
		lcd.cursor_pos = (1, 0)
		lcd.write_string("Timer Reset!")
		time.sleep(0.3)  # Debounce Delay

	# 3. Update Timer if running
	if running:
		elapsed_time = time.time() - start_time

	# 4. Format and Display Time on Line 2
	mins = int(elapsed_time // 60)
	secs = int(elapsed_time % 60)
	hundredths = int((elapsed_time * 100) % 100)

	status = "RUNNING" if running else "PAUSED"

	# 5. Format and Display on LCD 
	lcd.cursor_pos = (1, 0)
	lcd.write_string(f"{mins:02d}:{secs:02d}.{hundredths:02d} [{status}]")

	# Short pause to refresh the CPU
	time.sleep(0.03)

except KeyboardInterrupt:
	lcd.clear()
	lcd.write_string("Stopwatch Exiting...")
	time.sleep(3)
	lcd.clear()
	GPIO.cleanup()
