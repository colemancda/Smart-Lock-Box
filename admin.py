import time, sys, signal, atexit
import pyupm_zfm20 as upmZfm20
import mraa
import time
import os
# Instantiate a ZFM20 Fingerprint reader on UART 0
myFingerprintSensor = upmZfm20.ZFM20(0)


## Exit handlers ##
# This stops python from printing a stacktrace when you hit control-C
def SIGINTHandler(signum, frame):
	raise SystemExit

# This function lets you run code on exit,
# including functions from myFingerprintSensor
def exitHandler():
	print "Exiting"
	sys.exit(0)

# Register exit handlers
atexit.register(exitHandler)
signal.signal(signal.SIGINT, SIGINTHandler)


# make sure port is initialized properly.  57600 baud is the default.
if (not myFingerprintSensor.setupTty(upmZfm20.cvar.int_B57600)):
	print "Failed to setup tty port parameters"
	sys.exit(1)


# This example demonstrates registering a fingerprint on the zfm20
# module.  The procedure is as follows:
#
# 1. get an image, store it in characteristics buffer 1
# 2. get another image, store it in characteristics buffer 2
# 3. store the image, assuming the two fingerprints match

# first, we need to register our address and password

myFingerprintSensor.setPassword(upmZfm20.ZFM20_DEFAULT_PASSWORD)
myFingerprintSensor.setAddress(upmZfm20.ZFM20_DEFAULT_ADDRESS)

# now verify the password.  If this fails, any other commands
# will be ignored, so we just bail.
if (myFingerprintSensor.verifyPassword()):
	print "Password verified."
	os.system('espeak -a 200 -s 120 -v en-rp "Password verified"')
else:
	print "Password verification failed."
	os.system('espeak -a 200 -s 120 -v en-rp "Password verification failed"')
	sys.exit(1)


print " "

# get the first image
print "Place a finger on the sensor."
os.system('espeak -a 200 -s 120 -v en-rp "Place a finger on the sensor"')
while (myFingerprintSensor.generateImage() != upmZfm20.ZFM20.ERR_OK):
	pass

# in theory, we have an image
print "Image captured, converting..."

rv = myFingerprintSensor.image2Tz(1)

if (rv != upmZfm20.ZFM20.ERR_OK):
	print "Image conversion failed with error code %d" % rv
	sys.exit(1)

print "Image conversion succeeded, remove finger."
time.sleep(1)

while (myFingerprintSensor.generateImage() != upmZfm20.ZFM20.ERR_NO_FINGER):
	pass

print " "
print "Now place the same finger on the sensor."
os.system('espeak -a 200 -s 120 -v en-rp "Now place the same finger on the sensor"')

while (myFingerprintSensor.generateImage() == upmZfm20.ZFM20.ERR_NO_FINGER):
	pass

print "Image captured, converting..."

# save this one in slot 2
rv = myFingerprintSensor.image2Tz(2)
if (rv != upmZfm20.ZFM20.ERR_OK):
	print "Image conversion failed with error code %d" % rv
	sys.exit(1)

print "Image conversion succeeded, remove finger."
os.system('espeak -a 200 -s 120 -v en-rp "Remove finger"')
print " "

print "Storing fingerprint at id 1"

# create the model
rv = myFingerprintSensor.createModel()
if (rv != upmZfm20.ZFM20.ERR_OK):
	if (rv == upmZfm20.ZFM20.ERR_FP_ENROLLMISMATCH):
		print "Fingerprints did not match."
		os.system('espeak -a 200 -s 120 -v en-rp "Fingerprints did not match"')
	else:
		print "createModel failed with error code %d" % rv
	sys.exit(1)

# now store it, we hard code the id (second arg) to 1 here
rv = myFingerprintSensor.storeModel(1, 1)
if (rv != upmZfm20.ZFM20.ERR_OK):
	print "storeModel failed with error code %d" % rv
	sys.exit(1)

print " "
print "Fingerprint stored at id 1."