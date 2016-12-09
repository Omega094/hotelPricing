import csv
import argparse
import datetime
from random import randint
from hotels import genHotelList
#CONSTANTS

#Change this if you want the deals to last longer
MAX_REBATE_DEAL_LENGTH = 15
MAX_3_REBATE_DEAL_LENGTH = 31
MAX_PERCENT_DEAL_LENGTH = 25

#Change this if you want to change the frequency of deals
# 0-Nothing
# 1-rebate
# 2-rebate_3plus
# 3-pct
# 4-Nothing
NUMBER_OF_DEALS = 4

#Comprehensive List of Hotel
HOTELS = genHotelList()
#Output File format is as follows:
#Hotel Name, Nightly Rate, Promo Text, Deal Value, Deal Type, Start Date, End Date, City
parser = argparse.ArgumentParser(description="CSV File Generator for our CSE 543 project")

#Length of Travel Stay (Default Value is 7)
parser.add_argument("length",type=int,default=7)

args = parser.parse_args();

stayDuration = args.length

outputFileName = 'deals.csv';
csvHeaderLine = ('hotel_name','nightly_rate','promo_txt','deal_value','deal_type','start_date','end_date','city')

with open(outputFileName, 'wb') as outFile:
	outFileWriter = csv.writer(outFile, dialect='excel')
	outFileWriter.writerow(csvHeaderLine)	
        
	deal = randint(0,NUMBER_OF_DEALS)
	csvArray = []

 	#Set first date for possible trip two days from now

	curDate = datetime.datetime.now()
        curDate += datetime.timedelta(days = 2)
	for hotel in HOTELS:
   		tripCurDay = curDate
		count = 0
		while(count < stayDuration):
			randomDeal = randint(0,NUMBER_OF_DEALS)
			if randomDeal == 0 or randomDeal == 4:
				count += 1
				tripCurDay += datetime.timedelta(days = 1)			
			elif randomDeal == 1:
				dealDuration = randint(1,MAX_REBATE_DEAL_LENGTH)
				rebate = randint(5,hotel[3])
                                deal_text = '${0} off your stay'.format(rebate)
				endDate = tripCurDay + datetime.timedelta(days=dealDuration)			
 				csvArray.append([hotel[0],hotel[1],deal_text,-rebate,'rebate',tripCurDay.strftime('%Y-%m-%d'),endDate.strftime('%Y-%m-%d'),hotel[2]])
				tripCurDay += datetime.timedelta(days=dealDuration + 1)	
				count += dealDuration	      	
			elif randomDeal == 2:
				dealDuration = randint(3,MAX_3_REBATE_DEAL_LENGTH)
				rebate = randint(5,hotel[3])
                                deal_text = '${0} off your stay 3 nights or more'.format(rebate)
				endDate = tripCurDay + datetime.timedelta(days=dealDuration)			
 				csvArray.append([hotel[0],hotel[1],deal_text,-rebate,'rebate',tripCurDay.strftime('%Y-%m-%d'),endDate.strftime('%Y-%m-%d'),hotel[2]])
				tripCurDay += datetime.timedelta(days=dealDuration + 1)	
				count += dealDuration
			elif randomDeal == 3:
				dealDuration = randint(1,MAX_PERCENT_DEAL_LENGTH)
				discountPercent = randint(5,hotel[4])
                                deal_text = '%{0} off your stay'.format(discountPercent)
				endDate = tripCurDay + datetime.timedelta(days=dealDuration)			
 				csvArray.append([hotel[0],hotel[1],deal_text,-discountPercent,'pct',tripCurDay.strftime('%Y-%m-%d'), endDate.strftime('%Y-%m-%d'),hotel[2]])
				tripCurDay += datetime.timedelta(days=dealDuration + 1)	
				count += dealDuration
	
	#Write out to CSV File
	for row in csvArray:
		outFileWriter.writerow(row)
