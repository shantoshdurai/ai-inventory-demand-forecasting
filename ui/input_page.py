import streamlit as st
import pandas as pd

from core.gemini_engine import parse_text_input, parse_image_input
from core.stock_tracker import log_transaction
from core.data_importer import process_uploaded_file

def _process_gemini_output(parsed_data, source="voice"):
    if not parsed_data:
        st.warning("Nothing could be parsed.")
        return
    
    if isinstance(parsed_data, list) and len(parsed_data) > 0 and "error" in parsed_data[0]:
        st.error(f"Error AI Processing: {parsed_data[0]['error']}")
        return

    st.success("Successfully Parsed Details:")
    # Display table for confirmation
    st.table(parsed_data)

    if st.button("Confirm and Log to DB", key=f"confirm_{source}"):
        count = 0
        for item in parsed_data:
            if "item" in item and "qty" in item:
                txn_type = item.get("type", "sale")
                date = item.get("date")
                log_transaction(item["item"], float(item["qty"]), txn_type=txn_type, date=date, source=source)
                count += 1
        st.success(f"Successfully logged {count} transactions to database!")
        st.rerun()

def render_input_page():
    st.subheader("Data Input")
    st.write("Log sales or restock inventory using Voice/Text, Photo, or File Upload.")
    
    tab1, tab2, tab3 = st.tabs(["🗣️ Text / Voice", "📸 Photo Receipt", "📁 CSV / Excel Upload"])
    
    with tab1:
        st.write("### Log Transactions via Text")
        st.info("💡 You can type naturally, e.g., 'Sold 5 strips of Dolo 650' or 'Received 100 boxes of Crocin'")
        user_text = st.text_area("Describe your sales or restocks:", height=100)
        
        if st.button("Process Text"):
            if user_text:
                with st.spinner("AI is thinking..."):
                    parsed_data = parse_text_input(user_text)
                    st.session_state['parsed_text'] = parsed_data
            else:
                st.warning("Please enter some text.")

        if 'parsed_text' in st.session_state:
            _process_gemini_output(st.session_state['parsed_text'], source="text")

    with tab2:
        st.write("### Upload a Photo")
        st.info("💡 Upload photos of handwritten logs, receipts from distributors, or shelf labels.")
        image_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        
        if image_file and st.button("Analyze Photo"):
            with st.spinner("AI is analyzing the image..."):
                st.image(image_file, width=300)
                parsed_image_data = parse_image_input(image_file)
                st.session_state['parsed_image'] = parsed_image_data
        
        if 'parsed_image' in st.session_state:
            _process_gemini_output(st.session_state['parsed_image'], source="photo")
            
    with tab3:
        st.write("### Bulk File Import")
        st.info("💡 Upload historical data from spreadsheets. The AI will try to auto-detect the Item and Quantity columns.")
        file = st.file_uploader("Choose a spreadsheet file", type=["csv", "xlsx"])
        
        if file and st.button("Import Data"):
            with st.spinner("Importing and Processing..."):
                result = process_uploaded_file(file)
                if result.get("success"):
                    st.success(f"Successfully imported {result['count']} transactions!")
                else:
                    st.error(f"Import Failed: {result.get('error')}")
