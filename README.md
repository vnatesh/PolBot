PolBot is an automated trading engine designed for political futures markets. Mirroring the structure of algorithmic trading systems in finance, PolBot is made up of distinct components:
 
Market Data Aggregator – This component acquires raw data from polls as well as pricing and volume tick data from specific political futures exchanges. It then parses the data and loads it into a MySQL database. Market data is scraped every minute via the CRON scheduler.
	 
Trading API – This allows the user to programmatically interface with the exchange. It is composed of a terminal utility and python wrapper for that utility with extra functionality. The API can be called from any script, allowing the user to create algorithmic strategies based on signals
	 
Strategy Space – Users can dump scripts containing event-driven and/or statistical strategies into the strategy space where they will be executed according to whatever schedule is specified by the strategy
 
 
 
The platform also contains several interesting features:
 
Automatic Switching – The engine can be remotely turned on or off via a text message or email switch command.
	 
Parameter Toggling – Strategies involving several input parameters can be modified remotely via text message
	 
Poll Reporting – The user can be notified of recently updated polls via text message
	 
Error Alerting – Data scraping and trading errors are directly reported to the user via text message. For example, scraping errors may result from a change in the data source’s markup structure whereas trading errors can result from the platform trying to execute a buy/sell at a zero price.
	 
Real-time Data Tracking – User-friendly graphical display of polling, pricing, and volume data over time. The system can also be setup to send market reports at scheduled time intervals.



Coming soon
 
A shiny application (web-app framework for R) that integrates real-time data tracking and allows users to interactively view their positions, P&L, and other financial metrics. It will also serve as a GUI for backtesting strategies.
