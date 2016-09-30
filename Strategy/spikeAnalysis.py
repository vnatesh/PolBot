import matplotlib.pyplot as plt
from sqlConn import *
import datetime


# this version of spikeAnalysis uses both volume and price monotonicty


'''

These functions are used to backtest the algo strategy

    connnection - a pymysql connection to the politics databases
    spike - intended profit per share bought
    conf - int of consecutive time points to use for signal characterization
    buyLimit - minimum necessary price to buy at
    sellLimit - minimum necessary price to sell at
    concPrice - boolean to indicate whether to capture signals conditional on them being concave up in price
    concVolume - boolean to indicate whether to capture signals conditional on them being concave up in volume 
    verbose - verbosity level in ['v', 'vv']
'''

def spikeAnalysis(connection, spike, conf, buyLimit, sellLimit, concPrice = False, concVolume = False, verbose = ''):
    cursor = connection.cursor()
    cursor.execute("select p.report_id, p.BestBuyYesCost priceBuy, p.BestSellYesCost priceSell, p.Volume volume, c.ID security, r.timestamp \
                    from price_marketName p \
                    inner join contract_marketName c on p.contract_id = c.ID \
                    inner join report_marketName r on p.report_id = r.report_id \
                    WHERE DAYNAME(r.timestamp) NOT IN ('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday') \
                    AND HOUR(r.timestamp) >= 5")
    data = cursor.fetchall()
    contracts = set(i['security'] for i in data if i['security'] != 'marketName')
    totalProfit = 0
    contractProfits = {}
    for contract in contracts:
        spikes = []
        contractData = [[i['timestamp'], float(i['priceBuy']), float(i['priceSell']), i['volume']] \
                        for i in data if i['security'] == contract and i['volume'] >=0]
        #
        # Characterize the spikes by monotonicity and/or concavity
        for i in xrange(len(contractData) - conf):
            timeDiffs = [(contractData[i+c][0] - contractData[i+c-1][0]).seconds / 60.0 for c in xrange(1,conf+1)]
            checkTimes = all([t<=1.5 for t in timeDiffs])
            #           
            priceDiffs = [contractData[i+c][1] - contractData[i+c-1][1] for c in xrange(1,conf+1)]
            if concPrice == True:
                checkPrice = all(x<=y for x, y in zip(priceDiffs, priceDiffs[1:])) and all(p > 0 for p in priceDiffs)
            else:
                checkPrice = all(p > 0 for p in priceDiffs)
            #
            volDiffs = [contractData[i+c][3] - contractData[i+c-1][3] for c in xrange(1,conf+1)]
            if concVolume == True:
                checkVolume = all(x<=y for x, y in zip(volDiffs, volDiffs[1:])) and  all(v >= 0 for v in volDiffs)
            else:
                checkVolume = all(v >= 0 for v in volDiffs)
            #
            if all([checkTimes, checkPrice, checkVolume]):
                spikes.append(i+conf)
        #
        # remove any spikes where the buyPrice is less than the set buyLimit
        spikes = [ind for ind in spikes if contractData[ind][1] >= buyLimit]
        #
        # calculate the profit/loss obtained by waiting for priceSell to get up to (priceBuy + spike), and then selling
        success = dict()
        failure = dict()
        for ind in spikes:
            for j in xrange(ind + 1, len(contractData)):
                profit = contractData[j][2] - contractData[ind][1]
                if contractData[j][2] <= sellLimit:
                    failure[ind] = (j, profit)
                    break
                #
                if profit >= spike:
                    success[ind] = (j ,profit)
                    break
        #
        diff = set(spikes) - set(success.keys() + failure.keys())
        for i in diff:
            if contractData[-1][2] > contractData[i][1]:
                success[i] = (len(contractData)-1, contractData[-1][2] - contractData[i][1])
            else: failure[i] = (len(contractData)-1, sellLimit - contractData[i][1])
        #
        contractProfit = sum([i[1] for i in failure.values()]) + sum([i[1] for i in success.values()])
        contractProfits[contract] = contractProfit
        totalProfit += contractProfit
        if verbose == 'vv':
            print contract
            print spikes
            print success
            print diff
            print failure
            print contractData[-1][2]
            print len(contractData)
            print "\n\n"
    if verbose in ['v', 'vv']:
        for i in sorted(contractProfits.keys()):
            print i, ': ', contractProfits[i]
    return totalProfit




'''

    this version of spikeAnalysis uses only price data

    connnection - a pymsql connection to the politics databases
    spike - intended profit 
    conf - int of consecutive time points to use for signal characterization
    buyFloor - minimum necessary price to buy at
    buyCeiling - maximum price allowed for a buy
    sellLimit - price at which to sell contract
    concPrice - boolean to indicate whether to capture signals conditional on them being concave up in price
    verbose - verbosity level in ['v', 'vv']

'''



cursor = connection.cursor()
cursor.execute("SELECT p.report_id, p.BestBuyYesCost priceBuy, p.BestSellYesCost priceSell, c.ID security, r.timestamp \
                FROM price_marketName p \
                INNER JOIN contract_marketName c ON p.contract_id = c.ID \
                INNER JOIN report_marketName r ON p.report_id = r.report_id \
                WHERE DAYNAME(r.timestamp) NOT IN ('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday') \
                AND HOUR(r.timestamp) >= 5")
data = cursor.fetchall()


def spikeAnalysis(data, spike, conf, buyFloor, buyCeiling, sellLimit, concPrice = False, returnDistro = False, verbose = ''):
    contracts = set(i['security'] for i in data if i['security'] != 'marketName')
    totalProfit = 0
    contractProfits = {}
    master = []
    totalBuy = []
    for contract in contracts:
        spikes = []
        contractData = [[i['timestamp'], float(i['priceBuy']), float(i['priceSell'])] \
                        for i in data if i['security'] == contract]
        #
        # Characterize the spikes by monotonicity and/or concavity
        for i in xrange(len(contractData) - conf):
            timeDiffs = [(contractData[i+c][0] - contractData[i+c-1][0]).seconds / 60.0 for c in xrange(1,conf+1)]
            checkTimes = all([t<=1.5 for t in timeDiffs])
            #           
            priceDiffs = [contractData[i+c][1] - contractData[i+c-1][1] for c in xrange(1,conf+1)]
            if concPrice == True:
                checkPrice = all(x<=y for x, y in zip(priceDiffs, priceDiffs[1:])) and all(p > 0 for p in priceDiffs)
            else:
                checkPrice = all(p > 0 for p in priceDiffs)
            #
            if all([checkTimes, checkPrice]):
                spikes.append(i+conf)
        #
        # only use spikes where the buy price is between the buyFloor and buyCeiling
        spikes = [ind for ind in spikes if buyFloor <= contractData[ind][1] <= buyCeiling]
        contractQuantity = [contractData[buy][1] for buy in spikes]
        totalBuy += contractQuantity
        #
        # calculate the profit/loss obtained by waiting for priceSell to get up to (priceBuy + spike), and then selling
        success = dict()
        failure = dict()
        for ind in spikes:
            for j in xrange(ind + 1, len(contractData)):
                profit = contractData[j][2] - contractData[ind][1]
                if contractData[j][2] <= sellLimit:
                    failure[ind] = (j, profit)
                    break
                #
                if profit >= spike:
                    success[ind] = (j ,profit)
                    break
        #
        diff = set(spikes) - set(success.keys() + failure.keys())
        for i in diff:
            if contractData[-1][2] > contractData[i][1]:
                success[i] = (len(contractData)-1, contractData[-1][2] - contractData[i][1])
            else: failure[i] = (len(contractData)-1, sellLimit - contractData[i][1])
        #
        contractProfit = sum([i[1] for i in failure.values()]) + sum([i[1] for i in success.values()])
        contractProfits[contract] = contractProfit
        totalProfit += contractProfit
        #
        if returnDistro == True:
            for i in failure.values() + success.values():
                master.append(i[1])
        #
        if verbose == 'vv':
            print contract
            print spikes
            print success
            print diff
            print failure
            print contractData[-1][2]
            print len(contractData)
            print "\n\n"
    if verbose in ['v', 'vv']:
        print 'contract', '  ', 'profit'
        for i in sorted(contractProfits.keys()):
            print i, '   :   ', contractProfits[i]
        print master
        print totalBuy
        print 'number of executions = ', len(totalBuy)
        print 'totalProfit = ', totalProfit
        print 'totalBuy = ' , sum(totalBuy)
        print 'percent return = ', (totalProfit / sum(totalBuy)) * 100, '%'
    return (len(totalBuy), totalProfit, sum(totalBuy), totalProfit / sum(totalBuy))
