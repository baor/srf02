'''
Created on Oct 2, 2010

@author: michael

http://www.robot-electronics.co.uk/htm/usb_i2c_tech.htm
http://www.robot-electronics.co.uk/htm/srf02techI2C.htm
'''

import serial
import time
import logging


#set up the serial connection
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
#logging.basicConfig(filename='srf02.log', level=logging.INFO, format='[%(asctime)s][%(funcName)s][%(lineno)d][%(levelname)s] %(message)s')
logging.basicConfig(filename='srf02.log', level=logging.INFO, format='[%(asctime)s] %(message)s')

def print_response(resp):
    resp_txt = ""
    for byte in resp:
        resp_txt += "{:02x} ".format(ord(byte))
    print "response: " + resp_txt

#while True:
for i in range(0, 100):
    #basic error handling, occasionally the device fails to respond. This keeps the 
    #loop running.
    try:
        '''
        send the 5 byte command to start a ranging ping.
        1st byte 0x55 is the start command for the USB-I2C module.
        2nd byte 0xE0 is the address of the SRF02 on the I2C bus.
        3rd byte 0x00 is the address register of the SRF02 that we are writing the command to.
        4th byte 0x01 is the number of bytes in the command we are about to send.
        5th byte 0x51 is the command to tell the SRF02 to initiate a range in cm.
        '''
        ser.write(chr(0x55)+chr(0xE0)+chr(0x00)+chr(0x01)+chr(0x51))

        time.sleep(.1)
        '''
        this 4byte command tells the SRF02 to send the result to the I2C bus for reading.
        1st byte 0x55 is the start command for the USB-I2C module.
        2nd byte 0xE1 is the SRF02s address plus one, this tells it that we are reading.
        3rd byte 0x02 is the register thats holds the data we want to start reading from.
        4th byte 0x02 is the number of bytes to read.
        In this case we want 2bytes, the range high byte and the range low byte.
        '''
        ser.write(chr(0x55)+chr(0xE1)+chr(0x02)+chr(0x02))

        #read 3 bytes. Why 3 when we only requested 2? The USB-I2C device returns a 
        #byte first to tell of success or fail
        s = ser.read(3)
        
        #clear the screen so we are not repeating up the screen
        #os.system('clear')

        '''
        first check for a successful read response, first byte will be 1 if successful.
        Then print the second byte which is the range high followed byte the 3rd which
        is range low. Combine to get the actual range, we do this because each register
        is one byte of 8 bits, this only allows numbers to go to 255, this would give
        255cm on the low byte. But suppose we are measuring a range of 280cm, the low
        register maxes out at 255. We put a 1 in the high byte register to represent
        256 and the low byte starts again and counts to 24. So we can simply combine
        the high and the low bye h*256+l to get the range so in the example 1*256+24=280
        '''
        print_response(s)
        if ord(s[0]) == 1:
            range_in_cm = ord(s[1]) * 256 + ord(s[2])
            logging.info('range in cm: %s' % range_in_cm)
            print "Status OK. high: %s, low: %s, range in cm: %s" % (ord(s[1]), ord(s[2]), range_in_cm)
        else:
            print 'Status ERR. Error reading device'
        
        #slow the loop down a bit to give our eyes a chance to read the response
        #raw_input("Press key to continue...")
        time.sleep(1)

        '''
        handle errors, the second "except" here takes all errors in it's stride and allows
        the loop to continue. I did this because every now and again the USB-I2C device
        fails to respond and breaks the loop. By having a blanket error handling rule you
        could no longer interrupt the loop with a keyboard interrupt so I had to add an
        "except KeyboardInterrupt" rule to allow this to break the loop.
        '''
    except KeyboardInterrupt:
        print ' Exiting...Keyboard interrupt'
        break
    
    except:
        print 'unexpected error'
