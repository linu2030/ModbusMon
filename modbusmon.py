import minimalmodbus
import time
import paho.mqtt.client as mqtt
from contextlib import redirect_stdout

#PORT='COM3'
PORT='/dev/ttyUSB0'
SlaveAddress=1
RefreshTime=2
RetryTime=5
broker_address="homeassistant.local"
MqttClientID="MPPT"
LogFileName="modbusmon.py.txt"

MqttUser= "UserName"
MqttPw="Password"
StopAsyncIteration()

ChargeMode=0 
PVinputVoltage=0  
BatVoltage =0 
ChargingCurrent=0 
OutVoltInternalUse=0 
LoadVoltage=0 
LoadCurrent=0 
ChargingPower=0 
LoadPower=0 
Battreytemperature=0 
Internaltemperature=0 
Batterylevel=0 
CO2emissionReduction=0 
wFault=0 
systemhintsdetails=0 

def goto(linenum):
    global line
    line = linenum

def on_connect(client, userdata, flags, rc):
    if rc==0:
        with open(LogFileName, 'w') as f:
            with redirect_stdout(f):
                print("connected ok")

def on_message(client, userdata, flags):
    with open(LogFileName, 'w') as f:
        with redirect_stdout(f):
            print(str(message.payload.decode("utf-8")))

line = 1
while True:
    if line == 1:
        #Set up instrument
        try:
            instrument = minimalmodbus.Instrument(PORT,SlaveAddress,mode=minimalmodbus.MODE_RTU)
            #Make the settings explicit
            instrument.serial.baudrate = 9600      # Baud
            instrument.serial.bytesize = 8
            instrument.serial.parity   = minimalmodbus.serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout  = 1          # seconds
            goto(2)
        except Exception as e:
            with open(LogFileName, 'w') as f:
                with redirect_stdout(f):
                    print(e)
                    print('Error: Set up instrument retry again')
            time.sleep(RetryTime)
            goto(1)


    elif line == 2:
        try:
            with open(LogFileName, 'w') as f:
                with redirect_stdout(f):
                    print('Starting MQTT')
            
            global MqttPahoClient 
            MqttPahoClient = mqtt.Client(MqttClientID, transport="tcp", protocol=4) 
            #MqttPahoClient = mqtt.Client(MqttClientID, transport="tcp", protocol=4) #create new instance
            MqttPahoClient.username_pw_set(MqttUser,MqttPw)
            MqttPahoClient.connect(broker_address,1883,60) #connect to broker
            #MqttPahoClient.subscribe("raspberrypi/batvolt/value")
        
            MqttPahoClient.on_connect = on_connect
            #MqttPahoClient.loop_start()
            #MqttPahoClient.loop_forever() #start the loop
            goto(3)
          
        except Exception as e:
            with open(LogFileName, 'w') as f:
                with redirect_stdout(f):
                    print(e)
                    print('Error: creat mqtt client retry again ..')           
            time.sleep(RetryTime)
            goto(1)
   
    elif line == 3:
        try:
            l = instrument.read_registers(0, 16, 3 )
            ChargeMode= l[0] 
            PVinputVoltage=l[1] /10 
            BatVoltage =l[2] /10
            ChargingCurrent=l[3] /10 
            OutVoltInternalUse=l[4] /10
            LoadVoltage=l[5] /10
            LoadCurrent=l[6] /10
            ChargingPower=l[7]  
            LoadPower=l[8]  
            Battreytemperature=l[9]  
            Internaltemperature=l[10] 
            Batterylevel=l[11]  
            CO2emissionReduction=l[12] 
            wFault=l[13]  
            systemhintsdetails=l[14] 

            # print("ChargeMode ", ChargeMode)
            # print("PVinputVoltage ", PVinputVoltage )
            # print("BatVoltage ", BatVoltage)
            # print("ChargingCurrent ", ChargingCurrent)
            # print("OutVoltInternalUse ", OutVoltInternalUse)
            # print("LoadVoltage ", LoadVoltage)
            # print("LoadCurrent ", LoadCurrent)
            # print("ChargingPower ", ChargingPower)
            # print("LoadPower ", LoadPower)
            # print("Battreytemperature ", Battreytemperature)
            # print("Internaltemperature ", Internaltemperature)
            # print("Batterylevel ", Batterylevel)
            # print("CO2emissionReduction ", CO2emissionReduction)
            # print("wFault ", wFault)
            # print("systemhintsdetails ", systemhintsdetails)

            MqttPahoClient.publish("raspberrypi/batvolt/value",BatVoltage)
            MqttPahoClient.publish("raspberrypi/pvvolt/value",PVinputVoltage)
            MqttPahoClient.publish("raspberrypi/chargingcurrent/value",ChargingCurrent)
            MqttPahoClient.publish("raspberrypi/chargingpower/value",ChargingPower)
            MqttPahoClient.publish("raspberrypi/batterylevel/value",Batterylevel)
            MqttPahoClient.publish("raspberrypi/chargingmode/value",ChargeMode)
            MqttPahoClient.publish("raspberrypi/battreytemperature/value",Battreytemperature)
            MqttPahoClient.publish("raspberrypi/internaltemperature/value",Internaltemperature)
            time.sleep(RefreshTime)
            goto(3)              
            
        except Exception as e:
            goto(1)
            with open(LogFileName, 'w') as f:
                with redirect_stdout(f):
                    print(e)
                    print('Error: Read instrument retry again')

            time.sleep(RetryTime)
            goto(1)

    elif line == 20:
        instrument.serial.close()
        break
    elif line == 100:
        with open(LogFileName, 'w') as f:
            with redirect_stdout(f):
                print ("Nothing to Do ...")
        gotto(1)
