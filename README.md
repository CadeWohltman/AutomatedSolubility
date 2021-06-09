# AutomatedSolubility
An unfinished Python repository for determining the solubility points for novel combinations of salts and liquids.

![Sol](https://user-images.githubusercontent.com/85246308/121282489-75ab3d80-c88e-11eb-80e2-d352101327a5.jpeg)

This is the code package for an automated solubility device and is implemented on a Raspberry Pi 3B. This package has other dependencies that can be found here:

* Ika Magnetic Stirrer: https://pypi.org/project/ika/
* Adafruit Python Shell: https://pypi.org/project/adafruit-python-shell/
* Adafruit Blinka Library: https://pypi.org/project/Adafruit-Blinka/
* TCS34725 RGB Sensor: https://pypi.org/project/adafruit-circuitpython-tcs34725/

The objective of this code package is to find the saturation point of novel combinations of salts and solvents using two RGB color sensors to record RGB light data
emitted from an LED in the range of 0 to 255. The system is designed to scope a range for the solution's solubility and reduce human burden on solubility
measurement. Conductivity and temperature sensors are used in the code for informational purposes. 

The code should take a liquid and use dispense functions to oversaturate the solution. This over saturation point is determined by a slight increase in the RGB
index of the solution when compared to before and after the solid delivery. To ensure all salts have been dissolved we use an IKA magnetic stirrer to agitate the
solution.  

A custom PCB was used along with a a T-cobbler plus to help route all the connections to Raspberry Pi. 

![PCBGerber](https://user-images.githubusercontent.com/85246308/121282752-e2bed300-c88e-11eb-903e-8b345ee6c7c4.jpg)

Full Wiring Schematic can be found here:
![FinalCircuit_bb-1](https://user-images.githubusercontent.com/85246308/121282812-fa965700-c88e-11eb-90a4-256b31be0332.png)

This code still has some errors in the MainRGB.py file. When trying to use the the dependent .py files there were import and array size issues. Each component
worked on their own using these .py files but implementation in the Main file and on the Raspberry Pi caused issues.
