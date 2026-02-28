import pandas as pd
from datetime import datetime, timedelta
from core.database import get_connection

def prepare_time_series_data(product_id=None):
    """
    Fetches raw transaction data and engineers ML features.
    If product_id is specified, filters data for that product.
    Returns an aggregated daily time-series DataFrame suitable for ML.
    """
    conn = get_connection()
    query = """
    SELECT 
        p.id as product_id, 
        p.name as item, 
        t.date, 
        t.qty, 
        t.type 
    FROM transactions t
    JOIN products p ON t.product_id = p.id
    WHERE t.type = 'sale' AND t.date IS NOT NULL
    """
    
    if product_id:
        query += f" AND p.id = {product_id}"
        
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Convert dates to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Aggregate sales by day and product
    daily_sales = df.groupby(['product_id', 'item', 'date'])['qty'].sum().reset_index()
    
    # Sort chronologically
    daily_sales = daily_sales.sort_values(by=['product_id', 'date'])
    
    # Engineer Features
    # Create a full date range so explicit zeros are represented
    results_list = []
    
    for _, group in daily_sales.groupby('product_id'):
        if len(group) < 10:
             # Not enough data for this specific product to train ML properly
             continue
             
        # Reindex to ensure every day has a row
        min_date = group['date'].min()
        max_date = group['date'].max()
        idx = pd.date_range(start=min_date, end=max_date)
        
        group = group.set_index('date')
        group = group.reindex(idx, fill_value=0)
        group['product_id'] = group['product_id'].replace(0, method='ffill').replace(0, method='bfill')
        group['item'] = group['item'].replace(0, method='ffill').replace(0, method='bfill')
        group = group.reset_index().rename(columns={'index': 'date'})
        
        # Date Features
        group['day_of_week'] = group['date'].dt.dayofweek
        group['is_weekend'] = group['day_of_week'].isin([5, 6]).astype(int)
        group['month'] = group['date'].dt.month
        
        # Lag Features (What were sales 1 day ago? 7 days ago?)
        group['lag_1'] = group['qty'].shift(1).fillna(0)
        group['lag_7'] = group['qty'].shift(7).fillna(0)
        group['lag_14'] = group['qty'].shift(14).fillna(0)
        
        # Rolling Averages
        group['rolling_7'] = group['qty'].rolling(window=7, min_periods=1).mean()
        group['rolling_30'] = group['qty'].rolling(window=30, min_periods=1).mean()
        
        results_list.append(group)
        
    if not results_list:
        return pd.DataFrame()
        
    final_df = pd.concat(results_list, ignore_index=True)
    return final_df
