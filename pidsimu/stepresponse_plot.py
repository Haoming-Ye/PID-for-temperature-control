import serial
import time

import nidaqmx

import numpy as np
import matplotlib.pyplot as plt
import time

import pandas as pd

class LoggerNI:
    def __init__(self, port_name, daq_frequency):
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_thrmcpl_chan(port_name, thermocouple_type=nidaqmx.constants.ThermocoupleType.K, units=nidaqmx.constants.TemperatureUnits.DEG_C)
        self.task.timing.cfg_samp_clk_timing(rate=daq_frequency, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
       
    def read_temperature(self):
        return self.task.read()
       
    def close(self):
        self.task.close()

daq_freq = 3
daq = LoggerNI("NI9212R/ai0:7", daq_freq)

# Replace with your actual RS-232 port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
rs232_port = 'COM3'  # Change as needed
baud_rate = 9600             # Typically set to 9600 for RS-232

# Initialize the RS-232 connection
hmp4040 = serial.Serial(rs232_port, baud_rate, timeout=1)

# Define command func
def send_command(command):
    """Send a command to the HMP4040 over RS-232."""
    hmp4040.write((command + '\n').encode('ascii'))
    time.sleep(0.1)  # Brief pause to ensure command is processed

# step response
def stepresponse():
    send_command("INST OUT1")          # Select Channel 1
    send_command("VOLT 0")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("INST OUT2")          # Select Channel 2
    send_command("VOLT 0")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("OUTP:GEN 1")

    print('POWER SUPPLY TEST')

    time.sleep(1)

    send_command("OUTP:GEN 0")

    print('POWER SUPPLY GOOD')

    send_command("INST OUT1")          # Select Channel 1
    send_command("VOLT 3.5")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("INST OUT2")          # Select Channel 2
    send_command("VOLT 3.5")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("OUTP:GEN 1")

    # Enable interactive plotting
    plt.ion()

    # Create the figure and axis
    fig, ax = plt.subplots()

    # create empty data lists
    x_data = []

    temp0_data = []
    temp1_data = []
    temp2_data = []
    temp3_data = []
    temp4_data = []
    temp5_data = []
    temp6_data = []
    temp7_data = []

    # Create an empty line object
    tc_a1 = ax.plot([], [], label="TC-A1")[0]

    # Set up axis limits or dont
    ax.set_xlim(auto=True)
    ax.set_ylim(0, 30)      
    ax.set_ylabel("Temperature [C]")
    ax.set_title("Step Response Plot")
    ax.legend()

    # Start loop example
    t0=time.time()

    then = t0
    ta=[]
    for i in range(3600):
        now=time.time()
        # append actual time and actual signal  
        x_data.append(now-t0)
        temp0_data.append(daq.read_temperature()[0])
        temp1_data.append(daq.read_temperature()[1])
        temp2_data.append(daq.read_temperature()[2])
        temp3_data.append(daq.read_temperature()[3])
        temp4_data.append(daq.read_temperature()[4])
        temp5_data.append(daq.read_temperature()[5])
        temp6_data.append(daq.read_temperature()[6])
        temp7_data.append(daq.read_temperature()[7])

        temp_A = (temp4_data[-1] + temp5_data[-1] + temp6_data[-1] + temp7_data[-1])/4
        temp_B = (temp0_data[-1] + temp1_data[-1] + temp2_data[-1] + temp3_data[-1])/4

        ta.append((temp_A+temp_B)/2)

        # Update line data
        tc_a1.set_data(x_data, ta)

        '''
        # Manually reset limit if we have an initial limit
        if i > ax.get_xlim()[1]:
            ax.set_xlim(0, i + 20)
        '''
   
        # rescale limits automatically
        ax.relim()
        ax.autoscale_view()

        # Draw updated plots and pause for smooth update
        plt.pause(0.1)

        print("")
        print(f"Loop time: {now-then}")
        print("")

        then=now

    df=pd.DataFrame({'time':x_data,'temp':ta})
    df.to_excel('stepresponse.xlsx')
    # Check total time
    print(now-t0)

    # stop interactive and don't keep plot
    plt.ioff()
    #plt.savefig("davoltage.png", dpi=300, bbox_inches='tight')
    #plt.show()
    plt.close('all')
    plt.pause(0.01) # this helps with flushing down the figures
    print('done')

    # Close down the heater
    send_command("INST OUT1")          # Select Channel 1
    send_command(f"VOLT 0") # Set Voltage
    send_command("INST OUT2")          # Select Channel 2
    send_command(f"VOLT 0") # Set Voltage
    send_command("OUTP:GEN 0")     # Alternative syntax for turning off Channel 1
    hmp4040.close()