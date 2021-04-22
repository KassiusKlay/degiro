# Degiro Interactive Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/kassiusklay/degiro)

## Introduction

Degiro is one of the most used online brokers in Europe, mostly due to its very low trading fees. 

However, its interface is considered terrible by many users and there are not tools to show you how your portfolio is evolving over time. 

I developed this webapp that takes your CSV files and displays your trades is a much more appealing way.
It also allows you to compare the performance of your individual stocks over time.

You can see Examples and Instructions down below.

If you have any bugs, suggestions or questions please email me joaocassis@hey.com

**PLEASE READ:**
1. The CSV files required are completely anonymous, there is nothing to connect your data to your name or email (you can obviously check them before uploading).
2. Your data is not logged in any way, shape or form. It's only cached in StreamLit servers for faster access everytime you use it. No one has access to it (code is open source so fell free to confirm it).

## Example

Check how much you deposited and withdrew from your account over the years

![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_account.png "streamlit_account")
---

Check individual stock trades in your portfolio and compared them with its historical data

![](https://github.com/KassiusKlay/degiro/blob/master/img/streamlit_stocks.png "streamlit_stocks")
---

Compare all your stocks between each other

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
4. Select the starting date **(PLEASE READ: Start Date be before the beginning of the account creation or the app won't start)**
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/transactions_start_date.png "transactions_start_date")
---
5. Export the file as CSV (this will create the required **Transactions.csv**)
 
![](https://github.com/KassiusKlay/degiro/blob/master/img/transactions_export.png "transactions_export")
---
6. Click on "Wallet" and select a starting date
 
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

