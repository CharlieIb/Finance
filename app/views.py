from app import app
import sqlalchemy as sa
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from .utils.helpers import apology, lookup
from .utils.models import User, StockPortfolio, TransactionHistory

from app import db




@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = current_user.id

    # Fetch the username using the ORM
    user = db.session.get(User, user_id)
    username = user.username if user else "Unknown User"  # Fallback in case the user is not found

    # Fetch the stock portfolio using the ORM
    stocks = (
        db.session.query(
            StockPortfolio.stock_id,
            sa.func.sum(StockPortfolio.quantity).label('total_quantity'),
            sa.func.round(sa.func.avg(StockPortfolio.buy_price), 2).label('average_price')
        )
        .filter(StockPortfolio.user_id == user_id)
        .group_by(StockPortfolio.stock_id)
        .all()
    )

    return render_template("index.html", username=username, stocks=stocks)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Validate form inputs
        symbol = request.form.get("symbol")
        if not symbol:
            flash("Please enter a valid symbol", "failure")
            return redirect("/buy", 400)

        try:
            quantity = float(request.form.get("shares"))
            if quantity <= 0:
                flash("Please enter a valid quantity", "failure")
                return redirect("/buy", 400)
        except (ValueError, TypeError):
            flash("Please enter a valid quantity", "failure")
            return redirect("/buy", 400)

        # Look up the stock
        stock_data = lookup(symbol)
        if not stock_data:
            flash("Please enter a valid symbol", "failure")
            return redirect("/buy", 400)

        stock_price = stock_data['price']
        total_price = stock_price * quantity

        # Fetch the current user's cash balance
        user = db.session.get(User, current_user.id)
        if not user:
            flash("User not found", "failure")
            return redirect("/buy", 400)

        user_cash = user.cash

        # Check if the user has enough cash
        if user_cash < total_price:
            return apology("Not enough cash in account!")

        try:
            # Deduct the total price from the user's cash
            user.cash -= total_price

            # Add a new transaction to the transaction history
            transaction = TransactionHistory(
                user_id=current_user.id,
                stock_id=symbol,
                transaction_type='buy',
                quantity=quantity,
                price=stock_price
            )
            db.session.add(transaction)

            # Update or add to the user's stock portfolio
            portfolio_entry = db.session.query(StockPortfolio).filter(
                StockPortfolio.user_id == current_user.id,
                StockPortfolio.stock_id == symbol
            ).first()

            if portfolio_entry:
                # If the stock already exists in the portfolio, update the quantity and average price
                total_quantity = portfolio_entry.quantity + quantity
                total_cost = (portfolio_entry.quantity * portfolio_entry.buy_price) + (quantity * stock_price)
                average_price = total_cost / total_quantity

                portfolio_entry.quantity = total_quantity
                portfolio_entry.buy_price = average_price
            else:
                # If the stock is not in the portfolio, create a new entry
                portfolio_entry = StockPortfolio(
                    user_id=current_user.id,
                    stock_id=symbol,
                    quantity=quantity,
                    buy_price=stock_price
                )
                db.session.add(portfolio_entry)

            # Commit all changes to the database
            db.session.commit()
            flash('Purchase successful!', 'success')

        except Exception as e:
            # Rollback all changes if any operation fails
            db.session.rollback()
            flash(f"An error occurred: {e}", 'error')

        return redirect("/")

    return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = current_user.id

    # Fetch the username using the ORM
    user = db.session.get(User, user_id)
    username = user.username if user else "Unknown User"  # Fallback in case the user is not found

    # Fetch the transaction history using the ORM
    transactions = (
        db.session.query(TransactionHistory)
        .filter(TransactionHistory.user_id == user_id)
        .all()
    )

    # Format the transactions for the template
    stocks = []
    for transaction in transactions:
        stock = {
            "stock_id": transaction.stock_id,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "transactionTime": transaction.transaction_time.strftime('%Y-%m-%d %H:%M:%S'),
            "formatted_time": transaction.transaction_time.strftime('%B %d %Y at %I:%M %p')
        }
        stocks.append(stock)

    return render_template("history.html", username=username, stocks=stocks)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # redirect if page is inappropriate
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username using the ORM
        user = db.session.query(User).filter(User.username == request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.password_hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # login_user(user, remember=form.remember_me.data)

        # Log the user in using Flask-Login (if you're using Flask-Login)
        login_user(user)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    logout_user()

    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    stocks = {}
    if request.method == "POST":
        if not request.form.get("symbol"):
            return redirect("/quote", 400)
        symbol = request.form.get("symbol")
        stocks = lookup(symbol)
        if not stocks:
            return redirect("/quote", 400)

        return render_template("quote.html", stocks = stocks)

    return render_template("quote.html", stocks=stocks
                           )

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Verify whether data submitted is valid
        if not request.form.get("username"):
            return apology("please provide a username", 400)
        if not request.form.get("password"):
            return apology("please provide a password", 400)
        if not request.form.get("confirmation"):
            return apology("please confirm password", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the username already exists using the ORM
        existing_user = db.session.query(User).filter(User.username == username).first()
        if existing_user:
            flash("username is not available", "failure")
            return redirect("/register", 400)

        # Check if the password and confirmation match
        if password != confirmation:
            flash("passwords do not match", "failure")
            return redirect("/register", 400)

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user using the ORM
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Fetch the newly created user to get their ID
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            flash("registration failed", "failure")
            return redirect("/register", 400)

        # Remember which user has logged in
        current_user = db.session.scalar(sa.Select(User).where(User.username == username))
        if current_user is None or not current_user.check_password(password):
            flash('Error retrieving details', 'danger')
            return redirect(url_for('login'))

        login_user(current_user)
        # Redirect to home page after successful registration
        return redirect("/")

    # If the request method is GET, render the registration form
    return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = current_user.id

    # Fetch the username using the ORM
    user = db.session.get(User, user_id)
    username = user.username if user else "Unknown User"  # Fallback in case the user is not found

    # Fetch the user's stock portfolio using the ORM
    stocks = (
        db.session.query(
            StockPortfolio.stock_id,
            sa.func.sum(StockPortfolio.quantity).label('total_quantity'),
            sa.func.round(sa.func.avg(StockPortfolio.buy_price), 2).label('average_price')
        )
        .filter(StockPortfolio.user_id == user_id)
        .group_by(StockPortfolio.stock_id)
        .all()
    )

    # Update the databases respective to the sale
    if request.method == "POST":
        # Validate form inputs
        if not request.form.get("quantity"):
            return apology("quantity required", 400)
        quantity_to_sell = request.form.get('quantity', type=int)
        stock_id = request.form.get("stock_id")

        if not stock_id or not quantity_to_sell or quantity_to_sell <= 0:
            return apology("valid quantity required", 400)

        # Look up the stock to get the current price
        stock_data = lookup(stock_id)
        if not stock_data:
            return apology("stock not found", 404)

        sale_price = stock_data['price']

        # Fetch the user's stock portfolio entries for the specified stock
        stock_entries = (
            db.session.query(StockPortfolio)
            .filter(StockPortfolio.user_id == user_id, StockPortfolio.stock_id == stock_id)
            .order_by(StockPortfolio.id)
            .all()
        )

        if not stock_entries:
            return apology("stock not found in portfolio", 404)

        # Calculate the total quantity of the stock available
        total_quantity_available = sum(entry.quantity for entry in stock_entries)

        if total_quantity_available < quantity_to_sell:
            return apology("not enough shares to sell", 400)

        # Calculate the total sale price
        total_sale_price = sale_price * quantity_to_sell

        # Iterate through the stock entries to update or delete them
        remaining_quantity_to_sell = quantity_to_sell
        for entry in stock_entries:
            if remaining_quantity_to_sell >= entry.quantity:
                # Delete the entry if the entire quantity is sold
                db.session.delete(entry)
                remaining_quantity_to_sell -= entry.quantity
            else:
                # Update the entry if only part of the quantity is sold
                entry.quantity -= remaining_quantity_to_sell
                break

        # Add a new transaction to the transaction history
        transaction = TransactionHistory(
            user_id=user_id,
            stock_id=stock_id,
            transaction_type='Sale',
            quantity=quantity_to_sell,
            price=sale_price
        )
        db.session.add(transaction)

        # Update the user's cash balance
        user.cash += total_sale_price

        # Commit all changes to the database
        db.session.commit()

        # Redirect to the home page
        return redirect("/")

    # Render the sell template with the user's stock portfolio
    return render_template("sell.html", username=username, stocks=stocks)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Manage user account settings"""
    user_id = current_user.id

    # Fetch the user using the ORM
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found", "failure")
        return redirect("/")

    username = user.username
    cash = user.cash

    if request.method == "POST":
        # Identify the form type
        form_type = request.form.get("form_type")

        # Handle password change
        if form_type == "change_password":
            old_password = request.form.get("oldpassword")
            new_password1 = request.form.get("password1")
            new_password2 = request.form.get("password2")

            # Verify the old password
            if not check_password_hash(user.password_hash, old_password):
                flash("Old/current password is incorrect, try again", "failure")
                return redirect("/account")

            # Verify the new passwords match
            if new_password1 != new_password2:
                flash("Passwords do not match", "failure")
                return redirect("/account")

            # Update the password
            user.password_hash = generate_password_hash(new_password1)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect("/account")

        # Handle adding cash
        elif form_type == "add_cash":
            add_amount = request.form.get("add_amount", type=float)

            # Validate the amount
            if not add_amount or add_amount <= 0:
                flash("Please enter a valid amount", "failure")
                return redirect("/account")

            # Update the user's cash balance
            user.cash += add_amount
            db.session.commit()
            flash(f"Successfully added ${add_amount:.2f} to your account", "success")
            return redirect("/account")

    # Render the account page
    return render_template("account.html", username=username, cash=cash)