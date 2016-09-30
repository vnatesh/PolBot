#!/usr/bin/env python
import time
from tradingUtil import *
# from testConn import *


def buyCheck(data, contract, conf, buyFloor, buyCeiling, concPrice = False):
    contractData = [[i['timestamp'], float(i['priceBuy'])] \
                                    for i in data if i['security'] == contract]
    #
    # Characterize the spikes by monotonicity and/or concavity
    timeDiffs = [(contractData[c][0] - contractData[c-1][0]).seconds / 60.0 for c in xrange(1,conf+1)]
    checkTimes = all([t<=1.5 for t in timeDiffs])
    #
    priceDiffs = [contractData[c][1] - contractData[c-1][1] for c in xrange(1,conf+1)]
    if concPrice == True:
            checkPrice = all(x<=y for x, y in zip(priceDiffs, priceDiffs[1:])) and all(p > 0 for p in priceDiffs)
    else:
            checkPrice = all(p > 0 for p in priceDiffs)
    if all([checkTimes, checkPrice]) and buyFloor <= contractData[-1][1] <= buyCeiling:
        return True


def algoStratBuy(contract):
    if buyCheck(data, contract, conf, buyFloor, buyCeiling):
        trade(connection, contract, 'buyYes', quantity = 2, market = 'marketName')


if __name__ == '__main__':
        (conf, buyFloor, buyCeiling) = (1, 0.23, 0.30)
        data = pullData(connection, conf, 'marketName')
        if len(data) > 0:
                contracts = set(i['security'] for i in data)
                map(algoStratBuy, contracts)
        connection.close()
        print len(data)
        time.sleep(14)
