import json
import pickle

def create_pickle():
    # Read the JSON file
    with open('projects.json', 'r') as json_file:
        data = json.load(json_file)
    # Write to a pickle file
    with open('projects.pickle', 'wb') as pickle_file:
        pickle.dump(data, pickle_file)