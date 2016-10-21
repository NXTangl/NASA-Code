#!/usr/bin/python3

# I gotta ask...why tabs? Python standard is 4 spaces indent.



import socket
import RPi.GPIO as GPIO
PORT=9500
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)
s.setsockopt(socket.IPPROTO_TCP , socket.TCP_NODELAY , 1 )
conn, addr = s.accept()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(05, GPIO.OUT)
GPIO.setup(06, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

#this pwm setup might change to start button initializtion
Drive = GPIO.PWM(05, 50)        
Steer = GPIO.PWM(06, 50)
Auger = GPIO.PWM(13, 50)
Slide = GPIO.PWM(19, 50)
Tilt = GPIO.PWM(26, 50)
Convey = GPIO.PWM(21,50)

# initialize PWM drivers.
# PWM 0%-100% duty cycle is interpreted
# as full reverse to full forward.
# Thus, 50% = stopped.
Drive.start(50)
Steer.start(50)
Auger.start(50)
Slide.start(50)
Tilt.start(50)

# FIXME: Is Convey supposed to be initialized to 0?
Convey.start(0)

# These count the number of toggle commands.
# It's a rather silly way to do things, toggle commands
# are easy to implement client-side.
augerCount = 1
tiltCount = 1
conveyorCount = 1


#main loop.
while True:
	# Grab the packet.
	info = conn.recv(6).decode()
	
	# This is a value selection statement.
	# Or it would be, if python had one.
	
	if info[:2] == 'DR': # Drive motor change command.
		pwm = float(info[2:])
		Drive.ChangeDutyCycle(pwm)
	if info[:2] == 'ST': # Steering motor change command.
		pwm = float(info[2:])
		Steer.ChangeDutyCycle(pwm)
	if info[:2] == 'AU': # Augur motor change command.
		# This is a really silly way of doing it! Not to mention it causes problems if
		# the socket ever fails and the laptop and robot get out of sync.
		pwm = float(info[2:])
		augerCount += 1
		if augerCount % 2 == 0: # Update auger every first 'AU' command.
			Auger.ChangeDutyCycle(pwm)
		else: # Stop auger every second 'AU' command.
			Auger.ChangeDutyCycle(50)				
	if info[:2] == 'SL': # Slide motor change command.
		pwm = float(info[2:])
		Slide.ChangeDutyCycle(pwm)
		
	if info[:2] == 'TI': # Tilt motor change command.
		tiltCount += 1
		pwm = float(info[2:])
		if tiltCount % 2 == 0: # Update every first message.
			Tilt.ChangeDutyCycle(pwm)
		else: # Stop every second message.
			Tilt.ChangeDutyCycle(50)
			
			
	if info[:2] == 'CO':
		conveyorCount += 1
		if conveyorCount %2 == 1: # Set to forward@80% every SECOND message.
			Convey.ChangeDutyCycle(90)
		else: # set to neutral every FIRST message.
			Convey.ChangeDutyCycle(50)
s.close() # The loop never actually ends normally (no break), so this close does nothing.
exit(0) # Ditto this exit.
