import fastf1

session = fastf1.get_session(2019, 'Monza', 'R')

session.load()
session.results.to_csv("monza_qualifying.csv")
#print(session.event)

leclerc = session.laps.pick_driver('LEC')
leclerc.to_csv("data/lec_monzaq_laps.csv")
max = session.laps.pick_driver('VER')
max.to_csv("data/ver_monzaq_laps.csv")
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