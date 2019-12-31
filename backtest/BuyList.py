import datetime


class BuyList:
    def __init__(self, date):
        self.date = date
        self.names = []
        self.codes = []
        self.rates = []
        self.ratesum = 0.0
        self.position = 1.0

    def add(self, code, name, rate):
        self.codes.append(code)
        self.names.append(name)
        self.rates.append(rate)
        self.ratesum += rate

    def countPosition(self):
        if self.ratesum / len(self.codes) * 0.3 < 1:
            self.position = self.ratesum / len(self.codes) * 0.3
        print(self)

    def __str__(self):
        return str(self.date) + " " + str(len(self.codes)) + " " + str(self.position) + ' '.join("|" + x + " " + "{0:.0%}".format(y) for (x, y) in zip(self.names, [rate / self.ratesum for rate in self.rates]))
