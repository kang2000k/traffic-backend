import joblib
import pandas as pd


def load_model(model_type_name, model_file):
    model = None
    if model_type_name == 'predictaccident_RF':
        model = joblib.load(model_file)
        return model
    elif model_type_name == 'LogisticRegression':
        model = joblib.load(model_file)
        return model
    else:
        print("Unsupported model type.")
        return model