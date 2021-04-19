# Degiro Interactive Dashboard

This personal project will give you a different look at your portfolio from Degiro.

The app requires that you upload two files from the Degiro App to process and Data and show the graphs - see instructions below.

*Important Notes:*
1. The files are completely anonymous, there is nothing to connect the data to your name or email (you can obviously check them before uploading).
2. The application has no way to store the data. The code is open source above.

## Example

Check your account movements over the years

![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_account.png "streamlit_account")
---

Check individual stocks in your portfolio

![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_stocks.png "streamlit_stocks")
---

Check how they performed and whether you should have sold

![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_returns.png "streamlit_returns")
---

## Instructions

1. Login to your Degiro Account
---
2. Click on Activity on the sidebar on the left

![](https://github.com/KassiusKlay/degiro/blob/master/img/activity.png "activity")
---
3. Click on Transactions on the sidebar or on the menu
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/transactions.png "transactions")
---
4. Select the starting date, just click on a random old date like 1990 (**Important:** Must be before the beginning of the account creation or the app won't start)
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/transactions_start_date.png "transactions_start_date")
---
5. Export the file as CSV (this will create the required **Transactions.csv**)
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/transactions_export.png "transactions_export")
---
6. Click on "Wallet" and select a starting date (again, any date before you started using Degiro)
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/account_start_date.png "account_start_date")
---
7. Export the file as CSV (this will create the required **Account.csv**)
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/account_export.png "account_export")
---
8. On the Streamlit App, click on the arrow on the top left to open the sidebar
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_sidebar.png "streamlit_sidebar")
---
9. Click on the Browse button and upload the previous files **Transactions.csv** and **Account.csv**
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_upload.png "streamlit_sidebar")

