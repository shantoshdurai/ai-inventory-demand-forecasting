import streamlit as st
import pandas as pd

from core.gemini_engine import parse_text_input, parse_image_input, parse_voice_input
from core.stock_tracker import log_transaction
from core.data_importer import process_uploaded_file
from config import GEMINI_API_KEY


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
                                date=item.get("date"), source=source,
                                price=item.get("price"),
                                category=item.get("category"))
                n += 1
        st.success(f"Saved {n} transactions.")
        st.rerun()


def render_input_page():
    st.markdown("""
    <div class="page-title">Input Data</div>
    <div class="page-desc">Log inventory changes through voice, text, photos, or spreadsheets.</div>
    """, unsafe_allow_html=True)

    if not GEMINI_API_KEY:
        st.markdown("""
        <div class="card" style="border-color: rgba(248,113,113,0.3); margin-bottom: 24px;">
            <div style="font-size:14px; color:rgba(240,238,250,0.6); line-height:1.6;">
                <span style="color:#f87171; font-weight:600;">AI Parsing Unavailable</span> —
                Voice, text, and photo parsing require a Gemini API key.
                Spreadsheet import still works. Add <code style="background:rgba(124,110,240,0.15); padding:2px 6px; border-radius:4px; color:#c4b5fd;">GEMINI_API_KEY</code> to enable AI features.
            </div>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Voice", "Text", "Photo Receipt", "Spreadsheet"])

    # ── TAB 1: Voice Input ──
    with tab1:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">Voice Input</div>
            <div style="font-size:14px; color:#999; line-height:1.7;">
                Speak your transactions naturally in English or Hindi. Gemma 4 AI will parse your speech into structured data.<br>
                <span style="color:#7c6ef0; font-style:italic;">"Aaj 10 kilo chawal becha, 5 packet Maggi bhi. Distributor se 50 kilo atta aaya."</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Try to import mic recorder
        try:
            from streamlit_mic_recorder import speech_to_text

            st.markdown('<div class="sh">Tap the microphone to speak</div>', unsafe_allow_html=True)

            transcribed = speech_to_text(
                start_prompt="Start Recording",
                stop_prompt="Stop Recording",
                language="hi-IN",
                just_once=False,
                key="voice_input_stt"
            )

            if transcribed:
                st.markdown(f"""
                <div class="card" style="margin:12px 0; border-color:rgba(124,110,240,0.2);">
                    <div class="card-stat-label">You said</div>
                    <div style="font-size:15px; color:#f0eff5; margin-top:4px;">{transcribed}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Parse with AI", key="btn_voice_parse"):
                    with st.spinner("Gemma 4 is understanding your voice..."):
                        result = parse_voice_input(transcribed)
                        st.session_state['parsed_voice'] = result

            if 'parsed_voice' in st.session_state:
                _show_results(st.session_state['parsed_voice'], "voice")

        except ImportError:
            st.markdown("""
            <div class="card" style="border-color:rgba(251,191,36,0.3); margin-bottom:16px;">
                <div style="font-size:14px; color:rgba(240,238,250,0.6); line-height:1.6;">
                    <span style="color:#fbbf24; font-weight:600;">Mic recorder not installed</span> —
                    Run <code style="background:rgba(124,110,240,0.15); padding:2px 6px; border-radius:4px; color:#c4b5fd;">pip install streamlit-mic-recorder</code> to enable voice input.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Fallback: manual text box for voice transcription
            st.markdown('<div class="sh">Or type what you would say</div>', unsafe_allow_html=True)
            voice_text = st.text_area("Speak naturally", height=80,
                                      placeholder="e.g. aaj 10 kilo chawal becha, 5 packet Maggi bhi...",
                                      key="voice_fallback")
            if st.button("Parse Voice Text", key="btn_voice_fallback"):
                if voice_text:
                    with st.spinner("Parsing..."):
                        result = parse_voice_input(voice_text)
                        st.session_state['parsed_voice'] = result

            if 'parsed_voice' in st.session_state:
                _show_results(st.session_state['parsed_voice'], "voice")

    # ── TAB 2: Text Input ──
    with tab2:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">Text Input</div>
            <div style="font-size:14px; color:#999; line-height:1.7;">
                Type your transaction in plain language. Gemma 4 AI will parse it into structured records.<br>
                <span style="color:#7c6ef0; font-style:italic;">"Sold 5 kg Toor Dal, received 100 packets Maggi from distributor"</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        text = st.text_area("Your transaction", height=100,
                            placeholder="e.g. Sold 10 packets Parle-G, restocked 50 kg Rice, 20 Amul Milk...",
                            key="text_input")

        if st.button("Process Text", key="btn_text"):
            if text:
                with st.spinner("Gemma 4 is parsing..."):
                    result = parse_text_input(text)
                    st.session_state['parsed_text'] = result
            else:
                st.warning("Enter something first.")

        if 'parsed_text' in st.session_state:
            _show_results(st.session_state['parsed_text'], "text")

    # ── TAB 3: Photo Receipt ──
    with tab3:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">Photo Input</div>
            <div style="font-size:14px; color:#999; line-height:1.7;">
                Upload a photo of a receipt, distributor bill, handwritten register, or shelf stock.<br>
                Gemma 4 Vision extracts items and quantities automatically — works with Hindi text too.
            </div>
        </div>
        """, unsafe_allow_html=True)

        img = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])

        if img and st.button("Analyze Photo", key="btn_photo"):
            with st.spinner("Gemma 4 Vision is reading..."):
                st.image(img, width=300)
                result = parse_image_input(img)
                st.session_state['parsed_image'] = result

        if 'parsed_image' in st.session_state:
            _show_results(st.session_state['parsed_image'], "photo")

    # ── TAB 4: Spreadsheet ──
    with tab4:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-bottom:24px;">
            <div style="font-size:15px; color:#f0eff5; font-weight:600; margin-bottom:8px;">Spreadsheet Import</div>
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
