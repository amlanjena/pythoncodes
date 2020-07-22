import datetime
import calendar

def findDay(date): 
	born = datetime.datetime.strptime(date, '%d %m %Y').weekday() 
	return (calendar.day_name[born]) 

# Driver program 
date = '25  07  2020'
print(findDay(date))
