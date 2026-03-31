import control
from control import tf, feedback, step_response, bode, margin, rlocus
import matplotlib.pyplot as plt
import numpy as np

# Set up the plant and controller tf
G = tf([1], [10, 1])  
C = tf([0.5, 1, 0.2], [1, 0])  

# Get the open loop and closed loop tf
L = C * G
T = feedback(L, 1) 

# Analyze the resposne for a setpoint of 40C
plt.figure()
t, y = step_response(T)
plt.plot(t, y*15+25)
plt.show(block=False)

# Frequency domain analysis
# Bode plot
plt.figure()
bode(L,dB=True)
gm, pm, _, _ = margin(L)
print("Gain margin:", 20*np.log10(gm))
print("Phase margin:", pm)
plt.show(block=False)

#rlocus plot
plt.figure()
rlist,klist=rlocus(L,plot=True)
plt.title('Root locus plot')
plt.grid(True)
plt.show(block=False)

# Poles directly
pl=control.poles(T)
print(f'poles are {pl}')


# bode of 1st order sys
K = 1
tau = 2
G = tf([K], [tau, 1])  # First-order system: K / (τs + 1)
plt.figure()
bode(G, dB=True, Hz=False, omega_limits=(0.01, 100), margins=True)
plt.show()
