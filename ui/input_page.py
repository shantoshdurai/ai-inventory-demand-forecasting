import streamlit as st
import pandas as pd

from core.gemini_engine import parse_text_input, parse_image_input
from core.stock_tracker import log_transaction
from core.data_importer import process_uploaded_file

def _show_results(parsed, source="text"):
    if not parsed:
        st.warning("Nothing extracted.")
        return
    if isinstance(parsed, list) and len(parsed) > 0 and "error" in parsed[0]:
        st.error(f"Error: {parsed[0]['error']}")
        return

    st.markdown('<div class="sh">Extracted Data</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(parsed), hide_index=True, use_container_width=True)

    if st.button("Confirm & Save", key=f"save_{source}"):
        n = 0
        for item in parsed:
            if "item" in item and "qty" in item:
                log_transaction(item["item"], float(item["qty"]),
                                txn_type=item.get("type", "sale"),
                                date=item.get("date"), source=source)
                n += 1
        st.success(f"Saved {n} transactions.")
        st.rerun()

def render_input_page():
    st.markdown("""
    <div class="page-title">Input Data</div>
    <div class="page-desc">Log inventory changes through natural language, photos, or spreadsheets.</div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Text / Voice", "Photo Receipt", "Spreadsheet"])
    
    with tab1:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        # ── Instruction card ──
        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">How it works</div>
            <div style="font-size:14px; color:#999; line-height:1.7;">
                Type your transaction in plain language. Our Gemini AI will parse it into structured records.<br>
                <span style="color:#7c6ef0; font-style:italic;">"Sold 5 strips of Dolo 650 and received 100 Crocin from distributor"</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        text = st.text_area("Your transaction", height=100,
                            placeholder="e.g. Sold 10 Cetirizine, restocked 200 Band-Aid...")
        
        if st.button("Process Text", key="btn_text"):
            if text:
                with st.spinner("Parsing..."):
                    result = parse_text_input(text)
                    st.session_state['parsed_text'] = result
            else:
                st.warning("Enter something first.")
        
        if 'parsed_text' in st.session_state:
            _show_results(st.session_state['parsed_text'], "text")

    with tab2:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">How it works</div>
            <div style="font-size:14px; color:#999; line-height:1.7;">
                Upload a photo of a handwritten log, printed receipt, or shelf label.<br>
                Gemini Vision extracts items and quantities automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        img = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        
        if img and st.button("Analyze Photo", key="btn_photo"):
            with st.spinner("Analyzing..."):
                st.image(img, width=300)
                result = parse_image_input(img)
                st.session_state['parsed_image'] = result
        
        if 'parsed_image' in st.session_state:
            _show_results(st.session_state['parsed_image'], "photo")
            
    with tab3:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">How it works</div>
            <div style="font-size:14px; color:#999; line-height:1.7;">
                Upload a CSV or Excel file. Columns named <code style="background:rgba(124,110,240,0.15); padding:2px 6px; border-radius:4px; color:#c4b5fd;">item</code>, 
                <code style="background:rgba(124,110,240,0.15); padding:2px 6px; border-radius:4px; color:#c4b5fd;">qty</code>, and 
                <code style="background:rgba(124,110,240,0.15); padding:2px 6px; border-radius:4px; color:#c4b5fd;">date</code> are auto-detected.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        file = st.file_uploader("Upload file", type=["csv", "xlsx"])
        
        if file and st.button("Import", key="btn_import"):
            with st.spinner("Importing..."):
                res = process_uploaded_file(file)
                if res.get("success"):
                    st.success(f"Imported {res['count']} records.")
                else:
                    st.error(f"Failed: {res.get('error')}")
