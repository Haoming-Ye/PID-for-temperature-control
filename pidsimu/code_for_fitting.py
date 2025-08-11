import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd

# read from excel
df=pd.read_excel(r'C:\Users\10219\OneDrive\桌面\pidsimu\stepresponse.xlsx')

# your time and temp data, differentiated and normalized by the 3.36 W input
t = df['time'].to_numpy()
temp_raw = df['temp'].to_numpy()
temp_norm=(temp_raw-temp_raw[0])/3.36

# define the function to be fitted
def stepresponse(t, K, tau):
    return K * (1 - np.exp(-t / tau))

# fit the function with initial guesses obatined from the plots
popt, _ = curve_fit(stepresponse, t, temp_norm, p0=(temp_norm[-1], t[int(len(t)*0.2)]))

# Obtain the fitted parameters
K_fit, tau_fit= popt
print(f"Estimated K: {K_fit}, tau: {tau_fit}")

# Generate the fitted function
t_fit = np.linspace(t[0],t[-1],1000)
temp_fit=stepresponse(t_fit, K_fit, tau_fit)

# Plot the fitted curve and step response curve
plt.figure(figsize=(8, 5))
plt.plot(t, temp_norm, 'bo', label='Normalized Raw Data')
plt.plot(t_fit, temp_fit, 'r-', label=f'Fitted line with: K={K_fit:.2f}, τ={tau_fit:.1f}')
plt.xlabel('Time [s]')
plt.ylabel('Normalized Temperature (ΔT / 3.36W) [°C]')
plt.title('Plant Transfer Function Fit with the Step Response Data')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()