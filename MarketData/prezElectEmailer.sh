# runs every 6 hours

cd ~
chmod -R 777 PolBot
cd PolBot/R
./bettingMarketsGraph.R
./rcpGraph.R

uuencode marketReport.jpeg marketReport.jpeg | mail -s '6 Hour Market Report' "email1 , email2"
uuencode rcpMarketReport.jpeg rcpMarketReport.jpeg | mail -s '6 Hour RCP Market Report' "email1 , email2"

