from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting

fastf1.plotting.setup_mpl()

for i in range (1, 23):
    session = fastf1.get_session(2023, i)
    session.load()
    session.results.to_csv("data/" + str(i) + "/qual_results.csv")