import pandas as pd
from sklearn.linear_model import LogisticRegression
import os
from sklearn.metrics import accuracy_score, classification_report


def is_model_valid(model, model_file, df, model_accuracy):
    if model_file == 'accident_prediction_model_final.pkl':
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

        # Predict the labels on the test set using the calibrated model
        y_pred = model.predict(X)

        # Evaluate the model
        accuracy_for_task = accuracy_score(y, y_pred)

        print(accuracy_for_task)
        print(classification_report(y, y_pred))

        threshold = 0.05
        accuracy_difference = model_accuracy['accuracy'] - accuracy_for_task
        if (accuracy_difference / model_accuracy) > threshold:
            print("Model is invalid.")
            return False
        else:
            print("Model is valid.")
            return True

    else:
        if model_file == 'testing2.joblib':
            # Preprocess date and time
            df['Date'] = pd.to_datetime(df['Date'])
            df['DayOfWeek'] = df['Date'].dt.dayofweek
            df['Time'] = pd.to_datetime(df['Time']).dt.hour  # Only keeping the hour part

            # Define features and target
            X = df[['Latitude', 'Longitude', 'DayOfWeek', 'Time', 'Description']]
            y = df['Type']

            model.fit(X, y)

            y_pred = model.predict(X)
            accuracy_for_task = accuracy_score(y, y_pred)

            threshold = 0.05
            accuracy_difference = model_accuracy['accuracy'] - accuracy_for_task
            if (accuracy_difference / model_accuracy) > threshold:
                print("Model is invalid.")
                return False
            else:
                print("Model is valid.")
                return True


