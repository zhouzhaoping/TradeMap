import pickle

his_data_file = "data/his_data.pkl"

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


if __name__ == "__main__":
    print_cache_all()
