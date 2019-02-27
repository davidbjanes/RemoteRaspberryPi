
import time
import RPi.GPIO as GPIO

delay_period = 0.01

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18,100)
pwm.start(5)


def lower_awr():
  global pwm
  
  print('Going Down...')
  
  for angle in range(150, 5, -1):
    duty = float(angle) / 10.0 + 2.5
    pwm.ChangeDutyCycle(duty)
    time.sleep(delay_period)
  
  pwm.stop()

def raise_awr():
  global pwm
  
  print('Going Up...')
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(18, GPIO.OUT)
  pwm = GPIO.PWM(18,100)
  pwm.start(5)
  
  for angle in range(5, 150, 1):
    duty = float(angle) / 10.0 + 2.5
    pwm.ChangeDutyCycle(duty)
    time.sleep(delay_period)

def exit_awr():
  GPIO.cleanup()

if __name__ == "__main__":
  raise_awr()
  lower_awr()
  exit_awr()
  