from ML_classes import LogisticRegration as LR

bat_types = ["a","b","c"]
logistic_regression_models = [(f"{type}",LR(type).model_fit()) for type in bat_types]
