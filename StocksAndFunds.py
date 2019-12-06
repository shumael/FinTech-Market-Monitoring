import os
from twilio.rest import Client
import bs4
from datetime import datetime 
import requests as r
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
load_dotenv()

US_STOCK_LIST = ['FB','AMD','MSFT','PFE','SBUX','AAPL','TSLA','NKE']
CDN_STOCK_LIST = ['FTS','SHOP']
US_BASE_URL = "https://api.nasdaq.com/api/quote/"
CDN_BASE_URL = "https://www.tipranks.com/api/stockInfo/getDetails/?break=1574646949523&name="
EXCHANGE_RATE_URL = "https://api.nasdaq.com/api/quote/USDCAD/info?assetclass=currencies"

#Example cdn base url = CDN_BASE_URL+'TSE:FTS'

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")



def parseUSStockInfo():
	client = Client(account_sid, auth_token)
	for i in range(len(US_STOCK_LIST)):
		stockUrl = US_BASE_URL+US_STOCK_LIST[i]+'/info?assetclass=stocks'
		stockGet = r.get(stockUrl)
		stockData = json.loads(stockGet.content)

		stockPrice = stockData['data']['primaryData']['lastSalePrice'][1:7]
		stockNetChange = float(stockData['data']['primaryData']['netChange'])
		deltaIndicator = stockData['data']['primaryData']['deltaIndicator']
		stockPercentageChange = stockData['data']['primaryData']['percentageChange'] #will be in body of message
		stockPercentageChangeFloat = float((stockPercentageChange.split('%'))[0]) #for data manipulation only, WILL NOT BE IN BODY OF MESSAGE

		exchangeGet = r.get(EXCHANGE_RATE_URL)
		exchangeData = json.loads(exchangeGet.content)
		USDtoCAD = exchangeData['data']['primaryData']['lastSalePrice']

		#Case for Excellent Buying Oppurtunity (Decrease in price by more than 6%)
		if (deltaIndicator == 'down' and stockPercentageChangeFloat>6):
			toBeSent = (US_STOCK_LIST[i]+ ' is down by: '+'-'+stockPercentageChange+' and ' 
				+'-'+str(stockNetChange)+'. Current price is $'+stockPrice+'. Current Exchange Rate is ' 
				+str(USDtoCAD))
			# client.messages.create(
			# to = "+16476489178",
			# from_ = os.getenv("SENT_FROM_NUMBER"),
			# body = toBeSent#must be a string
			# )
			print(toBeSent)

		#Case for Intermediate Buying Oppurtunity (Decrease in price by more than 4%)
		#Recommeded to monitor stock during market hours.
		if (deltaIndicator == 'down' and stockPercentageChangeFloat>4):
			toBeSend = (US_STOCK_LIST[i]+ ' is down by: '+'-'+stockPercentageChange+' and '
				+'-'+str(stockNetChange)+'. Current price is $'+stockPrice+'. Monitor: '+ US_STOCK_LIST[i])
			# client.messages.create(
			# to = "+16476489178",
			# from_ = os.getenv("SENT_FROM_NUMBER"),
			# body = toBeSent#must be a string
			# )
			print(toBeSent)


def parseCADStockInfo():
	#To be developed.

def parseAGFMutualFundInfo(): 
	#To be developed.
		
		
parseUSStockInfo()
