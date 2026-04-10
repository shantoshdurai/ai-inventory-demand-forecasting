import streamlit as st
from config import GEMINI_API_KEY
from core.insights_engine import get_inventory_summary_text
from core.gemini_engine import chat_with_advisor, analyze_performance


# ── Demo responses for when no API key is configured ──
DEMO_RESPONSES = {
    "default": """Namaste! Based on your Kirana shop data, here's a quick overview:

**Top Sellers (Last 30 Days):**
- **Amul Milk** — your highest volume item (~35 units/day). Make sure daily supply is locked in.
- **Parle-G Biscuits** — consistent seller at ~30 packs/day. Good margins for low price point.
- **Maggi Noodles** — strong daily pull (~25/day), especially on weekends.

**Watch List:**
- MDH Garam Masala is moving slower than expected — check if a competing brand is stealing share
- Saffola Gold Oil has lower demand than Fortune — consider reducing shelf allocation

**Quick Win:** Bundle Maggi + Lays as an evening snack combo for weekends. Your data shows both spike on Saturdays.

What specific product or category would you like me to analyze deeper?""",

    "restock": """**Restock Priority List for This Week:**

| Priority | Product | Daily Rate | Days Left | Order Qty (14-day) |
|----------|---------|-----------|-----------|-------------------|
| 1 | Amul Milk (500ml) | ~35/day | ~2 days | 500 packets |
| 2 | Parle-G Biscuits | ~30/day | ~3 days | 420 packets |
| 3 | Maggi Noodles | ~25/day | ~4 days | 350 packets |
| 4 | Britannia Bread | ~12/day | ~5 days | 170 packets |
| 5 | Eggs (dozen) | ~10/day | ~6 days | 140 dozens |

**Order quantities include a 20% safety buffer.**

Toor Dal, Atta, and Rice have adequate stock for 10+ days. Next restock for staples can wait until next week.

Want me to estimate the total order cost for this list?""",

    "risk": """**Risk Analysis for Your Kirana Shop:**

**HIGH RISK:**
- **Milk stockout** — At 35 units/day, Amul Milk runs out fastest. Set up daily delivery if not already.
- **Bread freshness** — Britannia Bread has 2-3 day shelf life. Order in smaller, more frequent batches.

**MEDIUM RISK:**
- **Oil price volatility** — Cooking oil prices fluctuate. Consider locking in a 2-week supply with your distributor.
- **Overstock on Saffola Gold** — Moving only 3/day vs Fortune's 7/day. Too much capital tied up.

**SEASONAL ALERT:**
- Monsoon is approaching — expect **+50% spike** in Tea, Maggi, and Bread.
- Start increasing orders for Tata Tea and Maggi from next week.

**Cash Flow Tip:** Your highest margin items are MDH Masala (₹85) and Nescafe (₹160). Push these actively.""",

    "performance": """**Business Performance Report**

**Health Score: 7.5/10**

**What's Working Well:**
- Strong daily foot traffic indicated by high Milk and Bread sales
- Good product mix across all categories
- Consistent restocking cadence (every 10-14 days)

**Areas to Improve:**
1. **Reduce dead stock** — Saffola Gold and Volini equivalents move slowly. Cut next order by 40%.
2. **Margin optimization** — Parle-G sells 30/day but at only ₹10/pack. Cross-sell with higher margin Tea or Coffee.
3. **Weekend strategy** — Sales spike 35% on weekends. Stock up Thursday evening.

**This Month's Projection:**
- Estimated revenue: ₹2,50,000 - ₹2,80,000
- Top revenue contributor: Aashirvaad Atta (volume x price)
- Biggest margin opportunity: Push Nescafe and MDH Masala bundles

Want me to deep-dive into any category?""",

    "forecast": """Here's what our ML models predict for the next 2 weeks:

**Demand Forecast Summary:**
| Product | Next 14 Days | Trend | Action |
|---------|-------------|-------|--------|
| Amul Milk | ~490 packets | Stable | Daily supply essential |
| Parle-G | ~420 packets | Stable | Order 450 (buffer) |
| Maggi | ~350 packets | Rising | Monsoon boost coming |
| Rice (5kg) | ~84 bags | Stable | Month-end spike expected |
| Toor Dal | ~112 kg | Stable | Stock adequate |
| Tea | ~56 packets | Rising | Winter/monsoon uptick |

**Confidence Level:** High (based on 6 months of data)

**Key Insight:** Maggi and Tea demand will surge in monsoon. Pre-order 30% extra starting next week.

Go to the **Forecast** page for product-specific charts with XGBoost or Prophet models."""
}


def _get_demo_response(user_msg):
    msg_lower = user_msg.lower()
    if any(w in msg_lower for w in ["restock", "reorder", "order", "kharidna", "mangwao", "supply"]):
        return DEMO_RESPONSES["restock"]
    elif any(w in msg_lower for w in ["risk", "danger", "problem", "issue", "kharab", "dikkat"]):
        return DEMO_RESPONSES["risk"]
    elif any(w in msg_lower for w in ["performance", "kaisa", "health", "report", "overall", "review"]):
        return DEMO_RESPONSES["performance"]
    elif any(w in msg_lower for w in ["forecast", "predict", "future", "next week", "agle hafte", "trend"]):
        return DEMO_RESPONSES["forecast"]
    else:
        return DEMO_RESPONSES["default"]


def render_advisor_page():
    st.markdown("""
    <div class="page-title">AI Advisor</div>
    <div class="page-desc">Your AI-powered Kirana shop consultant. Ask anything about inventory, trends, and business strategy — by text or voice.</div>
    """, unsafe_allow_html=True)

    if not GEMINI_API_KEY:
        st.markdown("""
        <div class="card" style="border-color: rgba(124, 110, 240, 0.3); margin-bottom: 24px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="font-size:18px; color:#7c6ef0;">&#9672;</span>
                <span style="font-size:15px; font-weight:600; color:#f0eff5;">Demo Mode</span>
            </div>
            <div style="font-size:13px; color:rgba(240,238,250,0.5); line-height:1.6;">
                You're seeing pre-computed AI responses. Add a <code style="background:rgba(124,110,240,0.15); padding:2px 6px; border-radius:4px; color:#c4b5fd;">GEMINI_API_KEY</code>
                to enable live Gemma 4 31B responses with voice conversation powered by real-time inventory analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Quick Actions ──
    st.markdown('<div class="sh">Quick Actions</div>', unsafe_allow_html=True)

    qa_cols = st.columns(2)
    with qa_cols[0]:
        if st.button("Get Full Performance Report", key="perf_report", use_container_width=True):
            st.session_state["advisor_input"] = "Give me a full performance report of my shop"
    with qa_cols[1]:
        if st.button("Seasonal Preparation Plan", key="seasonal_plan", use_container_width=True):
            st.session_state["advisor_input"] = "What should I prepare for this season?"

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Suggested Questions ──
    st.markdown('<div class="sh">Try asking</div>', unsafe_allow_html=True)

    suggestions = [
        "What should I restock?",
        "What are my biggest risks?",
        "Which products are trending?",
        "Demand forecast summary",
    ]

    cols = st.columns(len(suggestions))
    for i, (col, suggestion) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                st.session_state["advisor_input"] = suggestion

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Chat History ──
    if "advisor_history" not in st.session_state:
        st.session_state["advisor_history"] = []

    for msg in st.session_state["advisor_history"]:
        if msg["role"] == "user":
            source_badge = ""
            if msg.get("source") == "voice":
                source_badge = '<span style="background:rgba(74,222,128,0.15); color:#4ade80; font-size:11px; padding:2px 8px; border-radius:8px; margin-left:8px;">voice</span>'
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-end; margin-bottom:16px;">
                <div style="background:rgba(124,110,240,0.15); border:1px solid rgba(124,110,240,0.2);
                     border-radius:16px 16px 4px 16px; padding:14px 20px; max-width:75%;
                     color:#f0eff5; font-size:14px; line-height:1.6;">
                    {msg["content"]}{source_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex; justify-content:flex-start; margin-bottom:16px;">
                <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
                     border-radius:16px 16px 16px 4px; padding:14px 20px; max-width:85%;
                     color:rgba(240,238,250,0.85); font-size:14px; line-height:1.7;">
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Voice Input for Advisor ──
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    input_method = st.radio("Input method", ["Type", "Voice"], horizontal=True, label_visibility="collapsed", key="advisor_input_method")

    voice_text = None
    if input_method == "Voice":
        try:
            from streamlit_mic_recorder import speech_to_text

            st.markdown("""
            <div style="font-size:13px; color:rgba(240,238,250,0.4); margin-bottom:8px;">
                Tap to speak in Hindi or English — ask about restocking, risks, sales performance, forecasts...
            </div>
            """, unsafe_allow_html=True)

            voice_text = speech_to_text(
                start_prompt="Speak to Advisor",
                stop_prompt="Stop",
                language="hi-IN",
                just_once=False,
                key="advisor_voice_stt"
            )

            if voice_text:
                st.markdown(f"""
                <div class="card" style="margin:8px 0; border-color:rgba(74,222,128,0.2);">
                    <div style="font-size:12px; color:rgba(240,238,250,0.4); margin-bottom:4px;">Heard:</div>
                    <div style="font-size:15px; color:#f0eff5;">{voice_text}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Send to Advisor", key="send_voice_advisor", use_container_width=True):
                    st.session_state["advisor_input"] = voice_text
                    st.session_state["advisor_input_source"] = "voice"

        except ImportError:
            st.info("Install `streamlit-mic-recorder` for voice input. Falling back to text.")
            input_method = "Type"

    if input_method == "Type":
        default_val = st.session_state.pop("advisor_input", "")
        user_input = st.text_input(
            "Message",
            value=default_val,
            placeholder="Ask about inventory, restocking, trends, risks... (Hindi/English)",
            label_visibility="collapsed",
            key="advisor_chat_input"
        )
    else:
        user_input = st.session_state.pop("advisor_input", "")

    col_send, col_clear = st.columns([6, 1])
    with col_send:
        send = st.button("Send", key="advisor_send", use_container_width=True)
    with col_clear:
        if st.button("Clear", key="advisor_clear", use_container_width=True):
            st.session_state["advisor_history"] = []
            st.rerun()

    if send and user_input and user_input.strip():
        source = st.session_state.pop("advisor_input_source", "text")

        st.session_state["advisor_history"].append({
            "role": "user",
            "content": user_input.strip(),
            "source": source
        })

        with st.spinner("Gemma 4 is thinking..."):
            if GEMINI_API_KEY:
                context = get_inventory_summary_text()
                # Use performance analysis for specific keywords
                msg_lower = user_input.lower()
                if any(w in msg_lower for w in ["performance report", "full report", "overall review", "health score"]):
                    response = analyze_performance(context)
                else:
                    response = chat_with_advisor(
                        user_input.strip(),
                        context,
                        chat_history=st.session_state["advisor_history"]
                    )
            else:
                response = _get_demo_response(user_input.strip())

        st.session_state["advisor_history"].append({
            "role": "assistant",
            "content": response
        })
        st.rerun()
