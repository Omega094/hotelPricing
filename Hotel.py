from collections import defaultdict 
class Hotel(object):
    
    def __init__(self, calendar, maxCapacity, threshold ):
        self.calendar = calendar 
        self.currentDate = None
        self.maxCapacity = maxCapacity
        self.totalRevenueCount = 0
        self.threshold = threshold 

    def computeRevenue(self):
        for vals  in self.calendar.get_values():
            self.totalRevenueCount += sum(vals)
        print self.totalRevenueCount 
        return 
    
    def reserveRoom(self, orders):
        for date, price in orders:
            if price >= self.threshold and len(self.calendar) < self.maxCapacity:
                self.calendar.append(price)
        return 
    

