from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)


session = fastf1.get_session(2023, 'Monza', 'Q')

session.load()
circuit_info = session.get_circuit_info()
track_angle = circuit_info.rotation / 180 * np.pi


drivers = session.drivers
laps = []

for driver in drivers:
    driver_info = session.get_driver(driver)
    fastest_lap = session.laps.pick_driver(driver).pick_fastest().get_telemetry()
    xy = fastest_lap.loc[:, ('X', 'Y')].to_numpy()
    xy_rotated = rotate(xy, angle=track_angle)
    fastest_lap.drop(columns=['X', 'Y'], inplace=True)
    fastest_lap.insert(0, "X", xy_rotated[:, 0], False)
    fastest_lap.insert(1, "Y", xy_rotated[:, 1], False)
    fastest_lap.insert(0, "FullName", [driver_info.FullName] * fastest_lap.shape[0], False)
    fastest_lap.insert(1, "TeamId", [driver_info.TeamId] * fastest_lap.shape[0], False)
    laps.append(fastest_lap)



fastest_laps = pd.concat(laps)
print(fastest_lap.columns)

# for fastest lap, "Status" is always "OnTrack"
columns_to_remove = ['DriverAhead', 'DistanceToDriverAhead', 'SessionTime', 'Date', 'Status']
fastest_laps.drop(columns=columns_to_remove, inplace=True)
fastest_laps.to_csv("monza_2023_fastest_laps.csv")

# fast_leclerc = session.laps.pick_driver('LEC').pick_fastest()
# lec_car_data = fast_leclerc.get_car_data()
# t = lec_car_data['Time']
# vCar = lec_car_data['Speed']

# # The rest is just plotting
# fig, ax = plt.subplots()
# ax.plot(t, vCar, label='Fast')
# ax.set_xlabel('Time')
# ax.set_ylabel('Speed [Km/h]')
# ax.set_title('Leclerc is')
# ax.legend()
# plt.show()