import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

def ml(df_processed, service_attributes):
    # select features and target variable
    feature_cols = [
        'Gender', 'Age', 'Customer Type', 'Type of Travel', 'Class',
        'Flight Distance', 'Departure Delay in Minutes', 'Arrival Delay in Minutes'
    ] + service_attributes
    X = df_processed[feature_cols]
    y = df_processed['satisfaction_binary']

    # encode categorical variables
    cat_cols = X.select_dtypes(include=['object', 'category']).columns
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    # split train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # train
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model.fit(X_train, y_train)

    # evaluate accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # prediction function
    def predict_func(passenger_info: dict):
        input_df = pd.DataFrame([passenger_info])
        for col in feature_cols:
            if col not in input_df.columns:
                input_df[col] = 0
        for col in cat_cols:
            if col in input_df.columns:
                input_df[col] = encoders[col].transform(input_df[col].astype(str))
        input_df = input_df[feature_cols]
        pred = model.predict(input_df)[0]
        return 'Satisfied' if pred == 1 else 'Neutral or Dissatisfied'

    return accuracy, predict_func
