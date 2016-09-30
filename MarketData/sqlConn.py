import pymysql.cursors
import pymysql

connection = pymysql.connect(host='localhost',
	user=username,
	password=password,
	db='politics',
	cursorclass=pymysql.cursors.DictCursor)


