
import datetime, csv, sys
from collections import defaultdict
#This is a map from deal id it to its real data (object)
DEALDATA = {}
#This is a map from hotel name to its real data (object)
HOTELDATA = {}

#This is a map from location to hotel data
LOCATIONDATA = defaultdict(list)


"""
Each deal has it's field, which could be parsed from the csv file. 
"""
class Deal(object):

    """
    id is a static variable so each deal has its static id.
    """
    deal_id = 0
    def __init__(self, nightly_rate, promo_txt, deal_value, deal_type ,start_date, end_date):
        self._id = self.__class__.deal_id
        self.__class__.deal_id += 1
        self._nightly_rate = nightly_rate
        self._promo_txt = promo_txt
        self._deal_value = deal_value
        self._deal_type = deal_type
        self._start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        self._end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        self._hotel_id = None

    """
    When we have a deal, since we know it's deal type and deal amount, we can 
    directly compute it's price after deal. 
    """
    def computeRateByDeal(self, start_date, end_date):
        duration  = (end_date - start_date).days
        if self._deal_type in( "rebate","rebate_3plus" ):
            price =  float(self._nightly_rate)*duration + float(self._deal_value)
        if self._deal_type == "pct":
            price =  (1+float(self._deal_value)/100)* float(self._nightly_rate)*duration
        #print price, start_date, end_date, self._deal_type, self._deal_value ,self._nightly_rate

        return price

    """
    For a api perspective, we might want to get the hotel through the deal. 
    """
    def setHotelId(self, hotel_id):
        self._hotel_id = hotel_id
        return 


"""
Each hotel has a field that stores all its deals' id. 
"""
class Hotel(object):

    """
    id is a static variable so each hotel has its static id.
    """
    hotel_id = 0
    def __init__(self, hotel_name):
        self._hotel_name = hotel_name
        self._hotel_id = self.__class__.hotel_id 
        self.__class__.hotel_id += 1
        self._deals = set()

    def addDealInfo(self, deal):
        self._deals.add(deal._id)
        deal.setHotelId(self._hotel_id)
        return 

    """
    Since the way we query deal already specifies hotel, therefore we can directly traverse 
    all deals of the specified hotel and get the best deal . 
    """
    def lookBestDeal(self,start_date, end_date):
        bestDealID, bestDealPrice = None, float("inf")
        duration = end_date - start_date
        for deal_id in self._deals:
            deal = DEALDATA[deal_id]
            if (deal._deal_type in ("rebate", "pct") and deal._start_date <= start_date and end_date <= deal._end_date)\
                or (deal._deal_type == "rebate_3plus" and deal._start_date <= start_date and duration.days >= 3):
                total_price = deal.computeRateByDeal(start_date, end_date)
                if total_price <= bestDealPrice:
                    bestDealPrice = total_price
                    bestDealID = deal._id
        return bestDealID, bestDealPrice
"""
Script function that parses the csv file and stores deal and hotel data. 
When it come across invalid input, it skips it and keep parsing next line. 
In real world, we should also log the exception into some kind of error monitoring system. 
"""

def processDealData(f):
    with open(f, 'rU') as csvfile:
        lineReader = csv.reader(csvfile)
        #print lineReader
        next(lineReader, None)
        for hotel_name,nightly_rate,promo_txt,deal_value,deal_type,start_date,end_date, city in lineReader:
            #print hotel_name,nightly_rate,promo_txt,deal_value,deal_type,start_date,end_date, city
            try:
                hotel_name = hotel_name + "-"+city
                deal = Deal(nightly_rate,promo_txt,deal_value,deal_type,start_date,end_date)
                DEALDATA[deal._id] = deal
                if hotel_name not in HOTELDATA:
                    HOTELDATA[hotel_name] = Hotel(hotel_name)
                    LOCATIONDATA[city].append(HOTELDATA[hotel_name])
                HOTELDATA[hotel_name].addDealInfo(deal)
            except :
                pass
    #print LOCATIONDATA
    return 

def greedyPathSearching(cities, start_date, duration):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date   = start_date + datetime.timedelta(int(duration))
    print start_date, end_date
    all_paths = []
    cities = set(cities)
    dfsSearchCities(cities, start_date, duration, [], all_paths, 0)
    return all_paths

def greedyPathSearchingWithBudgetConstraint(pruning,budgetConstraint, cities, start_date, duration):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date   = start_date + datetime.timedelta(int(duration))
    print start_date, end_date
    all_paths = []
    cities = set(cities)
    dfsSearchCitiesWithBudgetConstraint(pruning,budgetConstraint, cities, start_date, duration, [], all_paths, 0)
    return all_paths

def greedyPathSearchingWithStayOverConstraint(pruning, minStayOver, maxStayOver,cities, start_date, duration):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date   = start_date + datetime.timedelta(int(duration))
    print start_date, end_date
    all_paths = []
    cities = set(cities)
    dfsSearchCitiesWithStayOverConstraint(pruning, minStayOver, maxStayOver,cities, start_date, duration, [], all_paths, 0)
    return all_paths
 

def dfsSearchCities(cities,current_date, duration, current_path, all_paths, current_expense):
    if not cities and duration == 0: 
        all_paths.append(current_path)
        return 
    for nextCity in cities:
        cities.remove(nextCity)
        for hotel in LOCATIONDATA[nextCity]:
            for d in xrange(1, duration+1):
                bestDeal, bestDealPrice = hotel.lookBestDeal(current_date , current_date+datetime.timedelta(int(d)) )
                if bestDeal == None: continue
                nextPath = (nextCity,current_date, current_date+datetime.timedelta(int(d)), bestDeal, current_expense+bestDealPrice)
                dfsSearchCities(cities, current_date+datetime.timedelta(int(d)),  duration - d ,current_path + [nextPath],all_paths, current_expense + bestDealPrice)
        cities.add(nextCity)
    return 


def dfsSearchCitiesWithBudgetConstraint(pruning ,budgetConstraint,cities,current_date, duration, current_path, all_paths, current_expense):
    #Early pruning when we find the search is running out of budget 
    if pruning and current_expense > budgetConstraint: 
        print "larger !!!!!"
        return 
    if (len(cities) ==0  ) and duration == 0 and current_expense < budgetConstraint: 
        all_paths.append(current_path)
        return 
    for nextCity in cities:
        cities.remove(nextCity)
        for hotel in LOCATIONDATA[nextCity]:
            for d in xrange(1, duration+1):
                bestDeal, bestDealPrice = hotel.lookBestDeal(current_date , current_date+datetime.timedelta(int(d)) )
                if bestDeal == None: continue
                nextPath = (nextCity,current_date, current_date+datetime.timedelta(int(d)), bestDeal, current_expense+bestDealPrice)
                dfsSearchCities(cities, current_date+datetime.timedelta(int(d)),  duration - d ,current_path + [nextPath],all_paths, current_expense + bestDealPrice)
        cities.add(nextCity)
    return 

def dfsSearchCitiesWithStayOverConstraint(pruning, minStayOver, maxStayOver,cities,current_date, duration, current_path, all_paths, current_expense):
    #Early pruning when we find the search is running out of budget 
    if not cities and duration == 0 : 
        for a, start, end , b, c in current_path:
            if (end - start).days < minStayOver or (end - start).days > maxStayOver:
                return 
        all_paths.append(current_path)
        return 
    for nextCity in cities:
        cities.remove(nextCity)
        for hotel in LOCATIONDATA[nextCity]:
            for d in xrange(1, duration+1):
                #Do pruning here 
                if pruning and d < minStayOver or d > maxStayOver:
                    continue
                bestDeal, bestDealPrice = hotel.lookBestDeal(current_date , current_date+datetime.timedelta(int(d)) )
                if bestDeal == None: continue
                nextPath = (nextCity,current_date, current_date+datetime.timedelta(int(d)), bestDeal, current_expense+bestDealPrice)
                dfsSearchCities(cities, current_date+datetime.timedelta(int(d)),  duration - d ,current_path + [nextPath],all_paths, current_expense + bestDealPrice)
        cities.add(nextCity)
    return 


import timeit
def testPruning(cities, start_date, duration, budgetConstraint,minStayOver, maxStayOver):
    start = timeit.default_timer()
    all_paths = greedyPathSearching(["San Diego", "Denver","St. Louis"], "2016-12-12", 10)
    #Your statements here
    stop = timeit.default_timer()
    print str(stop - start) + " seconds used, which generates " + str(len(all_paths)) + "paths";
    
    
    start = timeit.default_timer()
    all_paths_budget_limit_pruning_false =  greedyPathSearchingWithBudgetConstraint(False , budgetConstraint, ["San Diego", "Denver","St. Louis"], "2016-12-12", 10)
    stop = timeit.default_timer()
    print str(stop - start) + " seconds used, which generates " + str(len(all_paths_budget_limit_pruning_false)) + "paths without pruning for limiting budgets";
    

    start = timeit.default_timer()
    all_paths_budget_limit_pruning_true =  greedyPathSearchingWithBudgetConstraint(True , budgetConstraint, ["San Diego", "Denver","St. Louis"], "2016-12-12", 10)
    stop = timeit.default_timer()
    print str(stop - start) + " seconds used, which generates " + str(len(all_paths_budget_limit_pruning_true)) + "paths with pruning for limiting budgets";





if __name__ == "__main__":
    processDealData("deals_total.csv")
    all_paths = greedyPathSearching(["San Diego", "Denver","St. Louis"], "2016-12-12", 30)
    #all_paths_budget_limit = 
    testPruning(["San Diego", "Denver","St. Louis"], "2016-12-12", 10, 2423.0, None, None)
    #print all_paths
    print min(all_paths, key = lambda x: x[-1])