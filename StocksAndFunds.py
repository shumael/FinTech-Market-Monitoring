import os
from twilio.rest import Client
import bs4
from datetime import datetime 
import requests as r
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
load_dotenv()

US_STOCK_LIST = ['FB','AMD','MSFT','PFE','SBUX','AAPL','TSLA','NKE','DELL','ADBE','T','STM','BABA','IAC','WUBA','AMZN','ORCL']
CDN_STOCK_LIST = ['FTS','SHOP','GIB.A','MFC','BNS','ACB','WEED','HEXO','CRON','TLRY','KXS','BAM.PF.F']
FUND_ID = ['789','808','201']
FUND_NAME = ['AGF U.S. Small-Mid Cap Fund','AGF Global Select Fund','AGF American Growth Class']
US_BASE_URL = "https://api.nasdaq.com/api/quote/"
CDN_BASE_URL = "https://www.tipranks.com/api/stockInfo/getDetails/?break=1576349858351&name=TSE:"
EXCHANGE_RATE_URL = "https://api.nasdaq.com/api/quote/USDCAD/info?assetclass=currencies"
FUND_BASE_URL = "https://www.agf.com/t2scr/fundPricesWeb/fpfundpage/displayFPFundPageResult.action?requestId=FP_DASHBOARD&lang=ENG&audience=NPFS&company=AGF&fundNum="

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")

class StockAndFunds():

	def parseUSStockInfo(self):
		client = Client(account_sid, auth_token)
		for i in range(len(US_STOCK_LIST)):
			stockUrl = US_BASE_URL+US_STOCK_LIST[i]+'/info?assetclass=stocks'
			stockGet = r.get(stockUrl)
			stockData = json.loads(stockGet.content)

			stockPrice = stockData['data']['primaryData']['lastSalePrice'][1:7]
			stockNetChange = float(stockData['data']['primaryData']['netChange'])
			deltaIndicator = stockData['data']['primaryData']['deltaIndicator']
			stockPercentageChange = stockData['data']['primaryData']['percentageChange'] 
			stockPercentageChangeFloat = float((stockPercentageChange.split('%'))[0]) 

			exchangeGet = r.get(EXCHANGE_RATE_URL)
			exchangeData = json.loads(exchangeGet.content)
			USDtoCDN = exchangeData['data']['primaryData']['lastSalePrice']
			
			#Case for Excellent Buying Oppurtunity (Decrease in price by more than 6%)
			if (deltaIndicator == 'down' and stockPercentageChangeFloat>6):
				toBeSent = (US_STOCK_LIST[i]+ ' is down by: '+'-'+stockPercentageChange+' and ' 
					+'-'+str(stockNetChange)+'. Current price is $'+stockPrice+'. Current Exchange Rate is ' 
					+str(USDtoCDN))
				client.messages.create(
				to = os.getenv("SENT_TO_NUMBER"),
				from_ = os.getenv("SENT_FROM_NUMBER"),
				body = toBeSent
				)
				print(toBeSent)

			#Case for Intermediate Buying Oppurtunity (Decrease in price by more than 4%)
			#Recommeded to monitor stock during market hours.
			if (deltaIndicator == 'down' and stockPercentageChangeFloat>=4 and stockPercentageChangeFloat<6):
				toBeSend = (US_STOCK_LIST[i]+ ' is down by: '+'-'+stockPercentageChange+' and '
					+'-'+str(stockNetChange)+'. Current price is $'+stockPrice+'. Monitor: '+ US_STOCK_LIST[i])
				client.messages.create(
				to = os.getenv("SENT_TO_NUMBER"),
				from_ = os.getenv("SENT_FROM_NUMBER"),
				body = toBeSent
				)
				print(toBeSent)


	def parseCADStockInfo(self):
		client = Client(account_sid, auth_token)
		for j in range(len(CDN_STOCK_LIST)):
			stockUrl = CDN_BASE_URL+CDN_STOCK_LIST[j]
			stockGet = r.get(stockUrl)
			stockData = json.loads(stockGet.content)

			stockPrice = float(stockData[0]['price'])
			stockNetChange = float(stockData[0]['changeAmount'])
			stockPercentageChangeFloat = float((stockData[0]['changePercent'])[:5]) 
			if (stockPercentageChangeFloat<0):
				deltaIndicator = 'down'
			if (stockPercentageChangeFloat>0):
				deltaIndicator='up'

			exchangeGet = r.get(EXCHANGE_RATE_URL)
			exchangeData = json.loads(exchangeGet.content)
			USDtoCDN = exchangeData['data']['primaryData']['lastSalePrice']
			
			#Case for Excellent Buying Oppurtunity (Decrease in price by more than 6%)
			if (deltaIndicator == 'down' and stockPercentageChangeFloat<=-6):
				toBeSent = (CDN_STOCK_LIST[j]+ ' is down by: '+str(stockPercentageChangeFloat)+'% and ' 
					+str(stockNetChange)+'. Current price is $'+str(stockPrice)+'. Current Exchange Rate is ' 
					+str(USDtoCDN))
				client.messages.create(
				to = os.getenv("SENT_TO_NUMBER"),
				from_ = os.getenv("SENT_FROM_NUMBER"),
				body = toBeSent
				)
				print(toBeSent)

			#Case for Intermediate Buying Oppurtunity (Decrease in price by more than 4%)
			#Recommeded to monitor stock during market hours.
			if (deltaIndicator == 'down' and (stockPercentageChangeFloat<=-4 and stockPercentageChangeFloat>=-6)):
				toBeSent = (CDN_STOCK_LIST[j]+ ' is down by: '+str(stockPercentageChangeFloat)+'% and ' 
					+str(stockNetChange)+'. Current price is $'+str(stockPrice)+'. Monitor: '+ CDN_STOCK_LIST[j])
				client.messages.create(
				to = os.getenv("SENT_TO_NUMBER"),
				from_ = os.getenv("SENT_FROM_NUMBER"),
				body = toBeSent
				)
				print(toBeSent)

	def parseAGFMutualFundInfo(self): 
		client = Client(account_sid, auth_token)
		for k in range(len(FUND_ID)):
			fundUrl = FUND_BASE_URL+FUND_ID[k]
			fundData = r.get(fundUrl)
			fundSoup = BeautifulSoup(fundData.content,'html.parser')
			fundPrice = (fundSoup.find_all('div',{'class':'small-6 cell Fund__information__data'}))[0].find('span',{'class':'Fund__information__title--price'}).text.strip()
			fundPercentChange = (fundSoup.find_all('div',{'class':'small-6 cell Fund__information__data'}))[2].find('span',{'class':'Fund__information__title--price'}).text.strip()
			fundPercentChangeFloat = float(fundPercentChange)
			fundPercentChangeIndicator = fundPercentChange[0]
		
			if((fundPercentChangeIndicator == '+') and fundPercentChangeFloat>0.5):
				print(fundPercentChange)
			if((fundPercentChangeIndicator == '-') and fundPercentChangeFloat<-0.5):
				toBeSent = (FUND_ID[k] + ' is down by ' + fundPercentChangeFloat + '. Monitor: ' + FUND_NAME[k])
				client.messages.create(
				to = os.getenv("SENT_TO_NUMBER"),
				from_ = os.getenv("SENT_FROM_NUMBER"),
				body = toBeSent
				)
			if((fundPercentChangeIndicator == '-') and fundPercentChangeFloat<-1):
				toBeSent = (FUND_ID[k] + ' is down by ' + fundPercentChangeFloat + '. Buy: ' + FUND_NAME[k])
				client.messages.create(
				to = os.getenv("SENT_TO_NUMBER"),
				from_ = os.getenv("SENT_FROM_NUMBER"),
				body = toBeSent
				)

def main():
	script = StockAndFunds()
	script.parseUSStockInfo()
	script.parseCADStockInfo()
	script.parseAGFMutualFundInfo()

main()