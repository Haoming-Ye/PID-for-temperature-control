import numpy as np
import matplotlib.pyplot as plt
import time

# Enable interactive plotting
plt.ion()

# Create the figure and axis
fig, ax = plt.subplots()

# create empty data lists
x_data = []
y_data = []

# Create an empty line object
line = ax.plot([], [], label="Temp/Voltage Signal")[0]

# Set up axis limits or dont
ax.set_xlim(auto=True)
ax.set_ylim(auto=True)       
ax.set_ylabel("Value")
ax.set_title("Temperature Plot")
ax.legend()

# Start loop example
t0=time.time()
for i in range(100):
    now=time.time()
    # append actual time and actual signal  
    x_data.append(now-t0)
    y_data.append(np.sin(i * 0.1))  

    # Update line data
    line.set_data(x_data, y_data)

    '''
    # Manually reset limit if we have an initial limit
    if i > ax.get_xlim()[1]:
        ax.set_xlim(0, i + 20)
    '''
    
    # rescale limits automatically
    ax.relim()
    ax.autoscale_view()
    
    # Draw updated plots and pause for smooth update
    plt.pause(0.05)

# Check total time
print(now-t0)

# stop interactive and keep plot
plt.ioff()
#plt.savefig("davoltage.png", dpi=300, bbox_inches='tight')
plt.show()
plt.close('all')
plt.pause(0.001) # this helps with flushing done the figures
print('done')
