import numpy as np
import matplotlib.pyplot as plt
import control
import pandas as pd
from scipy.optimize import curve_fit

# #Step 1: Fitting the Model from step response
# # read from excel
# df=pd.read_excel(r'C:\Users\10219\OneDrive\桌面\pidsimu\stepresponse.xlsx')

# # your time and temp data, differentiated and normalized by the 3.36 W input
# t = df['time'].to_numpy()
# temp_raw = df['temp'].to_numpy()
# temp_norm=(temp_raw-temp_raw[0])/3.36

# # define the function to be fitted
# def stepresponse(t, K, tau):
#     return K * (1 - np.exp(-t / tau))

# # fit the function with initial guesses obatined from the plots
# popt, _ = curve_fit(stepresponse, t, temp_norm, p0=(temp_norm[-1], t[int(len(t)*0.2)]))

# # Obtain the fitted parameters
# K_fit, tau_fit= popt
# print(f"Estimated K: {K_fit}, tau: {tau_fit}")

# # Generate the fitted function
# t_fit = np.linspace(t[0],t[-1],1000)
# temp_fit=stepresponse(t_fit, K_fit, tau_fit)

# # Plot the fitted curve and step response curve
# plt.figure(figsize=(8, 5))
# plt.plot(t, temp_norm, 'bo', label='Normalized Raw Data')
# plt.plot(t_fit, temp_fit, 'r-', label=f'Fitted line with: K={K_fit:.2f}, τ={tau_fit:.1f}')
# plt.xlabel('Time [s]')
# plt.ylabel('Normalized Temperature (ΔT / 3.36W) [°C]')
# plt.title('Plant Transfer Function Fit with the Step Response Data')
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# # endregion

#Step 2: Model and Simulation parameters setup
# Resistance values for voltage
R=7.3  # in Ohms

# First-order plant: G(s) = K / (tau*s + 1)
K = 5.415985071366008
tau = 1571.2104158160894

# PID gains
Kp = 12
Ki = 0.1
Kd = 0

# Actuator saturation limits
p_min = 0.0
p_max = (12**2/R)*2
# endregion

#Step 3: Simulated Control loop and plotting functions
def pidloop(Kp,Ki,Kd,setpoint,time,disturbance):
    # Time setup, both in s
    t_total=time
    dt = 5
    steps= int(t_total/dt)
    t=np.linspace(0,t_total,steps)
    # Create empty arrays for plots
    temp=np.zeros(steps)
    u=np.zeros(steps)
    temp[0]=23
    # Controller setup
    integral=0
    derivative=0
    prev_error=0




    # PID control loop
    for i in range(0,steps-1):
        # Calculate error
        #if isinstance(setpoint,list):
        if type(setpoint)==list:
            if 0<=i<round(steps/3):
                error = setpoint[0] - temp[i]
            elif round(steps/3)<=i<round(steps*2/3):
                error = setpoint[1] - temp[i]
                if disturbance!=0 and round(steps*2/3)-24<i< round(steps*2/3)-20:
                    temp[i]+=disturbance
            elif round(steps*2/3)<=i<steps-1:
                error = setpoint[2] - temp[i]
        else:
            error = setpoint - temp[i]

        # PID terms
        if i!=0:
            integral += error * dt
            derivative = (error - prev_error) / dt
            prev_error = error
        else:
            integral += error * dt
            derivative = (error-0)/dt
            prev_error = error

        # Control power input
        p_raw = Kp * error + Ki * integral + Kd * derivative

        # Apply limits
        p = max(min(p_raw, p_max), p_min)
        u[i]=p

        # Back calculate voltage
        volt=np.sqrt(p/2*R)

        # windup check for integral
        if u[i] != p_raw:
            integral-=error * dt

        # First-order plant update (aka. discrete-time Euler integration)
        d_deltat = (-((temp[i]-temp[0]) / tau) + (K * u[i] / tau)) * dt
        temp[i+1] = temp[i]+d_deltat
        
        # # Manually added disturbances
        # if i ==200:
        #     temp[i+1] = temp[i]+d_deltat-10
        # elif i ==400:
        #     temp[i+1] = temp[i]+d_deltat-10
        # elif i ==600:
        #     temp[i+1] = temp[i]+d_deltat-10
        # elif i ==800:
        #     temp[i+1] = temp[i]+d_deltat-10
        # else:
        #     temp[i+1] = temp[i]+d_deltat

    if type(setpoint)==list:
        e=[setpoint[0]]*round(steps/3)+[setpoint[1]]*(round(steps*2/3)-round(steps/3))+[setpoint[2]]*(steps-round(steps*2/3))-temp
    else:
        e=setpoint-temp
    return temp, u, e, t

# Plotting function
def plotting(t,temp,u,e,setpoint,Kp,Ki=0,Kd=0):
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.plot(t, temp, label='Temperature')
    #plt.axhline(setpoint, color='gray', linestyle='--', label='Setpoint')
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [°C]")
    plt.title("Temperature vs Time")
    plt.grid(True)
    plt.legend()

    plt.subplot(1, 3, 2)
    plt.plot(t[:-2], np.sqrt(u/2*R)[:-2], label='Heater Voltage')
    plt.xlabel("Time [s]")
    plt.ylabel("Voltage [V]")
    plt.title("Heater Input")
    plt.grid(True)
    plt.legend()

    plt.subplot(1, 3, 3)
    plt.plot(t, e, label='error')
    plt.xlabel("Time [s]")
    plt.ylabel("error [°C]")
    plt.title("error plot")
    plt.grid(True)
    plt.legend()

    plt.suptitle(f'Kp={Kp},Ki={Ki},Kd={Kd}')
    plt.tight_layout()

# comparison plots
def compplot(t,temp,u,e,setpoint,Kp,Ki=0,Kd=0):
    # read from excel
    df=pd.read_excel(r'C:\Users\10219\OneDrive\桌面\pidsimu\pidtest.xlsx')
    # your time and temp data, differentiated and normalized by the 3.36 W input
    t_meas = df['time'].to_numpy()
    temp_meas = df['temp'].to_numpy()
    plt.figure(figsize=(8, 5))
    plt.plot(t_meas, temp_meas, 'bo', label='Avg. Measured Temperature')
    plt.plot(t, temp, 'r-', label='Simulated Temperature')
    #plt.axhline(setpoint, color='gray', linestyle='--', label='Setpoint')
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [°C]")
    plt.title("Temperature [°C] vs Time [s] Plot for temp control at varying temp.")
    plt.grid(True)
    plt.legend()
# endregion

#Step 4: PID gains tuning and results
# templist_kp=[]
# ulist_kp=[]
# ind_kp=0
# for Kp in np.arange(1,15,1):
#     temp, u,e,t=pidloop(Kp,0,0,40,800)
#     templist_kp.append(temp)
#     ulist_kp.append(u)
#     plotting(t,templist_kp[ind_kp],ulist_kp[ind_kp],e,40,Kp)
#     ind_kp+=1
# plt.show(block=True)

# Now, find the according Ki, maybe around 0.014
# templist_ki=[]
# ulist_ki=[]
# ind_ki=0
# for Ki in np.arange(0.01,0.05,0.01):
#     temp, u,e,t=pidloop(8,Ki,0,40,800)
#     templist_ki.append(temp)
#     ulist_ki.append(u)
#     plotting(t,templist_ki[ind_ki],ulist_ki[ind_ki],e,40,8,Ki)
#     ind_ki+=1
# plt.show(block=True)

# # Finally, do Kd for noises handling, want small
# templist_kd=[]
# ulist_kd=[]
# ind_kd=0
# for Kd in np.arange(0.01,0.05,0.01):
#     temp, u,e,t=pidloop(4,0.014,Kd,40,800)
#     templist_kd.append(temp)
#     ulist_kd.append(u)
#     #plotting(t,templist_kd[ind_kd],ulist_kd[ind_kd],e,40,4,0.014,Kd)
#     ind_kd+=1
#     #print(e[-1])









# Function to get responses
def checkup(Kp,Ki,Kd,sp,t,disturbance):
    a,b,c,d=pidloop(Kp,Ki,Kd,sp,t,disturbance)
    plotting(d,a,b,c,sp,Kp,Ki,Kd)
    #compplot(d,a,b,c,sp,Kp,Ki,Kd)

# Results check
# 8,0.03,0
#checkup(7,0.02,0,[39,40,40],3000,3)
checkup(8,0.03,0,[39,40,40],3000,disturbance=0.5)
checkup(8,0.015,0,[39,40,40],3000,disturbance=0.5)
#checkup(12,0.1,0,[40,30,70],6400)
#checkup(8,0.03,0,25)
#checkup(0.3,0.1,7,40)
plt.show(block=True)
# endregion

# #Step 5: Frequency domain analysis
# # Define the plant
# G = control.tf([K],[tau,1])

# # Define the controller
# print(f'{Kp},{Ki}')
# C = control.tf([Kp*1,Ki], [1,0]) 

# # Open loop tf
# L=C*G

# # Check reference following and disturbance rejection
# T =L/(1+L) # same as our cltf
# S= 1/(1+L)

# # Bode plot generation and margin calculation
# plt.figure() # giving new canvas
# control.bode(L, dB=True, display_margins=True, plot=True, Hz=True, title='Ideal Bode Plot')
# gm,pm,wg,wp=control.margin(L)
# print(f'GM{gm:.2f}\nPM{pm:.2f}')
# plt.show(block=False)

# # Check complementary sensitivity tf
# plt.figure()
# control.bode(T, dB=True, display_margins=False, plot=True, plot_phase=False, Hz=True, title='Ideal CS tf plot')
# plt.show(block=False)

# # Check sensitivity tf
# plt.figure()
# control.bode(S, dB=True, display_margins=False, plot=True, plot_phase=False, Hz=True, title='Ideal Sensitivity tf plot')
# plt.show(block=False)

# # Closed loop tf and poles calcualtion
# T=control.feedback(L)
# pl=control.poles(T)
# print(f'poles are{pl}')
# plt.figure()
# control.root_locus(L, grid=True, title='Root Locus Plot for the Ideal System', label='')
# plt.plot(pl.real, pl.imag, 'ro', label='Current Poles')
# plt.legend()
# plt.xlabel("Real")
# plt.ylabel("Imaginary")
# plt.grid(True)
# plt.axhline(0, color='black', linewidth=0.5)
# plt.axvline(0, color='black', linewidth=0.5)
# plt.show()
# #endregion
