#!/usr/bin/env python
import json
import re
import string
import pymysql
import pymysql.cursors
from bs4 import BeautifulSoup
tmpPath = "~/PolBot/tmp/"


# For now, we are only tracking the US presidential election, the GOP nomination, and the DEM nomination...
# These three securities are present in all exchanges as opposed to the individual state primary securities
# which are only covered by exchangeName, paddypower, and oddschecker

# Note: 'back' is the same as bid or buy...'lay' is the same as ask or sell

# Our derived prices for each candiate is based on implied probability...we should aim to only include markets with
# both bid and ask prices

# First, we convert the bid/ask market prices (different format for every market) to fractional odds. As long 
# as the spread between the Bid and Ask prices is less than 15 percentage points, we take the average of the two. 
# Otherwise, we use the price of the most recent trade (in exchangeName) or the average of the two (predictious)
# Percentage spread b/w back and lay is calculated as:
#           100 * (lay - back) / lay

# Paddypower and oddschecker are not liquid markets and only contain back/bid/buy prices but no sell. In these cases, we only use the back price
# to compute implied probability...this is a our best estimation :(

# ...finally, our derived prices (implied probabilities) are normalized over all candidates to eliminate 
# the effect that the vig has on implied probability 

# The 15% bid/ask divergence system is not arbitrary...this is the same methodology that predictwise uses

# ----------------------------------------------------------------------------------

# Establish the mysql connection
# to enter mysql from terminal, cd /usr/local/mysql/bin and do ./mysql -u root -p 
# You can run mysql commands from terminal: ./mysql -u root -p -e 'show databases;'

connection = pymysql.connect(host='localhost',
    user='username',
    password='password',
    db='politics',
    cursorclass=pymysql.cursors.DictCursor)

# Get the last report id and increment it by 1 for manual insertion in mySQL later on

cursor = connection.cursor()
cursor.execute("select max(report_id) from politics.report_politics")
report_id = cursor.fetchone().values()[0]
if report_id ==None: 
    report_id = 1
else: 
    report_id = report_id+1


# add the report id to mySQL table report_politics

cursor = connection.cursor()
sql = "INSERT INTO `report_politics` (`report_id`) VALUES (%s)"
cursor.execute(sql, (report_id))
connection.commit()


# Get markets
cursor = connection.cursor()
cursor.execute("select * from markets")
allMarkets = cursor.fetchall()
allMarkets = {i.values()[1] : i.values()[0] for i in allMarkets}
# Get candidate names
cursor = connection.cursor()
cursor.execute("select * from candidates")
allCandidates = cursor.fetchall()
allCandidates = {i.values()[1] : i.values()[0] for i in allCandidates}
# Get securities 
cursor = connection.cursor()
cursor.execute("select * from securities")
allSecurities = cursor.fetchall()
allSecurities = {i.values()[1] : i.values()[0] for i in allSecurities}


# ----------------------------------------------------------------------------------
# Some Helper Functions

def normalize(odds):
    return [i/sum(odds) for i in odds]

               
def calcOdds(back, lay, market, mostRecent):
    diff = [(lay[i] - back[i]) / lay[i] for i in xrange(len(names))]
    odds = []
    for i in xrange(len(diff)):
        if abs(diff[i]) > 0.15:
            if market == 'predictious':
                odds.append(0.5*(back[i]+lay[i]))
            else: odds.append(mostRecent[i])
        else:
            odds.append(0.5*(back[i]+lay[i]))
    return odds

# ----------------------------------------------------------------------------------

## PaddyPower Market

# All candiates are used in this market...there is only a back price available so it is used for the implied probability calculation...
# prices are normalized over all candiates to eliminate the effect of the 
# vig on odds, which allows us to obtain the true implied probabilities of winning for each candidate

securities = {'usPrez' : '%susPrezPaddypower.txt' % tmpPath,
              'gopNom' : '%sgopNomPaddypower.txt' % tmpPath,
              'demNom' : '%sdemNomPaddypower.txt' % tmpPath}

market = 'paddypower'
for sec in securities.keys():
    html = open(securities[sec]).read()
    html = BeautifulSoup(html, "html5lib")
    data = html.find_all("div", {"class" : "oddsTable oddsNonracing cf"})
    odds = [re.findall(r'\S+',i.text)[-1] for i in data]
    names= [re.findall(r'\S+',i.text)[:-1] for i in data]
    odds = [float(int(j[1]))/(int(j[0])+int(j[1])) for j in [i.split('/') for i in odds]]
    # normalize for the vig
    odds = [round(i,3) for i in normalize(odds)]

    names = map(str,map(string.join,names))
    cursor = connection.cursor()
    sql = "INSERT INTO `import_politics` (`report_id`,`market`,`security`,`candidate`,`price`) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql, [(report_id, allMarkets[market], allSecurities[sec], allCandidates[names[i]], odds[i]) for i in xrange(len(names))])
    connection.commit()


# ----------------------------------------------------------------------------------

# ## Predictious Market

securities = {'usPrez' : '%susPrezPredictious.txt' % tmpPath,
              'gopNom' : '%sgopNomPredictious.txt' % tmpPath,
              'demNom' : '%sdemNomPredictious.txt' % tmpPath}

market = 'predictious'
for sec in securities.keys():
    html = open(securities[sec]).read()
    html = ''.join(html.split())
    pattern = re.compile(r'<tr><td>\S+</a><ahref="https://www.predictious.com/politics\S+<pclass="pull-rightalertalert-successprice-container">Buyat<span>\S+<pclass="pull-rightalertalert-dangerprice-container">Sellat\S+</span></p></a><divclass="media-body"><h4class="media-heading"><ahref="https://www.predictious.com/politics')
    html = ''.join(re.findall(pattern, html))
    data = html.split("<tr><td>")[1:]

    back = []
    lay = []
    odds = []
    names = []
    mostRecent = []
    for i in data:
        patternBuy = re.compile(r'Buyat<span>\d+\S<small>\d+</small></span>')
        patternSell = re.compile(r'Sellat<span>\d+\S<small>\d+</small></span>')
        patternName = re.compile(r'leftthumbnail-wrapper"href="https://www.predictious.com/politics\S+><imgsrc')
        name = ' '.join(re.split('">',''.join(re.findall(r'2016/\S+>',''.join(re.findall(patternName,i)))).split('2016/')[1])[0].split('-')).title()
        priceBuy = ''.join(re.findall(r'[0-9,.]',''.join(re.findall(patternBuy,i))))
        priceSell = ''.join(re.findall(r'[0-9,.]',''.join(re.findall(patternSell,i))))
        if priceBuy != '' and priceSell != '':
            names.append(name)
            back.append(float(priceBuy)/10)
            lay.append(float(priceSell)/10)

    # apply the 15% rule
    odds = calcOdds(back,lay,market,mostRecent)
    # normalize for the vig
    odds = [round(i,3) for i in normalize(odds)]
    cursor = connection.cursor()
    sql = "INSERT INTO `import_politics` (`report_id`,`market`,`security`,`candidate`,`price`) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql, [(report_id, allMarkets[market], allSecurities[sec], allCandidates[names[i]], odds[i]) for i in xrange(len(names))])
    connection.commit()


# ----------------------------------------------------------------------------------
## OddsChecker Market

securities = {'usPrez' : '%susPrezOddsChecker.txt' % tmpPath,
              'gopNom' : '%sgopNomOddsChecker.txt' % tmpPath,
              'demNom' : '%sdemNomOddsChecker.txt' % tmpPath}

market = 'oddschecker'
for sec in securities.keys():
    html = open(securities[sec]).read()
    pattern = re.compile(r'\[\[(.*?)\]\]')
    data = ''.join(re.findall(pattern, html)).split('],[')
    names = [i.split('"')[1].split(' (')[0] for i in data]
    odds = []
    for i in data:
        a = map(int,i.split('"')[1].split(' (')[1][:-1].split('/'))
        odds.append(float(a[1]) / (a[0]+a[1]))

    names = [names[i] for i in xrange(len(odds)) if odds[i] < 1]
    odds = [odds[i] for i in xrange(len(odds)) if odds[i] < 1]

    odds = [round(i,3) for i in normalize(odds)]
    cursor = connection.cursor()
    sql = "INSERT INTO `import_politics` (`report_id`,`market`,`security`,`candidate`,`price`) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql, [(report_id, allMarkets[market], allSecurities[sec], allCandidates[names[i]], odds[i]) for i in xrange(len(names))])
    connection.commit()


# ----------------------------------------------------------------------------------

securities = {'usPrez' : '%susPrezexchangeName.json' % tmpPath,
              'gopNom' : '%sgopNomexchangeName.json' % tmpPath,
              'demNom' : '%sdemNomexchangeName.json' % tmpPath}

# As long as the spread between the Bid and Ask prices is less than 15 points, we take the average of the two. 
# Otherwise, we use the price of the most recent trade
market = 'exchangeName'
for sec in securities.keys():
    dataObject = json.load(open(securities[sec],'r'))
    names = [dataObject['Contracts'][i]['Name'] for i in xrange(len(dataObject['Contracts']))]
    back =  [dataObject['Contracts'][i]['BestBuyYesCost'] for i in xrange(len(dataObject['Contracts']))]
    lay =  [dataObject['Contracts'][i]['BestSellYesCost'] for i in xrange(len(dataObject['Contracts']))]
    mostRecent = [dataObject['Contracts'][i]['LastTradePrice'] for i in xrange(len(dataObject['Contracts']))]

    # All candiates have a back (I hope) but lay is absent for some candidates...
    # we remove those cadidates from consideration since we need both back and lay prices in this market
    # to account for market liquidity
    names = [names[i] for i in xrange(len(lay)) if lay[i] is not None]
    back = [back[i] for i in xrange(len(lay)) if lay[i] is not None]
    mostRecent = [mostRecent[i] for i in xrange(len(lay)) if lay[i] is not None]
    lay = [i for i in lay if i is not None]  
    odds = calcOdds(back,lay,market,mostRecent)

    # line below corrects for the vig
    odds = [round(i,3) for i in normalize(odds)]
    cursor = connection.cursor()
    sql = "INSERT INTO `import_politics` (`report_id`,`market`,`security`,`candidate`,`price`) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(sql, [(report_id, allMarkets[market], allSecurities[sec], allCandidates[names[i]], odds[i]) for i in xrange(len(names))])
    connection.commit()


# ----------------------------------------------------------------------------------

# close the mysql connection
connection.close()


