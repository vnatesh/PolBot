import subprocess
import shlex
import os
import re
import time
from sqlConn import *
from dateutil.parser import parse


'''

Pull in 'conf' rows of pricing data from a specific market table

'''

def pullData(connection, conf, market):
    cursor = connection.cursor()
    cursor.execute("SELECT p.report_id, p.BestBuyYesCost priceBuy, p.BestSellYesCost priceSell, p.contract_id security, r.timestamp \
                    FROM price_%s p \
                    INNER JOIN report_%s r ON p.report_id = r.report_id \
                    WHERE DAYNAME(r.timestamp) NOT IN ('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday') \
                    AND HOUR(r.timestamp) >= 5 \
                    AND p.report_id >= (SELECT max(report_id) FROM price_%s) - %s \
                    ORDER by report_id ASC" % (market, market, market, conf))
    return cursor.fetchall()


'''

Pull in buys that haven't been sold yet

'''


def pullOpenBuyYes(connection, market):
	cursor = connection.cursor()
	cursor.execute("SELECT b.ID buyID, b.contract_id, b.buyYesPrice, b.quantity \
					FROM buyYes_%s b \
					LEFT JOIN tradeLink_%s s ON b.ID = s.source \
					WHERE s.source IS NULL" % (market, market))
	return cursor.fetchall()

'''

Pull in trades from a specific market and time frame

'''

def pullTrades(connection, start_dt, end_dt, market):
	cursor = connection.cursor()
	cursor.execute("SELECT c.tickerSymbol contract, b.buyYesPrice, b.quantity, b.timestamp time_buy s.sellYesPrice, s.quantity, s.timestamp time_sell \
					FROM buyYes_%s b \
					INNER JOIN contract_%s c ON b.contract_id = c.ID \
					LEFT JOIN sellYes_%s s ON b.ID = s.buy_origin \
					WHERE DATE(b.timestamp) >= %s \
					AND DATE(b.timestamp) BETWEEN %s AND %s   ") % (market, market, market, start_dt, end_dt)
	return cursor.fetchall()


'''

This function is a wrapper for the trade.sh script which executes a trade. It also records successfully executed trades in mysql. Unsuccessful
trades are reported via a text message alert 

'''
def trade(connection, contract, tradeType, quantity, market):
	tradeTypes = {'buyYes' : 1, 'sellYes' : 3}
	tradeTypeID = tradeTypes[tradeType]
	# execute the trade
	null_device = open(os.devnull, 'w')
	tradeCmd = shlex.split("./trade.sh %s %s %s > /dev/null 2>&1" % (contract, tradeTypeID, quantity))
	subprocess.call(tradeCmd, cwd = "~/PolBot/Trading", stdout=null_device, stderr = subprocess.STDOUT)
	# confirm that the trade executed successfully
	confirmTrade = "~/PolBot/tmp/success_%s_%s_%s.txt" % (contract, tradeTypeID, quantity)
	if os.path.exists(confirmTrade):
		# remove the file indicating success and record the trade  execution in mysql
		price = float(''.join(re.findall(r'\d+',open('%s' % confirmTrade).read()))) / 100
		os.remove(confirmTrade)
		cursor = connection.cursor()
		sql = "INSERT INTO `%s_%s`" % (tradeType, market) + "(`contract_id`, `%sPrice`, `quantity`)" % tradeType + "VALUES (%s, %s, %s)"
		cursor.execute(sql, (contract, price, quantity))
		connection.commit()
	else:
		# if it wasn't successful, send an alert
		os.system('''echo '%s %s shares of %s has failed' | mail -s 'trade error' "phoneNumber@vtext.com"''' % (tradeType, quantity, contract))


'''

generic state machine class

'''
class SM:
    def start(self):
        self.state = self.startState
    def step(self,inp):
        (s,o) = self.getNextSwitchState(self.state,inp)
        self.state = s
        return o
    def transduce(self,inputs):
        self.start()
        return [self.step(inp) for inp in inputs]
    def current_state(self):
        return self.state



# get the message content and datetime received of new switch messages sent to the mail server from a user phone

def getNewMessages(sender, mailDir):
	# use getmail to retrieve unopened mail
	null_device = open(os.devnull, 'w')
	subprocess.call('getmail', stdout=null_device)
	# find message content and datetime received
	mailList = []
	for i in os.listdir(mailDir):
	        with open("%s%s" % (mailDir, i), 'r') as mailFile:
	                text = mailFile.read()
	                if sender in text:
	                        lines = text.split('\n')
	                        mailList.append((lines[-4].strip(), parse(lines[3].strip())))
	        mailFile.close()
	return mailList


# find the last executed switch command from mysql

def getLastSwitch(connection, market):
	cursor = connection.cursor()
	cursor.execute("SELECT switchMessage FROM switch_%s ORDER BY ID DESC LIMIT 1" % market)
	return cursor.fetchone()['switchMessage']


'''

This function takes in a new switch command, executes it, and records the execution in mysql.
The switch command are:

	PolBot all on
	PolBot all off
	PolBot Buy on
	PolBot Buy off
	PolBot Sell on
	PolBot Sell off

'''

def switch(connection, newMessage, stratDir, market):
	null_device = open(os.devnull, 'w')
	newSwitch = str.split(newMessage)
	if newSwitch[2] == 'on':
	        if newSwitch[1] != 'all':
	                cmd =  shlex.split("./algo%s.sh" % newSwitch[1])
	                subprocess.Popen(cmd, cwd = stratDir, stdout=null_device)
	        else:
	                cmd1 =  shlex.split("./algoBuy.sh")
	                cmd2 =  shlex.split("./algoSell.sh")
	                subprocess.Popen(cmd1, cwd = stratDir, stdout=null_device)
	                subprocess.Popen(cmd2, cwd = stratDir, stdout=null_device)
	elif newSwitch[2] == 'off':
	        if newSwitch[1] in ['Buy', 'Sell']:
	                # shell = True is generally not reccomended but the chance of shell injection here is fairly low
	                # still, might wanna comvert this to a sequence of Popen pipes that communicate sequentially
	                cmd = '''ps -ax | grep algo%s | grep -v grep | awk '{print "kill -15 " $1}' | bash''' % newSwitch[1]
	                subprocess.call(cmd, shell = True)
	        else:
	                cmd1 = '''ps -ax | grep algoBuy | grep -v grep | awk '{print "kill -15 " $1}' | bash'''
	                cmd2 = '''ps -ax | grep algoSell | grep -v grep | awk '{print "kill -15 " $1}' | bash'''
	                subprocess.call(cmd1, shell = True)
	                subprocess.call(cmd2, shell = True)
	# insert new message into switch_market table
	cursor = connection.cursor()
	sql1 = "INSERT INTO switch_%s" % market
	sql2 = sql1 + "(`switchMessage`) VALUES (%s)"
	cursor.execute(sql2, (newMessage))
	connection.commit()


