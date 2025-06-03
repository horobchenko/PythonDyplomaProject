from pathlib import Path
import pandas as pd

class LogisticRegration:

    bat_type: int
    data_url: Path

    def __init__(self, bat_type):
       self.bat_type = bat_type
       #self.data_url =

    def _make_df(self):
        ...

    def model_fit(self):
        ...

    def _preprocess(self):
        ...

    def predict(self, user_id):
        last_cycle_number = 0
        last_cycle_date = 0
        result = 0
        return last_cycle_number, last_cycle_date, result