#! usr/bin/python
# PostObsPIR.py
# an attempt at mashing up existing scripts (oh boy!)
# and cleaning them up while we're at it
# march 5 2014 - KA


import time, datetime, requests, json, RPi.GPIO as GPIO
ID = " RPi 1 "

class data:

    def __init__(self,ID):
        self.ID = ID


    def __str__(self):
        return '{' + str(self.ID) + ' , ' + str(self.v) + ' , ' + str(self.t) +'}'

    def rootURI(self):
        return 'http://demo.student.geocens.ca:8080/SensorThings_V1.0/'

    def initRequest(self):
        url = self.rootURI() + 'Things'
        payload = {'Description': 'This is the real TurboCat (Raspberry Pi)',
            'Datastreams':
                [{'Description': 'This is a datastream for measuring people traffic'},
                    {'Description': 'This is a second datastream'}]}
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        ## ERROR CHECKING?! status code
        thing_location = r.headers['location']
        self.thing_location = thing_location
        
        url3 = self.rootURI() + 'Sensors'
        payload2 = {'Metadata': 'This is a PIR sensor'}
        rsensor = requests.post(url3, data=json.dumps(payload2), headers=headers)
        self.sensors_location = rsensor.headers['location']
        rsensor = requests.get(self.sensors_location)
        response = rsensor.json()
        self.sensorID = response['ID']
        return thing_location

    def sendObs(self, obs):
        url2 = self.thing_location + '/Datastreams'
        r2 = requests.get(url2)
        response2 = r2.json()
        datastreamID = response2['Datastreams'][0]['ID']
        urlOBS = self.rootURI() + 'Observations'
        headers = {'content-type': 'application/json'}
        payloadOBS = {'Time':time.strftime('%FT%T%z'),
                      'ResultValue':str(obs),
                      'ResultType':'Measure',
                      'Datastream':{'ID':datastreamID},
                      'Sensor' : {'ID' : self.sensorID}
                      }
        r3 = requests.post(urlOBS, data=json.dumps(payloadOBS), headers=headers)
        return r3.headers

        

##### Main #####

# Create instance of data class
thing1 = data(ID)
thing1.initRequest()

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# LED GPIO
GPIO_LED = 4
GPIO.setup(GPIO_LED,GPIO.OUT)

# Define GPIO to use on Pi
GPIO_PIR = 18

print "PIR Module Test (CTRL-C to exit)"

# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)      # Echo

Current_State  = 0
Previous_State = 0

try:

  print "Waiting for PIR to settle ..."

  # Loop until PIR output is 0
  while GPIO.input(GPIO_PIR)==1:
    Current_State  = 0    

  print "  Ready"     
    
  # Loop until users quits with CTRL-C
  while True :
   
    # Read PIR state
    Current_State = GPIO.input(GPIO_PIR)
   
    if Current_State==1 and Previous_State==0:
      # PIR is triggered
      print "  Motion detected!"
      thing1.sendObs(1)
      GPIO.output(GPIO_LED, True)
      # Record previous state
      Previous_State=1
    elif Current_State==0 and Previous_State==1:
      # PIR has returned to ready state
      print "  Ready"
      thing1.sendObs(0)
      GPIO.output(GPIO_LED, False)
      Previous_State=0
      
    # Wait for 10 milliseconds
    time.sleep(0.01)      
      
except KeyboardInterrupt:
  print "  Quit" 
  # Reset GPIO settings
  GPIO.cleanup()
  
  
