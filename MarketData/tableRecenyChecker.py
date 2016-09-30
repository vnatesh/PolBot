import os
import sys
import datetime
from sqlConn import *

# checks to see if the timestamp for the latest report_id in the price table is within 120 seconds of the current time...if not, send an error email
# checks to see that new volume data has been added
def recencyChecker(connection, market):
	cursor = connection.cursor()
	checkQuery1 = "SELECT r.timestamp FROM report_%s r \
				  INNER JOIN price_%s p on r.report_id = p.report_id \
				  ORDER BY p.report_id DESC LIMIT 1" % (market, market)
	cursor.execute(checkQuery1)
	timestamp = cursor.fetchone().values()[0]
	current = datetime.datetime.now()
	#
	cursor = connection.cursor()
	checkQuery2 = "SELECT SharesTraded, Volume, TotalShares FROM price_%s ORDER BY report_id DESC LIMIT 1" % market
	cursor.execute(checkQuery2)
	volumeCols = cursor.fetchone().values()
	#
	if (current - timestamp).seconds > 120 or any((i == None for i in volumeCols)):
		os.system('''echo 'There was a price_%s data writing error' | mail -s 'scraping error' "email1"''' % market)


if __name__ == "__main__":
	markets = sys.argv[1:]
	for market in markets:
		recencyChecker(connection, market)
	connection.close()

