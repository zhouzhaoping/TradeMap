import pickle
import os


# todo main cache pool
his_data_file = "data/his_data.pkl"
#his_data_file = "../curve/data/his_data.pkl"

def print_cache_all():
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}
    for (stockcode, date) in dict.keys():
        print(stockcode, date, dict[(stockcode, date)])

def get_cache():
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}
    return dict

def save_cache(dict):
    with open(his_data_file, 'wb') as f:
        pickle.dump(dict, f)

def insert_cache(key, value):
    dict = get_cache()
    dict[key] = value
    save_cache(dict)

def get(key):
    with open(his_data_file, 'rb') as f:
        try:
            dict = pickle.load(f)
        except:
            dict = {}
    if key in dict.keys():
        return dict[key]
    else:
        return None

if __name__ == "__main__":
    print_cache_all()
