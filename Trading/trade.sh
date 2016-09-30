#!/usr/bin/env bash

##### This is the core trading function that allows for automated trading directly from the terminal or any other script
##### The 'trade' function can be used to execute any type of order (buy yes, sell yes. buy no, sell no) on any contract in any
##### open market i.e. it is a ubiquitous, generalized trading function. One could theorteically set up a script in another
##### language that calls this function in some algorithmic/patterned way based on analysis of some data (see Strategy directory)
##### The trade function takes 3 inputs:
			# contract ID (an integer unique for every 'security' in the PolBot model)
			# tradeType (an integer representing buy yes, buy no, sell yes, or sell no)
			# quantitiy (an integer number of shares)
##### examples:   $ trade 3057 1 10  (buyYes 10 shares of contract 3057)
#####			  $ trade 3166 3 4   (sellYes 3 shares of contract 3166)
##### 0 : buyNo, 	2 : sellNo
# ******* NOTE ******* Currently only supports tradeTypes 1 (buyYes) and 3 (sellYes)

# trade() {

# set the PATH variable so we can use python modules like lxml and requests from the canopy distribution
PATH=/Users/userName/Library/Enthought/Canopy_64bit/User/bin:/Library/Frameworks/Python.framework/Versions/2.7/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# set the input variables
contract=$1
tradeType=$2
quantity=$3

# cd into the project tmp directory
cd ~
chmod -R 777 PolBot
cd PolBot/tmp
source ~/PolBot/MarketData/scrapeLib.sh

# create a tag that identifies the trade, append it to filenames of all files created during the execution
tradeTag=${contract}_${tradeType}_${quantity}_$(date +%Y-%m-%d:%H:%M:%S).txt

#### First we automate the exchange Login

# Log into the exchange and save the login cookie
LOGIN_COOKIES=loginCookies_${tradeTag}
USER_AGENT=$(randArrayElement "userAgentList[@]")
HEADER='referer : https://www.exchangeName.org/Account/SignIn'
LOGIN_HTML=loginHtml_${tradeTag}
SIGNIN_URL='https://www.exchangeName.org/Account/SignIn'
LOGIN_URL='https://www.exchangeName.org/Account/LogIn'

curl $SIGNIN_URL --cookie-jar $LOGIN_COOKIES --output $LOGIN_HTML --user-agent $USER_AGENT
a="__RequestVerificationToken="
b=$(python ~/PolBot/Trading/tradeRegex.py token login ${tradeTag} 2>&1)
c="&ReturnUrl=&Email=email@email.com&Password=password&RememberMe=false&X-Requested-With=XMLHttpRequest"
LOGIN_POST_DATA="$a$b$c"
USER_AGENT=$(randArrayElement "userAgentList[@]")

curl $LOGIN_URL --cookie $LOGIN_COOKIES --cookie-jar $LOGIN_COOKIES --data $LOGIN_POST_DATA --header $HEADER --user-agent $USER_AGENT

# you can use the curl below to confirm whether the login succeeded...it directs you to your homepage with balance etc
# curl --cookie $LOGIN_COOKIES 'https://www.exchangeName.org/Profile/MyShares' --user-agent $USER_AGENT


##### Automated trade for a given contract ID and tradeType (buy/sell, yes/no)

CONFIRM_COOKIES=confirmCookies_${tradeTag}
USER_AGENT=$(randArrayElement "userAgentList[@]")
CONFIRM_HTML=confirmHtml_${tradeTag}

if [ ${tradeType} == 1 ];  
	then LOAD_URL="https://www.exchangeName.org/Trade/LoadLong?contractId=${contract}"; 
elif [ ${tradeType} == 3 ];
	then LOAD_URL="https://www.exchangeName.org/Trade/LoadSellLong?contractId=${contract}";
elif [ ${tradeType} == 0 ];
	then LOAD_URL="https://www.exchangeName.org/Trade/LoadShort?contractId=${contract}";
elif [ ${tradeType} == 2 ];
	then LOAD_URL="https://www.exchangeName.org/Trade/LoadSellShort?contractId=${contract}";
fi

CONFIRM_URL='https://www.exchangeName.org/Trade/ConfirmTrade'
SUBMIT_URL="https://www.exchangeName.org/Trade/SubmitTrade"

# use the loginCookies (we obtained on login) to load the contract we want to trade. Save output to a file to extract the confirmToken
curl $LOAD_URL --cookie $LOGIN_COOKIES --cookie-jar $CONFIRM_COOKIES --output $CONFIRM_HTML --user-agent $USER_AGENT

# extract the confirmToken and price from the confirmHtml to use in the next curl...price is extracted from here
a='__RequestVerificationToken='
b=$(python ~/PolBot/Trading/tradeRegex.py token confirm ${tradeTag} 2>&1)
price=$(python ~/PolBot/Trading/tradeRegex.py price ${tradeType} ${tradeTag} 2>&1)
price_new=$(awk "BEGIN {printf \"%.0f\n\", ${price}*100}")  # convert price to cents from dollars
c="&ContractId=${contract}&TradeType=${tradeType}&Quantity=${quantity}&PricePerShare=${price_new}"
d='&X-Requested-With=XMLHttpRequest'
CONFIRM_POST_DATA="$a$b$c$d"


# Params for confirming the trade through curl
SUBMIT_COOKIES=submitCookies_${tradeTag}
USER_AGENT=$(randArrayElement "userAgentList[@]")
REFERER_URL=$(python ~/PolBot/Trading/tradeRegex.py contractUrl ${contract} ${tradeTag} 2>&1)
HEADER="referer : ${REFERER_URL}"

SUBMIT_HTML=submitHtml_${tradeTag}

# use the confirmToken and confirmCookies to confirm the trade 
curl $CONFIRM_URL --cookie $CONFIRM_COOKIES --cookie-jar $SUBMIT_COOKIES --data $CONFIRM_POST_DATA --header $HEADER --output $SUBMIT_HTML --user-agent $USER_AGENT

# extract the submitToken from the html to use in the next curl...use the price in the form data
a='__RequestVerificationToken='
b=$(python ~/PolBot/Trading/tradeRegex.py token submit ${tradeTag} 2>&1)
c="&BuySellViewModel.TradeType=${tradeType}&BuySellViewModel.Quantity=${quantity}&BuySellViewModel.ContractId=${contract}&BuySellViewModel.PricePerShare=${price}&X-Requested-With=XMLHttpRequest"
SUBMIT_POST_DATA="$a$b$c"

# Params for submitting the trade through curl
USER_AGENT=$(randArrayElement "userAgentList[@]")
RESULT_HTML=resultHtml_${tradeTag}

# finally, submit the trade
curl $SUBMIT_URL --cookie $SUBMIT_COOKIES --data $SUBMIT_POST_DATA --header $HEADER --output $RESULT_HTML --user-agent $USER_AGENT

# remove extraneous html and cookie files from the directory
rm $CONFIRM_COOKIES $CONFIRM_HTML $LOGIN_COOKIES $LOGIN_HTML $SUBMIT_COOKIES $SUBMIT_HTML

# check to see if the trade executed successfully. If it succeeded, create a tmp file with the price in it
resultContract=$(python ~/PolBot/Trading/tradeRegex.py result contract ${RESULT_HTML} 2>&1)
resultQuantity=$(python ~/PolBot/Trading/tradeRegex.py result quantity ${RESULT_HTML} 2>&1)
resultPrice=$(python ~/PolBot/Trading/tradeRegex.py result price ${RESULT_HTML} 2>&1)

if [ ${resultContract} == ${contract}  ] &&  [ ${resultQuantity} == ${quantity}  ]; then
	 echo $resultPrice > success_${contract}_${tradeType}_${quantity}.txt
fi

# check to see if the trade was properly executed...look at the resultHtml.txt file and parse the contract, sell price, and quantity out
# if the parsed (contract,price,quantity) values are the same as those for the input of the trade function:
#	touch success_${contract}_${tradeType}_${quantity}.txt

# }
