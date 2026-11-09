"""Calendar & Watchlist — dated catalysts and theatre indicators."""
from datetime import date, datetime, timezone

import pandas as pd
import streamlit as st

from data.brief import CALENDAR
from data.theatres import THEATRES
from views.common import chip, footer, header, show_df

header("Calendar & Watchlist", "Dated catalysts and the tripwires that would change the assessment.")

today = datetime.now(timezone.utc).date()
cal = pd.DataFrame(CALENDAR, columns=["date", "event", "theatre", "why it matters"])
cal["in (days)"] = cal["date"].apply(lambda d: (d - today).days)
show_past = st.toggle("Show past events", value=False)
view = cal if show_past else cal[cal["in (days)"] >= 0]
show_df(view.sort_values("date"), hide_index=True)
st.caption("Edit `data/brief.py → CALENDAR` to add events. Dates marked 'approx.' should be verified.")

st.markdown("### Indicators & warnings by theatre")
for t in sorted(THEATRES, key=lambda x: -x["intensity"]):
    with st.expander(f"{t['name']} — intensity {t['intensity']}"):
        st.markdown(" ".join(chip(i, cls="chip-theme") for i in t["indicators"]), unsafe_allow_html=True)
        trip = pd.DataFrame([{"actor": r["actor"], "action": r["action"], "tripwire": r["tripwire"],
                              "prob %": round(r["prob"] * 100)} for r in t["retaliation"]])
        show_df(trip, hide_index=True)
footer()
