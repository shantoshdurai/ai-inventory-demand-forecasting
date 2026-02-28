import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import timedelta

# Ensure matplotlib is installed or Prophet throws a minor warning, 
# but Prophet itself works using backend plotting if needed.
try:
    from prophet import Prophet
except ImportError:
    Prophet = None

def train_xgboost(df, steps=14):
    """
    Trains an XGBoost model on the time-series data of a single product.
    Returns the model and a 14-day dataframe forecast.
    """
    if len(df) < 30:
        return None, pd.DataFrame() # Needs at least a month of data for XGBoost

    features = ['day_of_week', 'is_weekend', 'month', 'lag_1', 'lag_7', 'lag_14', 'rolling_7', 'rolling_30']
    X = df[features]
    y = df['qty']

    # Splitting logic (train on everything except last 14 days, evaluate on last 14, 
    # but for simple hackathon, train on ALL to predict FUTURE)
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)
    model.fit(X, y)

    # Let's mock a rolling window future projection
    last_row = df.iloc[-1]
    
    future_dates = [last_row['date'] + timedelta(days=i) for i in range(1, steps + 1)]
    future_rows = []
    
    # Simple iterative autoregression for feature derivation
    current_lag_1 = last_row['lag_1']
    current_lag_7 = last_row['lag_7']
    current_lag_14 = last_row['lag_14']
    current_rolling_7 = last_row['rolling_7']
    current_rolling_30 = last_row['rolling_30']
    
    for i, future_date in enumerate(future_dates):
        row = {
            'date': future_date,
            'day_of_week': future_date.dayofweek,
            'is_weekend': int(future_date.dayofweek in [5, 6]),
            'month': future_date.month,
            'lag_1': current_lag_1,
            'lag_7': current_lag_7,
            'lag_14': current_lag_14,
            'rolling_7': current_rolling_7,
            'rolling_30': current_rolling_30
        }
        future_rows.append(row)
        
    future_df = pd.DataFrame(future_rows)
    X_future = future_df[features]
    predictions = model.predict(X_future)
    
    # Clip negative predictions to 0
    predictions = np.maximum(predictions, 0)
    
    future_df['predicted_qty'] = predictions.round()
    future_df['model_type'] = 'XGBoost'
    
    return model, future_df

def train_prophet(df, steps=14):
    """
    Trains a Facebook Prophet model on single-product time-series.
    Returns the model and the future dataframe forecast.
    """
    if Prophet is None or len(df) < 14:
        return None, pd.DataFrame()
        
    # Prophet requires columns to be strictly named 'ds' and 'y'
    pdf = df[['date', 'qty']].rename(columns={'date': 'ds', 'qty': 'y'})
    
    model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
    model.fit(pdf)

    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    
    # Extract only the future 'steps'
    future_forecast = forecast.tail(steps)[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'predicted_qty'})
    
    # Clip negative predictions to 0
    future_forecast['predicted_qty'] = np.maximum(future_forecast['predicted_qty'], 0).round()
    future_forecast['model_type'] = 'Prophet'
    
    return model, future_forecast
