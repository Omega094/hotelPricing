#Tripadvisor homework
#Author Jinxuan Zhao (Steven)

import datetime, csv, sys
from collections import defaultdict
"""
Uasge:

python BestHotelDeal.py <path to csv> <hotel name> <check in date> <nights stay>

Example:

python BestHotelDeal.py ./deals.csv "Hotel Foobar" 2016-03-10 1
"""




"""
####################Clarification####################
Assumptions I made in here:
It is vague that when the deal is rebate_3plus, should it be valid if the 
duration of a book exceeds the end_date of the deal ?

In here I make the deal valid as long as the start date is in between 
the deal's start_date and end_date. 
####################Clarification####################
"""



"""
In real word, each hotel and deal data should have their unique id,
and hotels data can be sharded by locations, each hotel's deal data 
should be stored in the same shard with hotel, because deal data is usually 
obtained through hotel. 
In here I simply used a hash table to "store" the hotel and deal.
"""
#This is a map from deal id it to its real data (object)
DEALDATA = {}
#This is a map from hotel name to its real data (object)
HOTELDATA = {}


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
            return float(self._nightly_rate)*duration + float(self._deal_value)
        if self._deal_type == "pct":
            return (1+float(self._deal_value)/100)* float(self._nightly_rate)*duration

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
        return bestDealID


"""
Script function that parses the csv file and stores deal and hotel data. 
When it come across invalid input, it skips it and keep parsing next line. 
In real world, we should also log the exception into some kind of error monitoring system. 
"""
def processDealData(f):
    with open(f, 'rU') as csvfile:
        lineReader = csv.reader(csvfile)
        next(lineReader, None)
        for hotel_name,nightly_rate,promo_txt,deal_value,deal_type,start_date,end_date in lineReader:
            try:
                deal = Deal(nightly_rate,promo_txt,deal_value,deal_type,start_date,end_date)
                DEALDATA[deal._id] = deal
                if hotel_name not in HOTELDATA:
                    HOTELDATA[hotel_name] = Hotel(hotel_name)
                HOTELDATA[hotel_name].addDealInfo(deal)
            except :
                pass
    return 

"""
Script function that finds the best deal of a specified hotel.  
"""
def findBestDeal(hotel_name, check_in_date, duration):
    start_date = datetime.datetime.strptime(check_in_date, "%Y-%m-%d")
    end_date   = start_date + datetime.timedelta(int(duration))
    return HOTELDATA[hotel_name].lookBestDeal(start_date, end_date) 



"""
Input can be invalid in 3 different ways:
1: argv count is wrong
2: csv file is not well formated, in this case we skip invalid row in csv because 
   we don't want to stop parsing a huge data file just becase of a single invalid input. 
3: Either one of hotel name, check in date, nights stay is invalid, in such case we just raise
   exceptions and print usage message. 
"""
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print ("Invalid input, please follow format: python BestHotelDeal.py <path to csv> <hotel name> <check in date> <nights stay>")
        exit()
    try :
        processDealData(sys.argv[1])
        hotel_name , check_in_date, duration = sys.argv[2], sys.argv[3], sys.argv[4]
        bestDealID = findBestDeal(hotel_name, check_in_date, duration)
        if bestDealID != None :
            print DEALDATA[bestDealID]._promo_txt
        else:
            print "no deals available"
    except:
        print "Please enter valid deal data file, hotel_name, check in date, and duration"

