from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import os

def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

for i in range(22, 23):
    os.mkdir("C:/Users/Arjan/Desktop/f1 dash/f1-dashboard.github.io/data/"+str(i))
    session = fastf1.get_session(2023, i, 'Q')

    session.load()
    circuit_info = session.get_circuit_info()
    track_angle = circuit_info.rotation / 180 * np.pi

    drivers = session.drivers
    laps = []

    for driver in drivers:
        driver_info = session.get_driver(driver)
        fastest_lap = session.laps.pick_driver(driver).pick_fastest()
        print(fastest_lap.Time)
        if pd.isna(fastest_lap.Time):
            continue
        telem = fastest_lap.get_telemetry()
        
        fastest_lap = telem
        xy = fastest_lap.loc[:, ('X', 'Y')].to_numpy()
        xy_rotated = rotate(xy, angle=track_angle)
        fastest_lap.drop(columns=['X', 'Y'], inplace=True)
        fastest_lap.insert(0, "X", xy_rotated[:, 0], False)
        fastest_lap.insert(1, "Y", xy_rotated[:, 1], False)
        fastest_lap.insert(0, "FullName", [driver_info.FullName] * fastest_lap.shape[0], False)
        fastest_lap.insert(1, "TeamId", [driver_info.TeamId] * fastest_lap.shape[0], False)
        laps.append(fastest_lap)

    fastest_laps = pd.concat(laps)

    # for fastest lap, "Status" is always "OnTrack"
    columns_to_remove = ['DriverAhead', 'DistanceToDriverAhead', 'SessionTime', 'Date', 'Status']
    fastest_laps.drop(columns=columns_to_remove, inplace=True)
    fastest_laps.to_csv("data/" + str(i) + "/" + "fastest_laps.csv")