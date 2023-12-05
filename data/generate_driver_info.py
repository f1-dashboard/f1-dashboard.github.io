import fastf1
from fastf1.ergast import Ergast
import numpy as np
import pandas as pd

session = fastf1.get_session(2023, 'Monza', 'Q')

session.load()

infos = []
for driver in session.drivers:
    info = session.get_driver(driver)
    info.drop(['Position', 'ClassifiedPosition', 'Q1', 'Q2', 'Q3', 'CountryCode','GridPosition','Time','Status', 'Points'], inplace=True)
    print(info["HeadshotUrl"])
    infos.append(info)

data = pd.concat(infos, ignore_index=True, axis=1).transpose()
data.to_csv("driver_info.csv")

