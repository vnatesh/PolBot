import json
import re
import string
import os
import sys
from regexPatterns import *
from sqlConn import *
tmpPath = "~/PolBot/tmp/"


# function to set allmarkets, allSecurities, and report_id variables
def set_rcp_environment(connection):
	global report_id, allMarkets, allSecurities
	# # Get the last report id and increment it by 1 for manual insertion in mySQL later on
	cursor = connection.cursor()
	cursor.execute("select max(report_id) from politics.report_rcp")
	report_id = cursor.fetchone().values()[0]
	if report_id ==None: 
		report_id = 1
	else: 
		report_id = report_id+1
	# add the report id to mySQL table report_rcp
	cursor = connection.cursor()
	sql = "INSERT INTO `report_rcp` (`report_id`) VALUES (%s)"
	cursor.execute(sql, (report_id))
	connection.commit()
	# Get markets
	cursor = connection.cursor()
	cursor.execute("select * from markets")
	allMarkets = cursor.fetchall()
	allMarkets = {i.values()[1] : i.values()[0] for i in allMarkets}
	# Get securities 
	cursor = connection.cursor()
	cursor.execute("select * from securities")
	allSecurities = cursor.fetchall()
	allSecurities = {i.values()[1] : i.values()[0] for i in allSecurities}


'''

This class instantiates an approvalPoll object...it takes case of 
		- Parsing the poll numbers from the txt/html file, and alerting the trader if there was unsuccessful scraping of the approval rate
		- Alerting the user (via text message) when a poll changes at least 0.001 since the poll number from the most recent scrape (usually a minute)
		- Inserting the new data into mysql

'''

class approvalPoll(object):
	approvalRate = None
	def __init__(self, market, security, report_id):
		self.market = market
		self.security = security
		self.report_id = report_id
	def parse(self):
		data = open('%s%s' % (tmpPath, self.market + self.security + '.txt')).read()
		for i in approvalPollRegex[self.security][self.market]:
			pattern = re.compile(i)
			data = ''.join(re.findall(pattern, data))
		try: 
			a = float(data)
		except ValueError:
			os.system('''echo 'Presidential approval poll scraping error. Web format of %s poll may have changed. Will not scrape this poll' | mail -s 'scraping error' "email1"''' % (self.market))
			return None
		self.approvalRate = float(data) /100
	def alert(self):
		if report_id == 1:
			return None
		tmpID = self.report_id - 1
		cursor = connection.cursor()
		cursor.execute("SELECT price FROM import_rcp WHERE report_id = %s AND market = %s" % (tmpID, allMarkets[self.market]))
		lastValue = cursor.fetchone()
		if lastValue == None:
			return None
		lastValue = float(lastValue.values()[0])
		diff = self.approvalRate - lastValue
		if round(abs(diff),3)>=0.001:
			os.system('''echo '%s has changed from %s to %s' | mail -s 'RCP Update' "phoneNumber@vtext.com"''' % (self.market, lastValue, self.approvalRate))
			os.system('''say "%s has changed...alert alert alert alert alert"''' % self.market)
	def insert(self):
		cursor = connection.cursor()
		sql = "INSERT INTO `import_rcp` (`report_id`,`market`,`security`,`price`) VALUES (%s, %s, %s, %s)"
		cursor.execute(sql, (self.report_id, allMarkets[self.market], allSecurities[self.security], self.approvalRate))
		connection.commit()

# ----------------------------------------------------------------------------------

'''

Partial python wrapper for the exchange trading data extraction API. For the rcp strategy, we only care about the lastTradePrice which 
is the latest buy yes or sell yes price. This function is only used in the rcp strategy

example:
getExchange('market1','import_rcp', allSecurities, allMarkets)
getExchange('market2','import_gallup', allSecurities, allMarkets)

 '''


def getExchange(security, table, allSecurities, allMarkets):
	market = 'exchangeName'
	dataObject = json.load(open('%s%s' % (tmpPath, security + 'exchangeName.json'),'r'))
	securities = [dataObject['Contracts'][i]['Name'] for i in xrange(len(dataObject['Contracts']))]
	tradePrice = [dataObject['Contracts'][i]['LastTradePrice'] for i in xrange(len(dataObject['Contracts']))]
	for sec in xrange(len(securities)):
		# check to see if any new securities have been added on the exchange...when a market updates every week, the actual security names
		# may change depending on the value of the underlying security (eg. if RCP changes, the bracket names may change)
		if securities[sec] not in allSecurities.keys():
			cursor = connection.cursor()
			sql = "INSERT INTO `securities` (`name`) VALUES (%s)"
			cursor.execute(sql, (securities[sec]))
			connection.commit()
		# re-get the securities table from mysql, in case new securities have been added
		cursor = connection.cursor()
		cursor.execute("select * from securities")
		allSecurities = cursor.fetchall()
		allSecurities = {i.values()[1] : i.values()[0] for i in allSecurities}
		temp = "INSERT INTO %s " % table
		cursor = connection.cursor()
		sql = temp + "(`report_id`,`market`,`security`,`price`) VALUES (%s, %s, %s, %s)"
		cursor.execute(sql, (report_id, allMarkets[market], allSecurities[securities[sec]], tradePrice[sec]))
		connection.commit()



'''
Complete python wrapper for market data ETL. These functions are used in the algo strategy (and potentially any new strat in 
any market, due to the generality of the function and corresponding DDL)

'''
def set_algo_environment(connection, market):
	# set report_id to be global so we can insert it with all the data later
	global report_id
	# Get the last report id and increment it by 1 for manual insertion in mySQL later on
	cursor = connection.cursor()
	cursor.execute("select max(report_id) from politics.report_%s" % market)
	report_id = cursor.fetchone().values()[0]
	if report_id ==None: 
		report_id = 1
	else: 
		report_id = report_id+1
	# add the report id to mySQL table report_rcp
	cursor = connection.cursor()
	sql = "INSERT INTO `report_%s`" % market  + "(`report_id`) VALUES (%s)"
	cursor.execute(sql, (report_id))
	connection.commit()


# parse the volume data from raw exchangeName html
def volumeData(id):
	volumeObject = open('%s%s' % (tmpPath, str(id) + '.txt'),'r').read()
	SharesTraded = ''.join(re.findall(r"SharesTraded:</td><td>[0-9,]+", ''.join(volumeObject.split())))
	Volume = ''.join(re.findall(r"Today'sVolume:</td><td>[0-9,]+", ''.join(volumeObject.split())))
	TotalShares = ''.join(re.findall(r"TotalShares:</td><td>[0-9,]+", ''.join(volumeObject.split())))
	return tuple(''.join(re.findall(r"\d+", i)) for i in [SharesTraded, Volume, TotalShares])


# this function takes care of database inserts and 
def marketData(connection, market):
	dataObject = json.load(open('%s%s' % (tmpPath, market + 'exchangeName.json'),'r'))
	contracts = dataObject['Contracts']
	for i in contracts:
		# insert the metadata for each contract
		cursor = connection.cursor()
		query1 = "INSERT IGNORE INTO contract_%s " % market
		cursor = connection.cursor()
		query1 = query1 + "(`ID`,`DateEnd`,`url`,`Name`,`LongName`,`ShortName`,`TickerSymbol`,`Status`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
		row = (i['ID'], i['DateEnd'], i['URL'], i['Name'], i['LongName'], i['ShortName'], i['TickerSymbol'], i['Status'])
		cursor.execute(query1, row)
		connection.commit()
		# now insert the actual pricing and volume data
		cursor = connection.cursor()
		query2 = "INSERT INTO price_%s " % market
		cursor = connection.cursor()
		query2 = query2 + "(`contract_id`,`report_id`,`TickerSymbol`,`LastTradePrice`, `BestBuyYesCost`, `BestBuyNoCost`, \
							`BestSellYesCost`, `BestSellNoCost`, `LastClosePrice`, `SharesTraded`, `Volume`, `TotalShares`) \
							VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		row = (i['ID'], report_id, i['TickerSymbol'], i['LastTradePrice'], i['BestBuyYesCost'], i['BestBuyNoCost'], \
				i['BestSellYesCost'], i['BestSellNoCost'], i['LastClosePrice']) + volumeData(i['ID'])
		row = tuple(0.0 if x == None else x for x in row)
		cursor.execute(query2, row)
		connection.commit()


if __name__ == "__main__":
	market = sys.argv[1]
	set_algo_environment(connection, market)
	marketData(connection, market)
	connection.close()
