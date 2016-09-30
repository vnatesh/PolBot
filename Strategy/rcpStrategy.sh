# # runs every 3 minutes plus a random number of seconds between 1 and 120
# # to edit the cron: EDITOR=/usr/bin/nano sudo crontab -u username -e
# To view all crons: crontab -l
cd ~
chmod -R 777 PolBot
cd Polbot/tmp
source ~/PolBot/MarketData/scrapeLib.sh

# contract ends every Friday and new one starts...if the date isn't a friday, get the date of the next friday
if [ "$(date +"%a")" == 'Fri' ];  
        then contractDate=$(date "+%m%d%y"); 
else  contractDate=$(date -v+Friday "+%m%d%y"); 
fi

# set up the marketList array containing the link to scrape and the output file
a="https://www.exchangeName.org/api/$contractDate"
marketList=($a "marketNameExchangeName.json" 
        "http://www.realclearpolitics.com/epolls/other/-1044.html" "RealClearPolitics.txt"
        "www.ipsos-na.com/news-polls/pressrelease.aspx?id=" "Reuters.txt"
        "http://www.gallup.com/poll/113980.aspx" "Gallup.txt")

# delay processing for a random number of seconds between 1 and 30
sleepTime=$[ ( $RANDOM % 30 )  + 1 ]
sleep $sleepTime
curlMarkets $marketList
python ~/PolBot/Strategy/rcpStrategy.py
cd ..




