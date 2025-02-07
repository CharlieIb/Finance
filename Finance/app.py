from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
from datetime import datetime

# Configure application
app = Flask(__name__)

app.secret_key = 'your_secret_key'

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


# Configure CS50 Library to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Not setting this results in a performance warning
db = SQLAlchemy(app)

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

    user_id = session["user_id"]
    print(session)
    print(user_id)
    # Fetch the username from the database (dictionary)
    result = db.session.execute(
                        text("SELECT username FROM users WHERE id = :user_id"),
                        {"user_id": user_id}
    ).fetchone()

    print(result[0])
    # Extract the username from the result
    if result:
        username = result[0]
    else:
        username = "Unknown User" # Fallback in case the user is not found

    stocks = db.session.execute(
                        text("""
                        SELECT stock_id, SUM(quantity) AS total_quantity, ROUND(AVG(purchase_price), 2) AS average_price
                        FROM stock_portfolio
                        WHERE user_id = :user_id
                        GROUP BY stock_id
                        """),
        {"user_id": user_id}
    ).fetchall()


    return render_template("index.html", username=username, stocks=stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            flash("Please enter valid symbol", "failure")
            return redirect("/buy", 400)
        symbol = request.form.get("symbol")
        if not request.form.get("shares"):
            flash("Please enter valid quantity", "failure")
            return redirect("/buy", 400)
        quantity = float(request.form.get("shares"))
        stocks = lookup(symbol)
        if not stocks:
            flash("Please enter valid symbol", "failure")
            return redirect("/buy", 400)

        # check the sql database has tables for transactions and a table for owned stocks

        user_id = session["user_id"]

        cash = db.session.execute(
            text("""
            SELECT cash 
            FROM users 
            WHERE id = :user_id
            """),
            {"user_id" : user_id}
        ).fetchone()

        if cash:
            user_cash = float(cash[0])
        else:
            user_cash = 0.0

        stock_price = stocks['price']

        total_price = stock_price*quantity

        if user_cash < total_price:
            return apology ("Not enough cash in account!")
        try:
            db.session.execute(text(
                "UPDATE users SET CASH = CASH - :total_price WHERE id = :user_id"),
                {"total_price" : total_price, "user_id" : user_id}
            )

            db.session.execute(text("""
            INSERT INTO transaction_history (user_id, stock_id, transaction_type, quantity, price)
            VALUES (:user_id, :stock_id, 'Purchase', :quantity, :stock_price)
        """),
            {"user_id" : user_id, "stock_id" : symbol, "quantity" : quantity, "stock_price" : stock_price}
            )

            db.session.execute(text("""
            INSERT INTO stock_portfolio (user_id, stock_id, quantity, purchase_price) 
            VALUES (:user_id, :stock_id, :quantity, :purchase_price)
        """),
            {"user_id" : user_id, "stock_id" : symbol, "quantity" : quantity, "purchase_price" : stock_price}
            )
            db.session.commit()
            flash('Data updated successfully!', 'success')

        except Exception as e:
            # Rollback all changes if any operation fails

            flash(f"An error occured: {e}", 'error')

        return redirect("/")

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    # Fetch the username from the database (dictionary)
    result = db.session.execute(text("""
            SELECT username 
            FROM users 
            WHERE id = :user_id
            """),
                                {"user_id" : user_id }
            ).fetchone()

    # Extract the username from the result
    if result:
        username = result[0]
    else:
        username = "Unknown User" # Fallback in case the user is not found

    result = (db.session.execute(text("""
        SELECT * 
        FROM transaction_history 
        WHERE user_id = :user_id
        """),
                                { "user_id" : user_id }
    ))

    rows = result.fetchall()

    stocks = [dict(zip(result.keys(), row)) for row in rows]


    # Format the DATETIME object to be more readable
    for stock in stocks:
        # Convert purchase_time from string to datetime object
        purchase_time = datetime.strptime(stock['transactionTime'], '%Y-%m-%d %H:%M:%S')
        # Format the datetime object to a more readable format
        stock['formatted_time'] = purchase_time.strftime('%B %d %Y at %I:%M %p')

        if stock['transaction_type'] == 'Purchase':
            stock['formatted_price'] = -abs(stock['price'])
        if stock['transaction_type'] == 'Sale':
            stock['formatted_price'] = abs(stock['price'])
    return render_template("history.html", username=username, stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.session.execute(text("""
            SELECT * 
            FROM users 
            WHERE username = :username
            """),
                                  { "username" : request.form.get("username") }
        ).fetchone()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows.hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows.id[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return redirect("/quote", 400)
        symbol = request.form.get("symbol")
        stocks = lookup(symbol)
        print(symbol, stocks)
        if not stocks:
            return redirect("/quote", 400)

        return render_template("quote.html", stocks = stocks)

    return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # forget any user_id and previous sessions
    session.clear()

    # if in "POST" then register the new user

    if request.method == "POST":
        # Verify wether data submitted is valid
        if not request.form.get("username"):
            return apology("please provide a username", 400)
        if not request.form.get("password"):
            return apology("please provide a password", 400)
        if not request.form.get("confirmation"):
            return apology("please confirm password", 400)
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        existing_user = db.session.execute(text("SELECT * FROM users WHERE username = :username"), { "username" : username }).fetchone()

        if existing_user:
            flash("username is not available", "failure")
            return redirect("/register", 400)

        if password != confirmation:
            flash("passwords do not match", "failure")
            return redirect("/register", 400)

        hashed_password = generate_password_hash(password)

        db.session.execute(text("INSERT INTO users (username, hash) VALUES(:username, :hash)"), { "username" : username, "hashed_password" : hashed_password })

        db.session.commmit()

        rows = db.session.execute(
            text("SELECT * FROM users WHERE username = :username"), { "username" : username }
        ).fetchone()
        session["user_id"] = rows.id[0]

        # return home with new session, once registered
        return redirect("/")


    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    # Fetch the username from the database (dictionary)
    result = db.session.execute(text(
                        "SELECT username FROM users WHERE id = :user_id"), { "user_id" : user_id }
                        ).fetchone()

    # Extract the username from the result
    if result:
        username = result[0]
    else:
        username = "Unknown User" # Fallback in case the user is not found

    stocks = db.session.execute(text("""
                        SELECT stock_id, SUM(quantity) AS total_quantity, ROUND(AVG(purchase_price), 2) AS average_price
                        FROM stock_portfolio
                        WHERE user_id = :user_id
                        GROUP BY stock_id
                        """), { "user_id" : user_id }
    ).fetchall()


    # Update the databases respective to the sale
    if request.method == "POST":

        # Request the entry variables
        if not request.form.get("quantity"):
            return apology("quanity required")
        quantity_to_sell = request.form.get('quantity', type=int)
        stock_id = request.form.get("stock_id")

        # Request for new sale price
        stocks = lookup(stock_id)
        if not stocks:
            return apology("stock not found", 404)

        sale_price = stocks['price']

        # Check that the variables are valid
        if not stock_id or not quantity_to_sell or quantity_to_sell <= 0:
            return apology("Valid quantity required")

        # Call stock to establish total quantity available
        stock = db.session.execute(text("""
                           SELECT id, quantity
                           FROM stock_portfolio
                           WHERE stock_id = :stock_id
                           AND user_id = :user_id
                           ORDER BY id ASC
                           """), { "stock_id" : stock_id, "user_id" : user_id }
                        ).fetchall()

        if not stock:
            return apology("stock not found", 404)

        total_quantity_available = sum(entry.quantity for entry in stock)

        if total_quantity_available < quantity_to_sell:
            return apology("Not enough shares to sell", 400)

        # Establish original value
        original_quantity_to_sell = quantity_to_sell

        # Establish total sale price
        total_sale_price = sale_price*quantity_to_sell


        # Separate entry quantities out in preparation for iteration
        for entry in stock:
            entry_quantity = entry.quantity


            # Iterate
            if quantity_to_sell >= entry_quantity:
                db.session.execute(text("DELETE FROM stock_portfolio WHERE id = :user_id"), { "user_id" : entry.id } ) # Check this in the future
                quantity_to_sell -= entry_quantity

            else:
                db.session.execute(text(
                    "UPDATE stock_portfolio SET quantity = quantity - :quantity_to_sell WHERE id = :user_id"), { "quantity_to_sell" : quantity_to_sell, "user_id" : entry.id }
                )
                break

        db.session.execute(text("""
                    INSERT INTO transaction_history (user_id, stock_id, transaction_type, quantity, price)
                    VALUES (:user_id, :stock_id, 'Sale', :quantity, :price)
                    """),
                           {"user_id" : user_id,
                            "stock_id" : stock_id,
                            "quantity" : original_quantity_to_sell,
                            "price" : sale_price }
                    )

        db.session.execute(text("""
                   UPDATE users SET CASH = CASH + :total_sale_price
                   WHERE id = :user_id
                   """), { "total_sale_price" : total_sale_price, "user_id" : user_id }
        )
        db.session.commit()

        return redirect("/")

    return render_template("sell.html", username=username, stocks=stocks)




@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user_id = session["user_id"]

    # Fetch the username from the database (dictionary)
    u_result = db.session.execute(text(
                        "SELECT username FROM users WHERE id = :user_id"), { "user_id" : user_id }
                        ).fetchone()

    # Extract the username from the result
    if u_result:
        username = u_result[0]
    else:
        username = "Unknown User" # Fallback in case the user is not found
    c_result = db.session.execute(text("""
                SELECT cash FROM users WHERE id = :user_id
    """), {"user_id" : user_id }).fetchone()

    if c_result:
        cash = c_result[0]
    else:
        flash("Cash amount not properly retrieved", "failure")


    if request.method =="POST":

        # to identify between the different post function in the account page
        form_type = request.form.get("form_type")

        # If change password is called
        if form_type == "change_password":
            result = db.session.execute(text(
                "SELECT * FROM users WHERE id = :user_id"), { "user_id" : user_id }
            )

            rows = result.fetchall()

            if not rows:
                flash("User not found.", "failure")
                return redirect("/account")

            rows = [dict(zip(result.keys(), row))for row in rows]

            row = rows[0]

            # variables to work with
            oldpassword = request.form.get("oldpassword")
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            user_hash = row['hash']

            # Verify conditions for correct form submition
            if not check_password_hash(user_hash, oldpassword):
                flash("Old/current password is inccorect, try again", "failure")
                return redirect("/account")

            if password1 != password2:

                flash("Passwords do not match", "failure")
                return redirect("/account")

            new_hashed_password = generate_password_hash(password1)
            # replace the old password

            db.session.execute(text("""
            UPDATE users 
            SET hash = :new_hashed_password 
            WHERE id = :user_id
            """), { "new_hashed_password" : new_hashed_password, "user_id" : user_id }
                               )

            flash('Password updated successfully!', 'success')

            return redirect("/account")
        elif form_type == "add_cash":
            add_cash = request.form.get("add_amount") # The amount entered by the user

            # request the current cash amount





    return render_template("account.html", username=username, cash=cash)