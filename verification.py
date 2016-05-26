import time, sys, signal, atexit
import mraa
import pyupm_zfm20 as upmZfm20
import mraa
import time
import os

led = mraa.Gpio(10)
led.dir(mraa.DIR_OUT)


led.write(0)

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

# how many valid stored templates (fingerprints) do we have?
print "Total stored templates: %d" % myFingerprintSensor.getNumTemplates()
print " "

# now spin waiting for a fingerprint to successfully image
print "Waiting for finger print..."

while (myFingerprintSensor.generateImage() == upmZfm20.ZFM20.ERR_NO_FINGER):
        pass

# in theory, we have an image
print "Image captured, converting..."

rv = myFingerprintSensor.image2Tz(1)
if (rv != upmZfm20.ZFM20.ERR_OK):
        print "Image conversion failed with error code %d" % rv
        sys.exit(1)

print "Image conversion succeeded."
while True:
        led.write(1)
		os.system('espeak -a 200 -s 120 -v en-rp " The door is now open"')
		time.sleep(1)
		os.system('espeak -a 200 -s 120 -v en-rp "Door is closing in 7 seconds"')
        time.sleep(7)
        led.write(0)
		os.system('espeak -a 200 -s 120 -v en-rp "Door closed"')
        break
print "Searching database..."

myid = upmZfm20.uint16Array(0)
myid.__setitem__(0, 0)
myscore = upmZfm20.uint16Array(0)
myscore.__setitem__(0, 0)

# we search for a print matching slot 1, where we stored our last
# converted fingerprint
rv = myFingerprintSensor.search(1, myid, myscore)
if (rv != upmZfm20.ZFM20.ERR_OK):
        if (rv == upmZfm20.ZFM20.ERR_FP_NOTFOUND):
                print "Finger Print not found"
				os.system('espeak -a 200 -s 120 -v en-rp "Finger Print not found"')
                sys.exit(0)
        else:
                print "Search failed with error code %d" % rv
                sys.exit(1)

print "Fingerprint found!"
os.system('espeak -a 200 -s 120 -v en-rp "Fingerprint found"')
print "ID: %d, Score: %d" % (myid.__getitem__(0), myscore.__getitem__(0))