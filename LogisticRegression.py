import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib


def train_model(model_name, df, hyper_parameter):
    
    # Preprocess date and time
    df['Date'] = pd.to_datetime(df['Date'])
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['Time'] = pd.to_datetime(df['Time']).dt.hour  # Only keeping the hour part

    # Define features and target
    X = df[['Latitude', 'Longitude', 'DayOfWeek', 'Time', 'Description']]
    y = df['Type']

    # Text vectorization and model pipeline
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer()),  # Convert text to numerical df
        ('scaler', StandardScaler()),  # Scale other features
        ('classifier', LogisticRegression())  # Logistic regression classifier
    ])

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X[['Latitude', 'Longitude', 'DayOfWeek', 'Time']], y,
                                                        test_size=0.2, random_state=42)

    # Train model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    class_report = classification_report(y_test, y_pred)
    print(classification_report(y_test, y_pred))

    # Save model
    model_file = f'{model_name}.joblib'
    joblib.dump(model, model_file)
    print(f"Model saved to {model_file}")

    return model_file, {"accuracy": accuracy}, {"classification_report": class_report}




