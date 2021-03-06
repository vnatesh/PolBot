from tradingUtil import *

# this is run every 3 minutes and retrieves switch commands from a central mail via POP3

mailDir = "~/PolBot/mail/new/"
stratDir = "~/PolBot/Strategy/"
senderNumber = "phoneNumber"
market = 'marketName'
newMail = getNewMessages(senderNumber, mailDir)
if newMail != []:
                # find the latest message from mail sent from the user's phone
        newMessage = max(newMail, key = lambda x: x[1])[0]
        # find the latest executed switch command from mysql
        mysqlLatestSwitch = getLastSwitch(connection, 'marketName')
        # compare the newMessage to the last message stored in mysql...if the message is indeed new, execute the switch command
        if newMessage != mysqlLatestSwitch:
                switch(connection, newMessage, stratDir, market)
        # clear the mail directory
        for i in os.listdir(mailDir):
                os.remove('%s%s' % (mailDir,i))
        connection.close()
