import datetime


class BuyList:
    def __init__(self, date):
        self.date = date
        self.codes = []

    def add(self, code):
        self.codes.append(code)

    def __str__(self):
        return str(self.date) + " " + self.codes.__str__()