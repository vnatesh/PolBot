import lxml.html
import sys
from bs4 import BeautifulSoup
import re
import json
from sqlConn import *

# This file is basically a dumping ground for regex extraction of various attributes from html/json/text files. Its functionality
# could be replaced by awk/sed and embedded directly in the shell code, eliminating the need for this file

# uses regex to isolate the _RequestVerificationToken from the raw html of predictit login, confirm trade, or submit trade pages
# uses regex to isolate the price from raw html of a buyYes, sellYes, buyNo, and sellNo contract

elementType = sys.argv[1]
tmpPath = "~/PolBot/tmp/"

if elementType == 'token':
	token_type = sys.argv[2]
	html =  open('%s%sHtml.txt' % (tmpPath,token_type)).read()
	html = BeautifulSoup(html, "html5lib")
	if token_type == 'login':
		data = html.find_all("form", {"action" : "/Account/LogIn"})
		formData = str(data[1])
		tree = lxml.html.fromstring(formData)
		token = tree.form_values()[0][1]
	elif token_type == 'confirm':
		data = html.find_all("form", {"action" : "/Trade/ConfirmTrade"})
		formData = str(data[0])
		tree = lxml.html.fromstring(formData)
		token = tree.form_values()[0][1]
	elif token_type == 'submit':
		data = html.find_all("form", {"action" : "/Trade/SubmitTrade"})
		formData = str(data[0])
		tree = lxml.html.fromstring(formData)
		token = tree.form_values()[0][1]
	sys.exit(token)


elif elementType == 'price':
	price_type = sys.argv[2]
	html = open('%sconfirmHtml.txt' % tmpPath).read()
	if price_type == '1' or price_type == '0':
		price = float(re.findall(r"var bestBuyOffer = '\d+[.]\d+", html)[0][-4:])
	elif price_type == '3' or price_type == '2':
		price = float(re.findall(r"var bestSellOffer = '\d+[.]\d+", html)[0][-4:])
	sys.exit(price)


elif elementType == 'contractUrl':
	contractId = sys.argv[2]
	cursor = connection.cursor()
	cursor.execute("SELECT url FROM contract_marketName WHERE ID = %s" % contractId)
	contractUrl = cursor.fetchone().values()[0]
	sys.exit(contractUrl)


elif elementType == 'volumeUrl':
	dataObject = json.load(open('%s' % (tmpPath + 'marketNameExchangeName.json'),'r'))
	contracts = dataObject['Contracts']
	volumeList=[]
	for i in contracts:
		volumeList.append(str(i['URL']))
		volumeList.append(str(i['ID'])+".txt")
	print volumeList
