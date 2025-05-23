Web App for Simulated Stock Trading Using Yahoo Finance API


Description:
- What does it do?
  - This web application allows the user to simulate buying and selling shares on the open market.
  - This app pulls its stock data from the Yahoo finance API using the yfinance package.
  - Each user when they make an account are given a simulated $10000 to spend on stocks at prices currently on the market.
- Why was it built?
  - To explore the usage of APIs and database usage in a web app.
- What problem does it solve?
  - This app does not solve any problem except that of curiosity

Features:
- User Authentication and Account management
  - User signup/login
  - User Dashboard
  - Session management
- Stock Data Retrieval (Yahoo Finance API Integration)
  - Fetch Live Stock Prices using yfinance
  - Show stock details (Symbol, Current Price) -- could also include Company Name and Historical Data in the future
  - Display Stock Charts - Coming soon
- Simulated Trading System
  - Starting Balance of $10,000
  - Users can buy and sell shares at live prices
  - Prevent Negative Balance
  - Allows users to manually add cash to their account
- See current holdings - stock name, quantity
  - Total value, profit/loss ----- Coming soon
- Transaction History and Analytics ----- Coming Soon
- Cash Management System
  - Users can add cash to their balance anytime
  - prevent negative balance
    - Show warning if they try to buy too much
- UI + Frontend
  - Responsive Dashboard
  - Stock search bar
    - Coming Soon -- autocomplete symbol search
  - Coming Soon -- Charts for portfolio performance
- Security Features
  - User Authentication using hashed passwords courtesy of the werkzeug.security package
  - Session security - Flask-session
  - 
- Coming Soon
  - Expose an API for Real-Time Data
  - Allow AJAX calls for buying and selling without relading
  - secure API with authentication and rate limiting

Things to be be updated in the file:
- Please write the Introduction to this project
- Need to update the comments to make the codes more readable:
  - app.py
  - helpers.py
  - account.html
  - apology.html
  - buy.html
  - buyquote.html ---- potential remove this html think it may be redundant
  - history.html
  - index.html
  - layout.html
  - login.html
  - quote.html
  - register.html
  - sell.html
- helpers.py
  - organise and clean the code in this file, much is not needed
- Account page:
  - (MH) make layout appealing:
    - balance revealing could be more appealing
    - there could be a separator between the balance and the add cash activities for the wallet options subheading
      - make this a h3 potentially
  - (NTH) Improve password change process:
    - The current process is unintuitive
    - Could be improved by either leading to a new page in which to change the password
    - Unsure how much the box reveal adds to the site and its functionality
- History:
  - This page is functionally good. There are additional features which coudl be nice to have(NTH)
  - (NTH) Could (maybe utilising AJAX) provide additional functionality
    - Grouping transactions
    - Filtering Columns
    - Ordering Columns
    - Searching for specific stocks
    -