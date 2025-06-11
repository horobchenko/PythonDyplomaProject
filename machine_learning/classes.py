from sklearn.compose import ColumnTransformer
from battery_app import db
import numpy as np
import pandas as pd
from battery_app.bat_analizer.models import Data, Battery
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