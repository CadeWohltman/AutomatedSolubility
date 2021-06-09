#!/home/pi/4funpt2/bin/python3.7

# Import sensors
import rgbsensor as rgb
import time
import board # Board, busio, and digitalio need to be indtalled from the Adafruit_blinka Library
import busio
import digitalio
import adafruit_tcs34725 as TCS # Install this dependency, found on github
import os
import RPi.GPIO as gpio # Included with Raspbian OS

# Import for conductivity 
import serial_conductivity_rev1 as Conduct

# Import for temperature sensor 
import pi_serial_test2 as temp_s

# Import for information input section (might not need to be here)
from datetime import date, datetime

# Import for pump
import pumpstuff as pumps

# Import libraries and modules for magnetic stirrer 
from ika.magnetic_stirrer import MagneticStirrer
import stirrer_control as stir

# Imports for email and information input files
import info_input5 as info
import python_code_email2 as email
import alert_email as alert
import alert_with_attachment as alert_attach

# Imports for stepper motor
import dispense_solid1 as solid

# Import for color to noise ratio
import RGB_color_noise_test

# User inputs the experiment setup information
data_log = info.info_input()
info.data_check1(data_log)
print(data_log)

# User inputs the email information for the email function later in the file
sender = input("Email address of the sender: ")
receiver = input("Email address of the receiver: ")
email_password = input("Enter the sender's email password: ")
email_info = [sender, receiver, email_password]

email.email_info_check(email_info)
print(email_info)

# Initialize sensors

i2c1 = board.I2C()  # Uses board.SCL and board.SDA
i2c2 = busio.I2C(board.D0,board.D1) # SDA and SCL used for a PCB Hat 
# Since these sensors have the same i2c address they need to be set up on different SDA & SCL pins
# Sensor 1 is bottom sensor 
# Sensor 2 is top sensor 
sensor1 = TCS.TCS34725(i2c1)
sensor2 = TCS.TCS34725(i2c2)
# The integration time and gain can be adjusted to fit whatever light conditions
# Longer integration times can be used for increased sensitivity at low light levels
# Acceptable values are 2.4, 24, 50 101, 154, and 700
# Values are in ms
sensor1.integration_time = 50
sensor2.integration_time = 50
# Sets the gain of the ADC to control the sensitivity of the sensor
# Acceptable values are 1, 4, 16, and 60 
# Values are dimensionless 
sensor1.gain = 4
sensor2.gain = 4
# We initialize our color arrays and time arrays
Red1 = []
Green1 = []
Blue1 = []
Red2 = []
Green2 = []
Blue2 = []
Gray1 = []
Gray2 = []
time2 = []
time3 = []
# Ask user if they want to calibrate 
g = True
while g == True:
	Message = input("Would you like to calibrate?")
	if Message.lower() == "yes":
		calibration = True
		rgb.CalibrateSensor()
		g = False
	elif Message.lower() == "no":
		calibration = False
		g = False
	else:
		print('Please retype input and try again')
		g = True

# Do a signal to noise ratio test so more accurate results are collected 
os.system('RGB_color_noise_test.py')

# Create empty lists for the time data and sensor data to fill in
time1 = []
temp = []
time2 = []
time3 = []
time4 = []
conductivity_list = []
pump_list = []



# Initialize the pump
pump = pumps.initializePort()

# End of definitions & setup

# Begining of coding sequence 

# Turning off incedent light measurement for both sensors by setting LED pin to low
gpio.setup(17, gpio.OUT, initial=gpio.LOW)
gpio.setup(25, gpio.OUT, initial=gpio.LOW)

# Re-initialize arrays so that arrays used for calibration are erased
Red1 = []
Green1 = []
Blue1 = []
Red2 = []
Green2 = []
Blue2 = []
Gray1 = []
Gray2 = []

# Run this function a couple times so that getGrAvg
for x in range(0, 10):
    Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3 = rgb.collect(Red1,Green1,Blue1,Red2,Green2,Blue2)
# Take last 10 values & average them for the our goal point and store that number for Goal 
Base_Gr = rgb.getGrAvg(Red1,Green1,Blue1)
# Base_Gr is used later for comparison with Cur_Gr

# Set magnetic stirrer speed and stirring time. These values can be changed
stirring_rpm_1 = 100 # Rpm (100-1500) in 100 increments
stirring_time_1 = 10 # In seconds
Cur_Gr = Base_Gr

# Initialize conductivity sensor 
ser = Conduct.initialize_conductivity()

# Add salts using the stepper motor. 
# Prcoess is adding salt, stir, then measure. 
# Solution should be oversaturated after this while loop terminates
# Saturation point is reached when RGB index is higher than Base_Gr by 1.1. 
while Cur_Gr < 1.1*Base_Gr:
    time1.append(temp_s.read_temp(time1)[0])
    temp.append(temp_s.read_temp(time1)[2])
    conductivity_list.append(Conduct.conductivity(ser,time4))
    solid.dispense_solid()
    stir.stirring_start(stirring_rpm_1)
    stir.stirring_wait(stirring_time_1) # Stirring_wait function sleeps the code so it will pause here to let the stirrer
    # to keep stirring
    stir.stirring_stop()
    Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3 = rgb.collect(Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3)
    # Update the value of Cur_gr. (using sensor 1 to detect solids)
    Cur_gr = rgb.getGrAvg(Red1,Green1,Blue1)
    
# Solution should now be over-saturated 
Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3 = rgb.collect(Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3)
Goal_Gr = rgb.getGr(Red2,Green2,Blue2)

difference = Cur_Gr - Goal_Gr

# Dispense liquid function from pump.py file 
# Units for pump volume inputs are in mL
capacity = data_log[2]
pumps.setFlowVol(pump, 20, capacity) # Placeholder value of 20 mL
tot_disp = 0 # Total volume dispensed over time 
beaker_vol = capacity # Total beaker capacity, will probably be hard coded
disp_vol = 20 # Discrete volume that will be dispensed into the solution

while difference > 5 & pumps.bigRedButton(pump, beaker_vol): # BigRedButton keeps 
    #track of current volume and stops processes when we are close to an overflow situation

    # Dispenses larger volumes of liquid based on the size difference we see between Cur_gr and Goal_Gr 
    if difference > 5 & difference < 10:
        disp_vol = 1
        pumps.setFlowVol(pump,disp_vol,beaker_vol)
    elif difference > 10 & difference < 15:
        disp_vol = 5
        pumps.setFlowVol(pump,disp_vol,beaker_vol)
    elif difference > 15:
        disp_vol = 10
        pumps.setflowVol(pump,disp_vol,beaker_vol)
    pump_list.append(disp_vol)
    tot_disp = tot_disp + disp_vol   # Updates total volume with the amount of dispensed volume

    stir.stirring_start(stirring_rpm_1)
    stir.stirring_wait(stirring_time_1) 
    stir.stirring_stop()
    Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3 = rgb.collect(Red1,Green1,Blue1,Red2,Green2,Blue2,time2,time3)
    Cur_Gr = rgb.getGr(Red1,Green1,Blue1)
    difference = Cur_Gr - Goal_Gr
else:
    # Email function that will alert the email inputted earlier, 
    # that experiment has failed and must be performed again
    # Email with text alert only
    alert.send_email(email_info[0], email_info[1], email_info[2])
    # Save all data in the user's desired filepath
    path = info.excel_placement()
    info.excel_create(path, data_log, time1, temp, time2, Red1, Green1, Blue1, time3, Red2,Green2,Blue2,
                             time4, conductivity_list, pump_list)
    # Email the Excel file that contains data
    alert_attach.send_email(path, email_info[0], email_info[1], email_info[2])

# The name of the Excel file and the file location where the user wants to save the file
# to copy path name:
# Windows - in File Explorer, left-click the file tree bar and type control-C
# Mac - in Finder, type option-command-C
path = info.excel_placement()

# Create the Excel file and save the data
info.excel_create(path, data_log, time1, temp, time2, Red1, Green1, Blue1, time3, Red2,Green2,Blue2,
                             time4, conductivity_list, pump_list)

density = data_log[3]

v_solvent = float(sum(pump_list))
print(v_solvent, "mL")

m_solvent = density*v_solvent
print("Mass of solvent")
print(m_solvent, "g")

while True:
    m_solute = input("Enter final mass of solute (unit in g): ")
    if info.is_number(m_solute):
        m_solute = float(m_solute)
        print(m_solute, "g")
        if m_solute < 0:
            print("Error: mass of final solute cannot be negative")
        elif m_solute > 1000:
            print("Error: mass of final solute is too large")
        else:
            break
    else:
        print("Error: Input data needs to be number")

while True:
    mass_solution = input("Enter final mass of solution (unit in g): ")
    if info.is_number(mass_solution):
        mass_solution = float(mass_solution)
        print(mass_solution, "g")
        if mass_solution < 0:
            print("Error: mass of final solution cannot be negative")
        elif mass_solution > 1000:
            print("Error: mass of final solution is too large")
        else:
            break
    else:
        print("Error: Input data needs to be number")

# Do math to calculate the concentration and save it in the file
# Equation reference: https://www.chem.purdue.edu/gchelp/howtosolveit/Solutions/concentrations.html
# Concentration (percent by mass)
concentration = m_solute/mass_solution * 100

data_log2 = [m_solute, mass_solution, concentration]
info.data_check2(data_log2)
print(data_log2)

# Add the information above into the Excel
info.excel_add(path, v_solvent, m_solvent, data_log2[1], data_log2[2])

# Email function implementation here
email.send_email_attachment(path, email_info[0], email_info[1], email_info[2])

