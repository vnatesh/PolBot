#!/usr/bin/env python

from tradingUtil import *
import time

# from testConn import *

if __name__ == '__main__':
    (conf, spike, sellLimit) = (0, 0.33, 0.01)
    openPositions = pullOpenBuyYes(connection, 'marketName')
    data = pullData(connection, conf, 'marketName')
    if len(data) > 0:
        for position in openPositions:
            sellPrice = [float(i['priceSell']) for i in data if i['security'] == position['contract_id']][0]
            numShares = position['quantity']
            if (sellPrice >= float(position['buyYesPrice']) + spike or sellPrice <= sellLimit) and sellPrice != 0:
                trade(connection, contract = position['contract_id'], tradeType = 'sellYes', quantity = numShares, market = 'marketName')
                #
                # link the buy and sell together
                cursor = connection.cursor()
                cursor.execute("SELECT ID from sellYes_marketName ORDER BY ID DESC LIMIT 1")
                sellID = cursor.fetchone()['ID']
                buyID = position['buyID']
                #
                cursor = connection.cursor()
                sql = "INSERT INTO `tradeLink_marketName` (`source`, `sink`) VALUES (%s, %s)"
                cursor.execute(sql, (buyID, sellID))
                connection.commit()
    connection.close()
    print len(data)
    time.sleep(14)


