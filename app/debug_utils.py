from .models import User, TransactionHistory, StockPortfolio
import random
from _datetime import datetime, timedelta
from app import db

def reset_db():
    """
    Resets the database by dropping all tables, creating them again,
    and then populating them with dummy data for testing.
    """
    db.drop_all()
    db.create_all()

    # Create dummy users
    user1 = User(username="testuser1", cash=10000.0)
    user1.set_password("password")
    user2 = User(username="testuser2", cash=10000.0)
    user2.set_password("password")
    user3 = User(username="testuser3", cash=10000.0)
    user3.set_password("password")
    user4 = User(username="testuser4", cash=10000.0)
    user4.set_password("password")

    db.session.add_all([user1, user2, user3, user4])
    db.session.commit()

    users = [user1, user2, user3, user4]
    stock_ids = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    transaction_types = ["buy", "sell"]

    # Create dummy transactions for each user
    for user in users:
        for _ in range(4):
            stock_id = random.choice(stock_ids)
            price = round(random.uniform(100, 200), 2)
            quantity = random.randint(1, 10)
            transaction_type = random.choice(transaction_types)
            transaction_time = datetime.now() - timedelta(days=random.randint(1, 30))  # Random time in the past

            transaction = TransactionHistory(
                user_id=user.id,
                stock_id=stock_id,
                price=price,
                transaction_type=transaction_type,
                quantity=quantity,
                transaction_time=transaction_time
            )
            db.session.add(transaction)

            # Update StockPortfolio (simplified - you might need more complex logic)
            portfolio_entry = StockPortfolio.query.filter_by(user_id=user.id, stock_id=stock_id).first()
            if portfolio_entry:
                if transaction_type == "buy":
                    portfolio_entry.quantity += quantity
                elif transaction_type == "sell":
                    portfolio_entry.quantity -= quantity
            elif transaction_type == "buy":
                portfolio_entry = StockPortfolio(
                    user_id=user.id,
                    stock_id=stock_id,
                    quantity=quantity,
                    purchase_price=price  # Or some average if needed
                )
                db.session.add(portfolio_entry)

    db.session.commit()