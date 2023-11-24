from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import numpy as np

fastf1.plotting.setup_mpl()

session = fastf1.get_session(2023, 'Monza', 'Q')


session.load()

lap = session.laps.pick_fastest()
pos = lap.get_telemetry()

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

circuit_info = session.get_circuit_info()
print(pos.columns)
# Get an array of shape [n, 2] where n is the number of points and the second
# axis is x and y.
track = pos.loc[:, ('X', 'Y')].to_numpy()
distance = pos.loc[:, ('Distance')].to_numpy().reshape((-1, 1))

print(track.shape, distance.shape)

# Convert the rotation angle from degrees to radian.
track_angle = circuit_info.rotation / 180 * np.pi

# Rotate and plot the track map.
rotated_track = rotate(track, angle=track_angle)
print(rotated_track.shape)
rotated_track = np.hstack((rotated_track, distance))
print(rotated_track.shape)

np.savetxt("monza_circuit.csv", rotated_track, delimiter=',', header='X,Y,Distance', comments="")
# pos.loc[:, ('Distance')].to_csv("test.csv")

# plt.plot(pos.loc[:, 0], pos.loc[:, 1])


# plt.show()
