from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    cash: so.Mapped[float] = so.mapped_column(sa.Float, default=10000.0)

    # Relationships
    transactions: so.Mapped[list['TransactionHistory']] = so.relationship(back_populates='user')
    portfolio: so.Mapped[list['StockPortfolio']] = so.relationship(back_populates='user')

    def __repr__(self):
        return f'User(id={self.id}, username={self.username}, cash={self.cash})'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TransactionHistory(db.Model):
    __tablename__ = 'transaction_history'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    stock_id: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=False)
    price: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    transaction_type: so.Mapped[str] = so.mapped_column(sa.String(4), nullable=False)  # 'buy' or 'sell'
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    transaction_time: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates='transactions')

    def __repr__(self):
        return f'TransactionHistory(id={self.id}, user_id={self.user_id}, stock_id={self.stock_id}, type={self.transaction_type}, quantity={self.quantity}, time={self.transaction_time})'


class StockPortfolio(db.Model):
    __tablename__ = 'stock_portfolio'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    stock_id: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=False)
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    purchase_price: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)

    # Relationships
    user: so.Mapped['User'] = so.relationship(back_populates='portfolio')

    def __repr__(self):
        return f'StockPortfolio(id={self.id}, user_id={self.user_id}, stock_id={self.stock_id}, quantity={self.quantity}, purchase_price={self.purchase_price})'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))