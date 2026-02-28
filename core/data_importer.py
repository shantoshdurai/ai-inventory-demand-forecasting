import pandas as pd
from core.stock_tracker import log_transaction

def process_uploaded_file(uploaded_file):
    """
    Reads a CSV or Excel file, auto-detects columns, 
    and logs the corresponding transactions.
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        columns = df.columns.str.lower()
        
        # Simple auto-detect heuristics
        item_col = next((c for c in columns if 'item' in c or 'product' in c or 'name' in c), None)
        qty_col = next((c for c in columns if 'qty' in c or 'quantity' in c or 'count' in c), None)
        type_col = next((c for c in columns if 'type' in c or 'status' in c or 'action' in c), None)
        date_col = next((c for c in columns if 'date' in c or 'time' in c), None)
        
        if not item_col or not qty_col:
            return {"success": False, "error": "Could not auto-detect Item and Quantity columns."}
            
        success_count = 0
        for _, row in df.iterrows():
            item = str(row[item_col])
            qty = float(row[qty_col])
            
            txn_type = str(row[type_col]).lower() if type_col else "initial"
            if txn_type not in ["sale", "restock", "initial"]:
                txn_type = "initial"
                
            date_val = str(row[date_col]) if date_col and not pd.isna(row[date_col]) else None
            
            log_transaction(item, qty, txn_type=txn_type, date=date_val, source="csv")
            success_count += 1
            
        return {"success": True, "count": success_count}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
