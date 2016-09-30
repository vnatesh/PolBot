from scrapingUtil import *

# This script executes a simple event-driven strategy. Whenever an rcp average changes by at least 0.001, an email
# and text message is sent out, alerting the trader to buy/sell the relevant security. In addition, the strategy
# tracks reuters ad gallup polls and alerts the trader in a similar way. The decision is left up to the trader to actually execute the buy/sell
# on the exchange website. More polls may be tracked in order to create an up-to-date (or expected) rcp average, before the actual rcp
# average on the website changes. 

# setup environment variables allMarkets, allSecurities, and report_id
set_rcp_environment(connection)

# scrapes the polling websites, alerts scraping errors, alerts significant polling changes, and inserts scraped data into mysql
for i in approvalPollRegex.keys():
	for j in approvalPollRegex[i].keys():
		poll = approvalPoll(j, i,report_id)
		poll.parse()
		if poll.approvalRate != None:
			poll.alert()
			poll.insert()

# collect all the exchange pricing data in the specific market for graphical comparison to polling release events in R
getExchange('marketName','import_rcp', allSecurities, allMarkets)
connection.close()

