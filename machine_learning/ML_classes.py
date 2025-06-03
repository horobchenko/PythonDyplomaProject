from pathlib import Path

from sklearn.compose import ColumnTransformer

from battery_app import db
import numpy as np
import pandas as pd
from battery_app.bat_analizer.models import Data, User, Battery
import missingno as msno
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


class LogisticRegration:
    df: pd.DataFrame
    pipe: Pipeline
    path: Path

    def train(self, bat_type):
        self.path = Path()
        self.df = pd.read_csv(self.path)
        train, test, y_train, y_test = train_test_split(self.df.drop('indicator', axis=1),
                                                        self.df['indicator'],
                                                        test_size=.3,
                                                        stratify=self.df['indicator'], random_state=100)
        cat_columns = train.dtypes[train.dtypes == 'object'].index.tolist()
        num_columns = train.dtypes[train.dtypes != 'object'].index.tolist()
        num_pipe = Pipeline([
            ('imp', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())])
        cat_pipe = Pipeline([('ohe', OneHotEncoder(handle_unknown='ignore'))])
        transformers =[('num', num_pipe, num_columns),('cat', cat_pipe, cat_columns)]
        transformer = ColumnTransformer(transformers=transformers)
        self.pipe = Pipeline([('tf', transformer),
                              ('logreg', LogisticRegression(C=0.03,
                                                            solver='liblinear',

                                                            random_state=20))])
        self.pipe.fit(train, y_train)

        def predict(self, user_id):
            cycle = db.select(User, Data.cycle).where(User.id == user_id).last()
            time = db.select(User, Data.time).where(User.id == user_id).last()
            data_df = {'cycle': [cycle], 'time': [time]}
            df = pd.DataFrame(data=data_df)
            proba = self.pipe.predict_proba(df)
            result = np.where(proba[0] == proba[0].max())[0]
            #if result == 1:
                #db.insert(Battery.stop_cycle)
            return result

log_reg_model = LogisticRegration()