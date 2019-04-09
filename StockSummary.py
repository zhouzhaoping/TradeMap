class StockSummary:
    name = ""
    position = 0
    cost = 0.0      #买入花费
    earn = 0.0      #卖掉+分红
    value = 0.0
    profit = 0.0
    rate = 0.0

    def __init__(self, name, position, cost, earn):
        self.name = name
        self.position = position
        self.cost = cost
        self.earn = earn

    def add(self, position, cost, earn):
        self.position += position
        self.cost += cost
        self.earn += earn

    def rate(self, nav):
        self.value = self.position * nav
        self.profit = self.earn + self.value - self.cost
        self.rate = self.profit / self.cost * 100
        return
        #todo 收益率应该用最大投入本金计算？
        #if self.position != 0:# 依然持仓 TODO if cost > earn 岂不是零成本
        #    self.rate = self.profit / (self.cost - self.earn) * 100
        #else:# 卖光
            #print("end")
        #    self.rate = self.profit / self.cost * 100

    def print(self):
        print(self.name, self.position, round(self.cost,2), round(self.earn,2), round(self.profit, 2),
              str(round(self.rate, 2)) + "%")
