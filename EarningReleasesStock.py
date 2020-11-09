#TODO: expand sheet; code the "before open" companies

import urllib.request, json
import datetime
from datetime import timedelta
import sheet,time
import matplotlib.pyplot as plt
import numpy as np

stockEvolutions = []
stockEvolutionsTemp = []
key=""
sheet.main()

#get percentage (up/down) from 2 days diff (deppending on stock market closing or opening)
def calculateStockEvolution(stockPriceBefore,stockPriceAfter):
	return (stockPriceAfter*100/stockPriceBefore)-100

def stockBeforeOpen(company,x):
	global stockEvolutions,stockEvolutionsTemp
	stockPriceBefore=0
	stockPriceAfter=0

	REDate = sheet.companiesBeforeOpen[x][0] #date in sheet
	REDate = datetime.datetime.strptime(REDate, '%y-%m-%d').date() #format string to date

	#api call to get symbol from company in sheet cell
	with urllib.request.urlopen("https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords="+company.replace(' ', '%20')+"&apikey="+key) as url:
		data = json.loads(url.read().decode())
		try:
			company=str(data['bestMatches'][0]["1. symbol"])
		except:
			print("error name of the company")
			#quit()

	print("symbol: "+company)
	time.sleep(13)

	#api call to get stock price after close, and the price on open of the day after
	with urllib.request.urlopen("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+company+"&outputsize=compact&apikey="+key) as url:
		data = json.loads(url.read().decode())
		try:
			try:
				print("REDate-1day close stock price:" + str(data['Time Series (Daily)'][(REDate  + timedelta(days=-1)).strftime("%Y-%m-%d")]['4. close']))
				stockPriceBefore=float(data['Time Series (Daily)'][(REDate  + timedelta(days=-1)).strftime("%Y-%m-%d")]['4. close'])
			except:
				print("REDate-3day close stock price:" + str(data['Time Series (Daily)'][(REDate  + timedelta(days=-3)).strftime("%Y-%m-%d")]['4. close']))
				stockPriceBefore=float(data['Time Series (Daily)'][(REDate  + timedelta(days=-3)).strftime("%Y-%m-%d")]['4. close'])
			print("REDate open stock price:" + str(data['Time Series (Daily)'][REDate.strftime("%Y-%m-%d")]['1. open']))
			stockPriceAfter=float(data['Time Series (Daily)'][REDate.strftime("%Y-%m-%d")]['1. open'])
			print("Stock evolution: "+str("{:.2f}".format(calculateStockEvolution(stockPriceBefore,stockPriceAfter)))+"% \n")
			stockEvolutions.append(float("{:.2f}".format(calculateStockEvolution(stockPriceBefore,stockPriceAfter))))
			stockEvolutionsTemp.append(float("{:.2f}".format(calculateStockEvolution(stockPriceBefore,stockPriceAfter))))
		except:
			print("error")
			#quit()

	time.sleep(13) #(5 call per minute allowed, each company needs 2 calls, 60/13<5)


#companiesAfterClose 2d list divided by day
for x in range(0,len(sheet.companiesBeforeOpen)):
	for i in range(1,len(sheet.companiesBeforeOpen[x])):
		print("\n"+sheet.companiesBeforeOpen[x][i]+":")
		stockBeforeOpen(sheet.companiesBeforeOpen[x][i],x)

def stockAfterClosing(company,x):
	global stockEvolutions
	stockPriceBefore=0
	stockPriceAfter=0

	REDate = sheet.companiesAfterClose[x][0] #date in sheet
	REDate = datetime.datetime.strptime(REDate, '%y-%m-%d').date() #format string to date

	#api call to get symbol from company in sheet cell
	with urllib.request.urlopen("https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords="+company.replace(' ', '%20')+"&apikey="+key) as url:
		data = json.loads(url.read().decode())
		try:
			company=str(data['bestMatches'][0]["1. symbol"])
		except:
			print("error name of the company")
			#quit()

	print("symbol: "+company)
	time.sleep(13)

	#api call to get stock price after close, and the price on open of the day after
	with urllib.request.urlopen("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+company+"&outputsize=compact&apikey="+key) as url:
		data = json.loads(url.read().decode())
		try:
			print("REDate close stock price:" + str(data['Time Series (Daily)'][REDate.strftime("%Y-%m-%d")]['4. close']))
			stockPriceBefore=float(data['Time Series (Daily)'][REDate.strftime("%Y-%m-%d")]['4. close'])
			print("REDate+1day open stock price:" + str(data['Time Series (Daily)'][(REDate  + timedelta(days=1)).strftime("%Y-%m-%d")]['1. open']))
			stockPriceAfter=float(data['Time Series (Daily)'][(REDate  + timedelta(days=1)).strftime("%Y-%m-%d")]['1. open'])
			print("Stock evolution: "+str("{:.2f}".format(calculateStockEvolution(stockPriceBefore,stockPriceAfter)))+"% \n")
			stockEvolutions.append(float("{:.2f}".format(calculateStockEvolution(stockPriceBefore,stockPriceAfter))))
		except:
			print("error")
			#quit()

	time.sleep(13) #(5 call per minute allowed, each company needs 2 calls, 60/13<5)


#companiesAfterClose 2d list divided by day
for x in range(0,len(sheet.companiesAfterClose)):
	for i in range(1,len(sheet.companiesAfterClose[x])):
		print("\n"+sheet.companiesAfterClose[x][i]+":")
		stockAfterClosing(sheet.companiesAfterClose[x][i],x)

#how did this stock index perform
totalStockEvolution=0
for j in range(0,len(stockEvolutions)):
	totalStockEvolution = totalStockEvolution + float(stockEvolutions[j])
print(totalStockEvolution)

#graph stock evolution of each comapny
plt.plot(stockEvolutions,"o")
plt.plot(stockEvolutionsTemp,"ro")
plt.xlabel('Stock Evolution')
plt.show()
