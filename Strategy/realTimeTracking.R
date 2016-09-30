library(RMySQL)
library(data.table)
library(reshape2)

mydb = dbConnect(MySQL(), user='username', 
                 password='password', 
                 dbname='politics', 
                 host='localhost')

# SELECT p.report_id, p.BestBuyYesCost priceBuy, p.BestSellYesCost priceSell, p.contract_id security, r.timestamp
# FROM price_marketName p
# INNER JOIN report_marketName r ON p.report_id = r.report_id
# WHERE DAYNAME(r.timestamp) NOT IN ('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday')
# AND HOUR(r.timestamp) >= 5
# AND p.report_id >= (SELECT max(report_id) FROM price_marketName) - 1
# ORDER by report_id ASC

rawData = suppressWarnings(data.table(dbGetQuery(mydb, "select p.report_id, p.BestBuyYesCost,
p.BestSellYesCost, BestBuyNoCost, BestSellNoCost, p.Volume, c.TickerSymbol security, r.timestamp
from price_marketName p
inner join contract_marketName c on p.contract_id = c.ID
inner join report_marketName r on p.report_id = r.report_id")))

# rawData = suppressWarnings(data.table(dbGetQuery(mydb, "select p.report_id, p.BestBuyYesCost, 
# p.BestSellYesCost, BestBuyNoCost, BestSellNoCost, p.Volume, c.TickerSymbol security, r.timestamp 
# from price_marketName p 
# inner join contract_marketName c on p.contract_id = c.ID 
# inner join report_marketName r on p.report_id = r.report_id
# WHERE DAYNAME(r.timestamp) NOT IN ('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday')
# AND HOUR(r.timestamp) >= 5")))

data <- rawData[!is.na(Volume)]
data$volumeDelta <- c(0, diff(data$Volume))
# data <- rawData
data$day <- as.Date(data$timestamp)
data$week <- strftime(data$day,format="%W")
data$contractWeek <- ifelse(weekdays(data$day) %in% c('Saturday', 'Sunday'), as.integer(data$week) + 1, as.integer(data$week))

priceData <- data[contractWeek == max(contractWeek)]
# priceData <- data
priceData = acast(priceData, report_id ~ security, value.var="BestBuyYesCost")

par(mfcol=2:1,xpd=TRUE, font.lab = 4)
matplot(priceData, type = c("b"),pch=1,col = 1:ncol(priceData), bty='L'
        , ylab="BestBuyYesCost", yaxt='n')
title("Real-time Exchange Data Tracking")
axis(side = 2, tick = 0.01, at = seq(0,1,0.05), cex.axis = 0.9)
legend('topleft',legend = colnames(priceData), lty=c("solid","dashed"), col = 1:7, bty="n", cex=0.6)

# volumeData <- data
volumeData <- data[volumeDelta>=0 & contractWeek == max(contractWeek)]
volumeData = acast(volumeData, report_id ~ security, value.var="volumeDelta")
matplot(volumeData, type = c("b"), pch=1,col = 1:ncol(volumeData), bty='L', xlab="time (approx 1 minute increment)",  ylab="∆ Volume" )
legend('topleft',legend = colnames(volumeData), lty=c("solid","dashed"), col = 1:7, bty="n", cex=0.6)

cons = dbListConnections(MySQL())
for(con in cons){dbDisconnect(con)}

# func <- function(x, data){
#   if(data[x,]$volumeDelta < data[x+1,]$volumeDelta &  data[x+1,]$volumeDelta < data[x+2,]$volumeDelta) {
#     print('ewdscx')}
#   else{print('er cx')}
# }
# 
# 
# data$rownum <- 1:nrow(data)
# func <- function(x){
#   if(data[rownum == x]$volumeDelta < data[rownum==x+1]$volumeDelta & data[rownum==x+1]$volumeDelta < data[rownum==x+2]$volumeDelta & x <=nrow(data)-3) {
#   return(TRUE)
#   }
#   else {return(FALSE)}
# }
# 
# data[, func(x,data), by = data$rownum]
# 
# 
# mapply()
