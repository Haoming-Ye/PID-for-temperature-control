import serial
import time

import nidaqmx

import numpy as np
import matplotlib.pyplot as plt
import time

import pandas as pd

MAX_V = 12

KP = 0.7         #0.5
KD = 2          #0.5
KI = 0.005         #0.01

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

def send_command(command):
    """Send a command to the HMP4040 over RS-232."""
    hmp4040.write((command + '\n').encode('ascii'))
    time.sleep(0.1)  # Brief pause to ensure command is processed

# try:
#     send_command()

#     # Set channel 1 voltage to 1V and current to 1A, hold for 5 seconds
#     send_command("INST CH1")          # Select Channel 1
#     send_command("VOLT 5")            # Set Voltage to 1V
#     send_command("CURR 1")            # Set Current to 1A
#     send_command("OUTP ON,(@1)")      # Turn on Channel 1 output (Alternative syntax)
#     time.sleep(5)                     # Wait for 5 seconds

#     # Set channel 1 voltage to 0.5V and current to 1A, hold for 10 seconds
#     send_command("VOLT 7.56585")          # Set Voltage to 0.5V
#     time.sleep(5)                    # Wait for 10 seconds

# finally:
#     # Turn off Channel 1 output and close the connection
#     send_command("OUTP OFF,(@1)")     # Alternative syntax for turning off Channel 1
#     hmp4040.close()

# print("Voltage and current settings applied successfully.")

def heat():
    send_command("INST OUT1")          # Select Channel 1
    send_command("VOLT 1")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("INST OUT2")          # Select Channel 2
    send_command("VOLT 1")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("OUTP:GEN 1")

    print('POWER SUPPLY TEST')

    time.sleep(1)

    send_command("OUTP:GEN 0")

    print('POWER SUPPLY GOOD')

    send_command("INST OUT1")          # Select Channel 1
    send_command("VOLT 0")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("INST OUT2")          # Select Channel 2
    send_command("VOLT 0")            # Set Voltage to 1V
    send_command("CURR 1.7")            # Set Current to 1.7A
    send_command("OUTP:SEL 1")

    send_command("OUTP:GEN 1")

    # Enable interactive plotting
    plt.ion()

    # Create the figure and axis
    fig, (ax,ex) = plt.subplots(1, 2, figsize=(10,5))

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

    errorA_data = []
    errorB_data = []

    # Create an empty line object
    tc_a1 = ax.plot([], [], label="TC-A1")[0]
    tc_a2 = ax.plot([], [], label="TC-A2")[0]
    tc_a3 = ax.plot([], [], label="TC-A3")[0]
    tc_a4 = ax.plot([], [], label="TC-A4")[0]

    tc_b1 = ax.plot([], [], label="TC-B1")[0]
    tc_b2 = ax.plot([], [], label="TC-B2")[0]
    tc_b3 = ax.plot([], [], label="TC-B3")[0]
    tc_b4 = ax.plot([], [], label="TC-B4")[0]

    ea = ex.plot([], [], label="Block A Error")[0]
    eb = ex.plot([], [], label="Block B Error")[0]

    # Set up axis limits or dont
    ax.set_xlim(auto=True)
    ax.set_ylim(20, 60)      
    ax.set_ylabel("Temperature [C]")
    ax.set_title("Temperature Plot")
    ax.legend()

    ex.set_xlim(auto=True)
    ex.set_ylim(auto=True)      
    ex.set_ylabel("Error [C]")
    ex.set_title("Error")
    ex.legend()

    # Start loop example
    t0=time.time()

    # Set up initial conds just in case
    then = t0

    int_A = 0
    int_B = 0

    control_A=0
    control_B=0

    old_A=0
    old_B=0

    # Start of the control loop
    for i in range(1000):

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

        error_A = 40 - temp_A
        error_B = 40 - temp_B

        errorA_data.append(error_A)
        errorB_data.append(error_B)

        if len(temp0_data) > 1:
            diff_A = (error_A - old_A)/(now - then)
            diff_B = (error_B - old_B)/(now - then)
        else:
            diff_A = 0
            diff_B = 0

        # Conditional Ki update
        if not ((error_A>0 and control_A>MAX_V) or (error_A<0 and control_A==0)):
            int_A += error_A * (now - then)
        if not ((error_B>0 and control_B>MAX_V) or (error_B<0 and control_B==0)):
            int_B += error_B * (now - then)

        control_A = round(KP*error_A + KD*diff_A + KI*int_A, 3)
        control_B = round(KP*error_B + KD*diff_B + KI*int_B, 3)

        if control_A > MAX_V:
            control_A = MAX_V

        if control_B > MAX_V:
            control_B = MAX_V

        if control_A < 0:
            control_A = 0

        if control_B < 0:
            control_B = 0

        print("----------------------------------------")
        print(f"LOOP NUMBER {i}")
        print("")

        print("TEMPERATURES")
        print(f"Temperature A: {temp_A}")
        print(f"Temperature B: {temp_B}")
       
        print("")
        print("VOLTAGES")
        print(f"Heater A: {control_A}")
        print(f"Heater B: {control_B}")


        send_command("INST OUT1")          # Select Channel 1
        send_command(f"VOLT {control_A}") # Set Voltage

        send_command("INST OUT2")          # Select Channel 2
        send_command(f"VOLT {control_B}") # Set Voltage

        # Update line data
        tc_a1.set_data(x_data, temp4_data)
        tc_a2.set_data(x_data, temp5_data)
        tc_a3.set_data(x_data, temp6_data)
        tc_a4.set_data(x_data, temp7_data)

        tc_b1.set_data(x_data, temp0_data)
        tc_b2.set_data(x_data, temp1_data)
        tc_b3.set_data(x_data, temp2_data)
        tc_b4.set_data(x_data, temp3_data)

        ea.set_data(x_data, errorA_data)
        eb.set_data(x_data, errorB_data)

        '''
        # Manually reset the limit dynamically
        if i > ax.get_xlim()[1]:
            ax.set_xlim(0, i + 20)
        '''
   
        # rescale limits automatically
        ax.relim()
        ax.autoscale_view()

        ex.relim()
        ex.autoscale_view()
   
        # Draw updated plots and pause for smooth update
        plt.pause(0.01)

        print("")
        print(f"Loop time: {now-then}")
        print("")

        old_A = error_A
        old_B = error_B

        then=now

    # Check total time
    print(now-t0)

    # stop interactive and keep plot
    plt.ioff()
    #plt.savefig("davoltage.png", dpi=300, bbox_inches='tight')
    #plt.show()
    plt.close('all')
    plt.pause(0.01) # this helps with flushing done the figures
    print('done')
   
    # flushing the voltage
    #send_command("INST OUT1")          # Select Channel 1
    #send_command(f"VOLT 0") # Set Voltage

    #send_command("INST OUT2")          # Select Channel 2
    #send_command(f"VOLT 0") # Set Voltage


    send_command("OUTP:GEN 0")     # Alternative syntax for turning off Channel 1
    hmp4040.close()



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
    ax.set_ylim(20, 60)      
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
