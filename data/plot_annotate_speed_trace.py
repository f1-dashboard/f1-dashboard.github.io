"""Plot speed traces with corner annotations
============================================

Plot the speed over the course of a lap and add annotations to mark corners.
"""


import matplotlib.pyplot as plt

import fastf1.plotting
import scipy


# enable some matplotlib patches for plotting timedelta values and load
# FastF1's default color scheme
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

# load a session and its telemetry data
session = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
session.load()

##############################################################################
# First, we select the fastest lap and get the car telemetry data for this
# lap.

lewis_lap = session.laps.pick_driver("HAM").pick_fastest()
lewis_car_data = lewis_lap.get_car_data().add_distance()

charles_lap = session.laps.pick_driver("LEC").pick_fastest()
charles_car_data = charles_lap.get_car_data().add_distance()

##############################################################################
# Next, load the circuit info that includes the information about the location
# of the corners.

circuit_info = session.get_circuit_info()

##############################################################################
# Finally, we create a plot and plot the speed trace as well as the corner
# markers.

team_color = fastf1.plotting.team_color(lewis_lap['Team'])

fig, ax = plt.subplots()
# ax.plot(lewis_car_data['Distance'], lewis_car_data['Speed'],
#         color=team_color, label=lewis_lap['Driver'])

v_min = lewis_car_data['Speed'].min()
v_max = lewis_car_data['Speed'].max()

import numpy as np
p = np.poly1d(np.polyfit(lewis_car_data['Distance'], lewis_car_data['Speed'], 16))
lewis_spline = scipy.interpolate.UnivariateSpline(lewis_car_data['Distance'], lewis_car_data['Speed'], s=10*len(lewis_car_data))
charles_spline = scipy.interpolate.UnivariateSpline(charles_car_data['Distance'], charles_car_data['Speed'], s=10*len(charles_car_data))

# print(s.get_coeffs())

xp = np.linspace(-2, lewis_car_data['Distance'].max(), 1000)

# plt.plot(lewis_car_data['Distance'], lewis_car_data['Speed'], '.', xp, lewis_spline(xp), '--')
# plt.plot(charles_car_data['Distance'], charles_car_data['Speed'], '.', xp, charles_spline(xp), '--')
plt.plot(xp, lewis_spline(xp) - charles_spline(xp), '--')

ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')
ax.legend()

plt.show()
