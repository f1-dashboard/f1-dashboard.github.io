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

fastest_lap = session.laps.pick_fastest()
car_data = fastest_lap.get_car_data().add_distance()

##############################################################################
# Next, load the circuit info that includes the information about the location
# of the corners.

circuit_info = session.get_circuit_info()

##############################################################################
# Finally, we create a plot and plot the speed trace as well as the corner
# markers.

team_color = fastf1.plotting.team_color(fastest_lap['Team'])

fig, ax = plt.subplots()
# ax.plot(car_data['Distance'], car_data['Speed'],
#         color=team_color, label=fastest_lap['Driver'])

v_min = car_data['Speed'].min()
v_max = car_data['Speed'].max()

import numpy as np
p = np.poly1d(np.polyfit(car_data['Distance'], car_data['Speed'], 16))
s = scipy.interpolate.UnivariateSpline(car_data['Distance'], car_data['Speed'])
print(s.get_coeffs())

xp = np.linspace(-2, car_data['Distance'].max(), 1000)

_ = plt.plot(car_data['Distance'], car_data['Speed'], '.', xp, p(xp), '-', xp, s(xp), '--')

ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')
ax.legend()

plt.show()
