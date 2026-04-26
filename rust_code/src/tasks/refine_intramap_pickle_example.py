# intramap=np.load(f'data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.npy', allow_pickle=True).item()
# intermap = np.load(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy', allow_pickle=True).item()

# change the above lines to below ones to load data from the underlying pickle format directly
# this saves time and effort on the rust side

with open(f'data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.pickle', mode='rb') as intra_source:
    intramap = pickle.load(intra_source)
with open(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.pickle', mode='rb') as inter_source:
    intermap = pickle.load(inter_source)
