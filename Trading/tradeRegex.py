import lxml.html
import sys
from bs4 import BeautifulSoup
import re
import json
from sqlConn import *


elementType = sys.argv[1]
tmpPath = "~/PolBot/tmp/"

if elementType == 'token':
	token_type = sys.argv[2]
	tradeTag = sys.argv[3]
	html =  open('%s%sHtml_%s' % (tmpPath, token_type, tradeTag)).read()
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
	tradeTag = sys.argv[3]
	html = open('%sconfirmHtml_%s' % (tmpPath, tradeTag)).read()
	if price_type == '1' or price_type == '0':
		price = float(re.findall(r"var bestBuyOffer = '\d+[.]\d+", html)[0][-4:])
	elif price_type == '3' or price_type == '2':
		price = float(re.findall(r"var bestSellOffer = '\d+[.]\d+", html)[0][-4:])
	sys.exit(price)


elif elementType == 'result':
	resultType = sys.argv[2]
	resultFile = sys.argv[3]
	html = open('%s%s' % (tmpPath, resultFile)).read()
	if resultType == 'contract':
		result = ''.join(re.findall(r"\d+",''.join(re.findall(r"Contract/\d+",html))))
	elif resultType == 'quantity':
		result = ''.join(re.findall(r"\d+",''.join(re.findall(r"label.*\d+",html))))
	elif resultType == 'price':
		result = ''.join(re.findall(r"\d+",''.join(re.findall(r"\d+<span style",html))))
	sys.exit(result)



