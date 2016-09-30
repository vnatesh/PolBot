#!/usr/bin/env Rscript

library(RMySQL)
library(data.table)
library(reshape2)

mydb = dbConnect(MySQL(), user='username', 
                 password='password', 
                 dbname='politics', 
                 host='localhost')

data <- suppressWarnings(dbSendQuery(mydb, "select * from import_rcp"))
data = data.table(fetch(data, n = -1))

markets = suppressWarnings(dbSendQuery(mydb, "select * from markets"))
markets = data.table(fetch(markets, n=-1))
setnames(markets, 'id' , 'market')

securities = suppressWarnings(dbSendQuery(mydb, "select * from securities"))
securities = data.table(fetch(securities, n=-1))
setnames(securities, 'id' , 'security')


data = merge(merge(data,markets,by = 'market'), securities, by ='security')
data = data[, !c('tick_id','security','market'), with=FALSE]
setnames(data,c('name.x','name.y'),c('market','security'))


#data = acast(data, report_id ~ security, value.var="price")
data = tail(acast(data, report_id ~ security, value.var="price"), 480)
data = data[,colnames(data)[!is.na(data[nrow(data),])]]



jpeg(filename=paste0(getwd(),"/rcpMarketReport.jpeg"), 
     width = 1200, height = 1000, res = 100 )


# first, set the size of the window
#par(mar = c(5,5,2,5))
par(mar = c(5.1,3,3,2.1))
exchangeName = data[,colnames(data)[colnames(data)!='marketNameRCP']]
matplot(exchangeName, type = c("b"),pch=1,col = 1:ncol(exchangeName), bty='L',
        xlab="time (3-5 min)", ylab="Price", yaxt='n')
# set the axis side as left or right (4)
axis(side = 2, tick = 0.01, at = seq(0,1,0.05), cex.axis = 0.9)
#legendxy<-c(1, -0.5)
legend('topleft',legend = colnames(exchangeName), lty=c("solid","dashed"), col = 1:7, bty="n", cex=0.9)

par(new=TRUE)
rcp = data[,colnames(data)[colnames(data)=='marketNameRCP']]
rcp = matrix(rcp,nrow = length(names(rcp)), ncol = 1, dimnames = list(names(rcp),'marketNameRCP'))
matplot(rcp, type = c("b"), pch=1,col = 1:ncol(rcp), bty='L', axes = FALSE, xlab="time (3-5 min)", ylab="Price" )
axis(side = 4)
mtext(side = 4, line = 3, 'RCP Rating')
legend('left', legend = colnames(rcp), lty=c("solid","dashed"), col = 1:7, bty="n", cex=0.9)

title("RCP Average Tracking")


# data = tail(acast(data, report_id ~ security, value.var="price"), 200)
# data = data[,colnames(data)[!is.na(data[nrow(data),])]]
# matplot(data, type = c("b"),pch=1,col = 1:ncol(data), bty='L',
#         xlab="time (3-5 min)", ylab="Price", yaxt='n')
# axis(side = 2, tick = 0.01, at = seq(0,1,0.05), cex.axis = 0.9)
# legendxy<-c(1, -0.5)
# legend(legendxy,legend = colnames(data), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
# title("RCP Average Tracking")


# x <- 1:5
# y1 <- rnorm(5)
# y2 <- rnorm(5,20)
# par(mar=c(5,4,4,5)+.1)
# plot(x,y1,type="l",col="red")
# par(new=TRUE)
# plot(x, y2,type="l",col="blue",xaxt="n",yaxt="n",xlab="",ylab="")
# axis(4)
# mtext("y2",side=4,line=3)
# legend("topleft",col=c("red","blue"),lty=1,legend=c("y1","y2"))



dev.off()
# 
cons = dbListConnections(MySQL())
for(con in cons){dbDisconnect(con)}

