#!/usr/bin/env Rscript

library(RMySQL)
library(data.table)
library(reshape2)

mydb = dbConnect(MySQL(), user='username', 
                 password='password', 
                 dbname='politics', 
                 host='localhost')

data <- suppressWarnings(dbSendQuery(mydb, "select * from import_politics"))
data = data.table(fetch(data, n = -1))

markets = suppressWarnings(dbSendQuery(mydb, "select * from markets"))
markets = data.table(fetch(markets, n=-1))
setnames(markets, 'id' , 'market')

securities = suppressWarnings(dbSendQuery(mydb, "select * from securities"))
securities = data.table(fetch(securities, n=-1))
setnames(securities, 'id' , 'security')

candidates = suppressWarnings(dbSendQuery(mydb, "select * from candidates"))
candidates = data.table(fetch(candidates, n=-1))
setnames(candidates, 'id' , 'candidate')

data= merge(merge(merge(data,candidates,by = 'candidate'), markets, by ='market'), securities, by = 'security')
data = data[, !c('tick_id','security','market','candidate'), with=FALSE]
setnames(data,c('name.x','name.y','name'),c('candidate','market','security'))

marketAgg = data[market!='exchangeOnly'][,list(price = mean(price)),by=list(candidate,security,report_id)]
exchangeOnly = data[market=='exchangeOnly']



jpeg(filename=paste0(getwd(),"/marketReport.jpeg"), 
      width = 1200, height = 1000, res = 100 )
par(mfrow=c(2,3))



usPrezAgg = marketAgg[security == 'usPrez'][,-2,with=FALSE]
gopNomAgg = marketAgg[security == 'gopNom'][,-2,with=FALSE]
demNomAgg = marketAgg[security == 'demNom'][,-2,with=FALSE]

usPrezAgg = acast(usPrezAgg, report_id ~ candidate, value.var="price")
matplot(usPrezAgg, type = c("b"),pch=1,col = 1:ncol(usPrezAgg), bty='L',
        xlab="time (hr)", ylab="Probability", yaxt='n')
axis(side = 2, tick = 0.05, at = seq(0,1,0.05), cex.axis = 0.9)
legendxy<-c(0.5, -1)
legend(legendxy,legend = colnames(usPrezAgg), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
title("US Presidential Election - Market Average")


gopNomAgg = acast(gopNomAgg, report_id ~ candidate, value.var="price")
matplot(gopNomAgg, type = c("b"),pch=1,col = 1:ncol(gopNomAgg), bty='L',
        xlab="time (hr)", ylab="Probability", yaxt='n')
axis(side = 2, tick = 0.05, at = seq(0,1,0.05), cex.axis = 0.9)
legendxy<-c(0.5, -1)
legend(legendxy,legend = colnames(gopNomAgg), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
title("GOP Nomination - Market Average")


demNomAgg = acast(demNomAgg, report_id ~ candidate, value.var="price")
matplot(demNomAgg, type = c("b"),pch=1,col = 1:ncol(demNomAgg), bty='L',
        xlab="time (hr)", ylab="Probability", yaxt='n')
axis(side = 2, tick = 0.05, at = seq(0,1,0.05), cex.axis = 0.9)
legendxy<-c(0.5, -1)
legend(legendxy,legend = colnames(demNomAgg), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
title("DEM Nomination - Market Average")





usPrez = exchangeOnly[security == 'usPrez'][,-4,with=FALSE]
gopNom = exchangeOnly[security == 'gopNom'][,-4,with=FALSE]
demNom = exchangeOnly[security == 'demNom'][,-4,with=FALSE]


usPrez = acast(usPrez, report_id ~ candidate, value.var="price")
usPrez = usPrez[,colnames(usPrez)[!is.na(usPrez[nrow(usPrez),])]]
matplot(usPrez, type = c("b"),pch=1,col = 1:ncol(usPrez), bty='L',
        xlab="time (hr)", ylab="Probability", yaxt='n')
axis(side = 2, tick = 0.05, at = seq(0,1,0.05), cex.axis = 0.9)
legendxy<-c(0.5, -1)
legend(legendxy,legend = colnames(usPrez), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
title("US Presidential Election - exchangeOnly")


gopNom = acast(gopNom, report_id ~ candidate, value.var="price")
gopNom = gopNom[,colnames(gopNom)[!is.na(gopNom[nrow(gopNom),])]]
matplot(gopNom, type = c("b"),pch=1,col = 1:ncol(gopNom), bty='L',
        xlab="time (hr)", ylab="Probability", yaxt='n')
axis(side = 2, tick = 0.05, at = seq(0,1,0.05), cex.axis = 0.9)
legendxy<-c(0.5, -1)
legend(legendxy,legend = colnames(gopNom), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
title("GOP Nomination - exchangeOnly")


demNom = acast(demNom, report_id ~ candidate, value.var="price")
demNom = demNom[,colnames(demNom)[!is.na(demNom[nrow(demNom),])]]
matplot(demNom, type = c("b"),pch=1,col = 1:ncol(demNom), bty='L',
        xlab="time (hr)", ylab="Probability", yaxt='n')
axis(side = 2, tick = 0.05, at = seq(0,1,0.05), cex.axis = 0.9)
legendxy<-c(0.5, -1)
legend(legendxy,legend = colnames(demNom), lty=c("solid","dashed"), col = 1:4, bty="n", cex=0.9)
title("DEM Nomination - exchangeOnly")



dev.off()

cons = dbListConnections(MySQL())
for(con in cons){dbDisconnect(con)}

