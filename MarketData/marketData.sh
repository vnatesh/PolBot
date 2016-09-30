# # runs every 1 minutes plus a random number of seconds between 1 and 30
# # to edit the cron: EDITOR=/usr/bin/nano sudo crontab -u username -e
# To view all crons: crontab -l
cd ~
chmod -R 777 PolBot
cd PolBot/tmp
source ~/PolBot/MarketData/scrapeLib.sh

# contract ends every Friday and new one starts...if the date isn't a friday, get the date of the next friday
if [ "$(date +"%a")" == 'Fri' ];  
	then contractDate=$(date "+%m%d%y"); 
else  contractDate=$(date -v+Friday "+%m%d%y"); 
fi

# set up the marketList array containing the link to scrape and the output file
a="https://www.marketApiPlaceHolder.com/$contractDate"
marketList=($a "marketNameExchangeName.json")

# delay processing for a random number of seconds between 1 and 30
sleepTime=$[ ( $RANDOM % 30 )  + 1 ]
sleep $sleepTime

curlMarkets ${marketList[@]}

# set up the volumeList array containing volume data links to scrape and the output file (contract id)
volumeList=($(python ~/PolBot/MarketData/getElement.py volumeUrl  | tr -d '[],'))
volumeList=("${volumeList[@]//\"/}")
volumeList=("${volumeList[@]//\'/}")
curlMarkets ${volumeList[@]}

# run the scraping engine for the pertinent markets 
python ~/PolBot/MarketData/scrapingUtil.py 'marketName'
rm marketNameExchangeName.json
ls | grep -E '^[0-9]+.txt' | xargs rm
cd ..

