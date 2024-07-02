import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set ultrasonic sensor pins
trigger_pin = 23
echo_pin = 24

# Set LED pin
led_pin = 2
GPIO.setup(led_pin, GPIO.OUT)

# Set GPIO direction for ultrasonic sensor (IN or OUT)
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)
0
def measure_distance():
    # Send a pulse to trigger the sensor
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    # Measure the time for the echo signal
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()

    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start

    # Speed of sound in air is approximately 343m/s
    # Distance = time * speed of sound / 2 (since the sound travels back and forth)
    distance = pulse_duration * 34300 / 2

    return distance

try:
    while True:
        dist = measure_distance()
        print(f"Distance: {dist} cm")

        # Check distance threshold and blink LED
        if dist < 50:
            GPIO.output(led_pin, GPIO.HIGH)  # Turn LED on
            time.sleep(0.5)  # Wait for 0.5 seconds
            GPIO.output(led_pin, GPIO.LOW)  # Turn LED off
            time.sleep(0.5)  # Wait for 0.5 seconds

            if dist < 100:
            GPIO.output(led_pin, GPIO.HIGH)  # Turn LED on
            time.sleep(1)  # Wait for 0.5 seconds
            GPIO.output(led_pin, GPIO.LOW)  # Turn LED off
            time.sleep(1)  # Wait for 0.5 seconds
        else:
            GPIO.output(led_pin, GPIO.LOW)  # Turn LED off

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on keyboard interrupt
