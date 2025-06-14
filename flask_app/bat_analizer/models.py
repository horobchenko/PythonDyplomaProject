from datetime import datetime
from typing import List
import dataclasses
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import mapped_column, Mapped, declared_attr, composite
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.simple import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo

from flask_app.battery_app import app

#DB creation
db = SQLAlchemy(app)
with app.app_context():
 db.create_all()

#migration db creation
migration = Migrate(app, db)

#####db models#####

class TableNameMixin:
    """ Міксин, що встановлює назву таблиці відповідно назві класу в нижньому регістрі"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class User(db.Model, TableNameMixin):
    """Клас користувача додатка"""

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
    parameters: Mapped[Parameters] = composite(mapped_column("min_temperature", nullable=True),
                                               mapped_column("max_temperature", nullable=True),
                                               mapped_column("bat_type", nullable=True))
    user_id = mapped_column(db.Integer, db.ForeignKey("user.id"))
    user: Mapped["User"] = db.relationship(back_populates="battery")
    data: Mapped[List["Data"]] = db.relationship(back_populates="battery", cascade="all, delete-orphan")
    stop_cycle = mapped_column(db.Integer, nullable=True)

    def __repr__(self) -> str:
        return f"Battery(id={self.id!r}, serial_number ={self.serial_number!r}, stop_cycle ={self.stop_cycle!r})"


class Data(db.Model, TableNameMixin):
    """Клас для даних зарядного циклу"""

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle: Mapped[int] = mapped_column(nullable=True)
    time: Mapped[int] = mapped_column(db.Integer)
    timestamp: Mapped[datetime]
    battery: Mapped["Battery"] = db.relationship(back_populates="data")
    bat_id: Mapped[int] = mapped_column(db.ForeignKey("battery.id"))

    def __repr__(self) -> str:
        return f"Data(id={self.id!r}, cycle={self.cycle!r}, time={self.time!r}, timestamp = {self.timestamp!r} )"

class Article(db.Model, TableNameMixin):
    """Клас для статей"""

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String)
    text: Mapped[str] = mapped_column(db.String)
    timestamp: Mapped[datetime]

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

###############Logistic Regression class

from sklearn.compose import ColumnTransformer
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from pathlib import Path
from sqlalchemy import bindparam, update

class LogisticRegressionClass:
    """class to estimate if the last cycle is stop cycle"""
    df: pd.DataFrame
    pipe: Pipeline

    def train(self, bat_type: str):
        """method finds the data file path according to the battery type, then make a table, a model and train it """
        path = Path.cwd()
        class_name = self.__class__.__name__
        name = bat_type
        file_name = f"machine_learning/data/{class_name}_data/{name}.csv"  # example: machine_learning/data/LogisticRegression_data/a.csv
        file = path/file_name
        if file.exists():
            file = file.as_posix()
        else:
            while path.parent:
                file = path.parent/file_name
                if file.exists():
                    file = file.as_posix()
                    break
        self.df = pd.read_csv(file)
        train, test, y_train,y_test = train_test_split(self.df.drop('indicator', axis=1),
                          self.df['indicator'],
                          test_size=.3,
                          stratify=self.df['indicator'], random_state=100)
        cat_columns = train.dtypes[train.dtypes == 'object'].index.tolist()
        num_columns = train.dtypes[train.dtypes != 'object'].index.tolist()
        num_pipe = Pipeline([('imp', SimpleImputer(strategy='median')),('scaler', StandardScaler())])
        cat_pipe = Pipeline([('ohe', OneHotEncoder(handle_unknown='ignore'))])
        transformers = [('num', num_pipe, num_columns),('cat', cat_pipe, cat_columns)]
        transformer = ColumnTransformer(transformers=transformers)
        self.pipe = Pipeline([('tf', transformer),('logreg', LogisticRegression(C=0.03,solver='liblinear',random_state=20))])
        self.pipe.fit(train, y_train)


    def predict(self, user_id):
        """method finds the last cycle data according to the user id and predict if it is the stop cycle """
        cycle = db.select(Data.cycle).join_from(Battery, Data).where(Battery.user_id == user_id)
        cycle = db.session.scalar(cycle).last()
        time = db.select(Data.time).join_from(Battery, Data).where(Battery.user_id == user_id)
        time = db.session.scalar(time).last()
        data_df = {'cycle': [cycle], 'time': [time]}
        df = pd.DataFrame(data=data_df)
        proba = self.pipe.predict_proba(df)
        result = np.where(proba[0] == proba[0].max())[0]
        if result == 1:
            db.session.execute(update(Battery).where(Battery.user_id==bindparam("user_id")),
                               [
                                   {"user_id": user_id,"stop_cycle": cycle}
                               ]
                               )
        return result


log_reg_model = LogisticRegressionClass()





