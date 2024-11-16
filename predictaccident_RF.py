import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.calibration import CalibratedClassifierCV
import numpy as np
import joblib


def train_model(model_name, df, hyper_parameters):
    """
    Function to train a calibrated random forest model for accident prediction.

    Parameters:
    - file_path (str): Path to the CSV file containing the dataset.

    Returns:
    - dict: A dictionary containing the trained model, calibration, and evaluation metrics.
    """

    # One-hot encode the 'Type' column without dropping any category
    df_encoded = pd.get_dummies(df, columns=['Type'], drop_first=False)

    # Identify the new one-hot encoded columns (they will have 'Type_' as a prefix)
    new_columns = [col for col in df_encoded.columns if col.startswith('Type_')]

    # Convert the new one-hot encoded columns to integers
    df_encoded[new_columns] = df_encoded[new_columns].astype(int)

    # Drop the 'Description' and 'Date' columns
    if 'Description' in df_encoded.columns and 'Date' in df_encoded.columns:
        df_encoded = df_encoded.drop(columns=['Description', 'Date'])

    # Convert 'Time' column to total minutes since midnight
    df_encoded['Time'] = pd.to_datetime(df_encoded['Time'], format='%H:%M:%S')
    df_encoded['Time'] = df_encoded['Time'].dt.hour * 60 + df_encoded['Time'].dt.minute

    # Define the features and target
    incident_columns = ['Type_Roadwork', 'Type_Heavy Traffic', 'Type_Vehicle breakdown']
    X = df_encoded[['Latitude', 'Longitude', 'Time'] + incident_columns]
    y = df_encoded['Type_Accident']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize RandomForestClassifier with optimized parameters
    rf_model = RandomForestClassifier(
        class_weight=hyper_parameters.class_weight,
        max_depth=int(hyper_parameters.max_depth),
        max_features=hyper_parameters.max_features,
        min_samples_leaf=int(hyper_parameters.min_samples_leaf),
        min_samples_split=int(hyper_parameters.min_samples_split),
        n_estimators=int(hyper_parameters.n_estimators),
        random_state=42
    )

    # Train the model
    rf_model.fit(X_train, y_train)

    # Calibrate the RandomForest model using Platt scaling (CalibratedClassifierCV with method='sigmoid')
    calibrated_rf_model = CalibratedClassifierCV(rf_model, method=hyper_parameters.method, cv=hyper_parameters.cv)

    # Fit the calibrated model
    calibrated_rf_model.fit(X_test, y_test)

    # Predict the labels on the test set using the calibrated model
    y_pred = calibrated_rf_model.predict(X_test)
    y_prob = calibrated_rf_model.predict_proba(X_test)[:, 1]  # Get the predicted probabilities for the positive class

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred)

    model_file = f'{model_name}.pkl'
    joblib.dump(calibrated_rf_model, model_file)

    # Return the trained model, calibration, and evaluation metrics
    return model_file, {"accuracy": accuracy}, {"confusion_matrix": conf_matrix,
        "classification_report": class_report,
        "predicted_probabilities": y_prob}
