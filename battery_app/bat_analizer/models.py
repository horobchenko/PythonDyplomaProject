import dataclasses
from datetime import datetime
from typing import List
from sqlalchemy.orm import mapped_column, declared_attr, Mapped, composite
from battery_app import db, es
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo


class TableNameMixin:
    """ Міксин, що встановлює назву таблиці відповідно назві класу в нижньому регістрі"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class User(db.Model, TableNameMixin):
    """Клас користувача додатку"""

    id = mapped_column(db.Integer, primary_key=True)
    username = mapped_column(db.String(50), unique=True)
    password = mapped_column(db.Integer)
    admin = mapped_column(db.Boolean())
    battery: Mapped[List["Battery"]] = db.relationship(back_populates="user", cascade="all, delete-orphan")

    def __init__(self, username, password, admin=False):
        self.username = username
        self.password = generate_password_hash(password)
        self.admin = admin


    def is_admin(self):
        return self.admin


    def __repr__(self) -> str:
         return f"User(id={self.id!r}, name={self.name!r}, battery={self.battery!r})"

    def check_password(self, password):
        return check_password_hash(self.password, password)


@dataclasses.dataclass
class Parameters:
    """Клас для параметрів батареї, що використовуються в розрахунках"""

    min_temperature: int
    max_temperature: int
    bat_type: str

    def __repr__(self) -> str:
        return f"Parameters( min temp={self.min_temperature!r}, max tamp={self.max_temperature!r}, battery type ={self.bat_type!r})"

class Battery(db.Model, TableNameMixin):
    """Клас акумулятора користувача"""

    id = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    serial_number: Mapped[int] = mapped_column(db.Integer)
    parameters: Mapped[Parameters] = composite(mapped_column("f_cycle", nullable=True),
                                               mapped_column("l_cycle", nullable=True),
                                               mapped_column("b_type", nullable=True))
    user_id = mapped_column(db.Integer, db.ForeignKey("user.id"))
    user: Mapped["User"] = db.relationship(back_populates="battery")
    data: Mapped[List["Data"]] = db.relationship(back_populates="battery", cascade="all, delete-orphan")
    stop_cycle = mapped_column(db.Integer, nullable=True)

    def __repr__(self) -> str:
        return f"Battery(id={self.id!r}, serial_number ={self.serial_number!r}, stop_cycle ={self.stop_cycle!r})"


class Data(db.Model, TableNameMixin):
    """Клас для даних зардного циклу"""

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle: Mapped[int] = mapped_column(nullable=True)
    time: Mapped[int] = mapped_column(db.Integer)
    timestamp: Mapped[datetime]
    battery: Mapped["Battery"] = db.relationship(back_populates="ccct_data")
    bat_id: Mapped[int] = mapped_column(db.ForeignKey("battery.id"))

    def __repr__(self) -> str:
        return f"Data(id={self.id!r}, cycle={self.cycle!r}, time={self.time!r}, timestamp = {self.timestamp!r} )"

class Article(db.Model, TableNameMixin):
    """Клас для статей"""

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String)
    text: Mapped[str] = mapped_column(db.String)
    timestamp: Mapped[datetime]

    def add_index_to_es(self):
        es.index(index='articles', document={'title': self.name}, id=self.id)
        es.indices.refresh(index='articles')

    def __repr__(self) -> str:
        return f"Article(id={self.id!r}, title={self.title!r},  timestamp = {self.timestamp!r} )"


class RegistrationForm(FlaskForm):
   username = StringField('Username', [InputRequired()])
   password = PasswordField('Password', [InputRequired(), EqualTo('confirm',
   message='Passwords must match')])
   confirm = PasswordField('Confirm Password', [InputRequired()])
   serial_number = StringField('Serial_number', [InputRequired()])

class LoginForm(FlaskForm):
   username = StringField('Username', [InputRequired()])
   password = PasswordField('Password', [InputRequired()])