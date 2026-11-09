"""
Geopolitical Intelligence & Risk Monitor
========================================
Streamlit entry point. Run locally with:

    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Geopolitical Intelligence & Risk Monitor",
    page_icon="♞",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.risk import DEFAULT_WEIGHTS  # noqa: E402
from core.theme import CSS  # noqa: E402

st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar: global controls ────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-family:EB Garamond,serif;font-size:1.5rem;line-height:1.1'>♞ Strategic<br>Intelligence</div>"
        "<div style='color:#BDA786;font-size:.7rem;letter-spacing:2.5px;margin:4px 0 10px 0'>GEO-RISK · FINANCE DESK</div>",
        unsafe_allow_html=True,
    )

    if st.button("⟳  Refresh all live data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Feeds auto-refresh every 15 min (cache TTL).")

    with st.expander("Collection settings", expanded=False):
        st.session_state["gdelt_on"] = st.toggle("GDELT global event stream", value=st.session_state.get("gdelt_on", True),
                                                 help="Adds ~250 worldwide articles. Turn off if GDELT is rate-limiting.")
        st.session_state["timespan"] = st.select_slider("GDELT look-back", options=["24h", "48h", "72h", "7d"],
                                                        value=st.session_state.get("timespan", "48h"))

    with st.expander("Risk model weights", expanded=False):
        w = dict(st.session_state.get("weights", DEFAULT_WEIGHTS))
        w["structural"] = st.slider("Structural baseline", 0.0, 1.0, w["structural"], 0.05)
        w["governance"] = st.slider("World Bank stability", 0.0, 1.0, w["governance"], 0.05)
        w["live"] = st.slider("Live news heat", 0.0, 1.0, w["live"], 0.05)
        w["escalation"] = st.slider("Escalation exposure", 0.0, 1.0, w["escalation"], 0.05)
        tot = sum(w.values()) or 1.0
        st.session_state["weights"] = {k: v / tot for k, v in w.items()}
        st.caption("Weights are re-normalised to sum to 1.")

    with st.expander("AI analyst (optional)", expanded=False):
        has_secret = False
        try:
            has_secret = bool(st.secrets.get("ANTHROPIC_API_KEY"))
        except Exception:  # noqa: BLE001 — no secrets file
            pass
        if has_secret:
            st.success("Claude key loaded from secrets.")
        else:
            st.session_state["anthropic_key"] = st.text_input(
                "Anthropic API key", type="password", value=st.session_state.get("anthropic_key", ""),
                help="Optional. Lets Claude rewrite the live 12-point brief as analyst prose. Kept in this session only.")

pages = [
    st.Page("views/home.py", title="Command Brief", icon="♞", default=True),
    st.Page("views/risk_map.py", title="Global Risk Map", icon="🛰️"),
    st.Page("views/dossier.py", title="Country Dossier", icon="📁"),
    st.Page("views/escalation.py", title="Escalation & Strike-back", icon="⚔️"),
    st.Page("views/wire.py", title="Intelligence Wire", icon="📡"),
    st.Page("views/markets_view.py", title="Market Transmission", icon="📈"),
    st.Page("views/calendar_view.py", title="Calendar & Watchlist", icon="🗓️"),
    st.Page("views/method.py", title="Methodology & Sources", icon="📜"),
]
st.navigation(pages).run()
