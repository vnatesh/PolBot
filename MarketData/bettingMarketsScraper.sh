# # runs every hour
# # to edit the cron: EDITOR=/usr/bin/nano sudo crontab -u vikasnatesh -e
# To view all crons: crontab -l
cd ~/Documents/Python/
chmod -R 777 cciPolitics
cd cciPolitics/tmp
source ~/Documents/Python/cciPolitics/bash/scrapeLib.sh

# array of market websites to scrape...they are arranged in a specific order, so as to prevent sequential scraping patterns from the same site
marketList=("https://www.marketDataApiPlaceHolder.com" "usPrezMarket.json" 
"https://www.predictious.com/politics/democratic-presidential-primaries-2016" "demNomPredictious.txt" 
"http://www.paddypower.com/bet/politics/other-politics/us-politics?ev_oc_grp_ids=481890" "gopNomPaddypower.txt" 
"http://www.oddschecker.com/politics/us-politics/us-presidential-election-2016/democrat-candidate" "demNomOddsChecker.txt" 
"https://www.predictious.com/politics/republican-presidential-primaries-2016" "gopNomPredictious.txt" 
"https://www.marketDataApiPlaceHolder.com" "demNomMarket.json" 
"http://www.oddschecker.com/politics/us-politics/us-presidential-election-2016/winner" "usPrezOddsChecker.txt" 
"http://www.paddypower.com/bet/politics/other-politics/us-politics?ev_oc_grp_ids=791149" "usPrezPaddypower.txt" 
"https://www.marketDataApiPlaceHolder.com" "gopNomMarket.json" 
"http://www.paddypower.com/bet/politics/other-politics/us-politics?ev_oc_grp_ids=482040" "demNomPaddypower.txt" 
"https://www.predictious.com/politics/us-presidential-election-2016" "usPrezPredictious.txt" 
"http://www.oddschecker.com/politics/us-politics/us-presidential-election-2016/republican-candidate" "gopNomOddsChecker.txt"
)

# get data from the respective betting websites
sleepTime=$[ ( $RANDOM % 1000 )  + 1 ]
sleep $sleepTime
curlMarkets $marketList
python /Users/vikasnatesh/Documents/Python/cciPolitics/bettingMarketsScraper.py
