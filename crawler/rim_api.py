import requests
import datetime
import json
from crawler import cache


class RimValue:
    def __init__(self):
        self.code = ""
        self.name = ""
        self.vp = 0.0

    def dump(self, jsonstr):
        self.code = jsonstr["code"][7:].lower() + '.' + jsonstr["code"][:6]
        self.name = jsonstr["name"]
        self.vp = float(jsonstr["RIMResult"]["vp"])

    def __str__(self):
        return self.code + " " + self.name + " " + str(self.vp)

def get_rimvalue_top100(date, ifcache=True):
    if ifcache and cache.get(("rim100", date)):
        return cache.get(("rim100", date))

    url = "http://rimvalue.cn/api/rank?date=$date"
    url = url.replace("$date", str(date))
    #print(url)
    r = requests.get(url)
    j = json.loads(r.content)
    #print(j)
    if "latestDate" in j:
        return get_rimvalue_top100(j["latestDate"], ifcache)
    else:
        if ifcache:
            cache.insert_cache(("rim100", date), j)
        return j


if __name__ == "__main__":
    print(get_rimvalue_top100(datetime.datetime.strptime("2018-06-07", '%Y-%m-%d').date()))
    #print(get_rimvalue_top100(datetime.datetime.strptime("2018-06-06", '%Y-%m-%d').date()))
    #print(get_rimvalue_top100(datetime.datetime.strptime("2018-06-05", '%Y-%m-%d').date()))
    #print(get_rimvalue_top100(datetime.datetime.strptime("2018-06-04", '%Y-%m-%d').date()))
    #print(get_rimvalue_top100(datetime.datetime.strptime("2018-06-03", '%Y-%m-%d').date()))
    #print(get_rimvalue_top100(datetime.datetime.strptime("2018-06-02", '%Y-%m-%d').date()))