from crawler.his_data import get_his_data

class AssetsSummary:
    def __init__(self):
        self.cash = 0.0
        self.debt = 0.0
        self.stock_position = {}

    def change_position(self, flow):
        #print("change:", flow.code, flow.position, flow.flow)
        if flow.code not in self.stock_position.keys():
            self.stock_position[flow.code] = flow.position
        else:
            self.stock_position[flow.code] += flow.position
        self.cash += flow.flow
        #print("assets now:", self.cash, self.stock_position)

    def sum(self, date):
        #print("cash:", self.cash)
        sum = self.cash
        for code in self.stock_position.keys():
            #print("add ", code, self.stock_position[code], get_his_data(code, date))
            sum += self.stock_position[code] * get_his_data(code, date)
        return sum

class Flow(object):
    def __init__(self, time, code, position, flow):
        self.time = time
        self.code = code
        self.position = position
        self.flow = flow

def flowSort(flows):
    flows.sort(key=lambda x:x.time, reverse=False)