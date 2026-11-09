"""
Analyst baseline brief, calendar and source register — as of 10 Nov 2026.

The home page shows the LIVE 12-point wire by default. This analyst baseline is
the fallback when feeds are unreachable, and the reference point the live wire
is compared against. Update it whenever you re-baseline.
"""
from datetime import date

BRIEF_AS_OF = "10 November 2026"

ANALYST_BRIEF = [
    {"tag": "Hormuz", "theatre": "hormuz", "level": "SEVERE",
     "what": "US blockade of Iranian ports continues. Iran claims fresh mine strikes on tankers, and the US carried out 'minor' strikes on Qeshm air defences (2 & 6 Nov). Trump and Qatar's leadership reviewed a 48-hour de-escalation framework on 9 Nov.",
     "so_what": "Brent fell ~7% w/w to ~$94–98 as deal hopes compressed the risk premium. The premium is binary: either a reopening or a renewed US campaign with Iranian retaliation 'without geographical limits'.",
     "next": "Watch for a framework readout and any US order to resume operations. Base case is armed stalemate (40%), then reopening (35%) and escalation (25%)."},
    {"tag": "Gulf exports", "theatre": "hormuz", "level": "HIGH",
     "what": "Iraq agreed an emergency US-backed offshore crude lane near Oman. Cumulative war losses are ~$60bn. War-risk cover is suspended for many VLCCs, which are diverting via the Cape.",
     "so_what": "Partial Gulf barrels return at higher freight and insurance cost. That supports Dubai–Brent spreads and tanker equities, and hurts Asian refiners' margins.",
     "next": "Insurance review of the Oman lane; first cargoes loaded; OPEC+ ministerial on 29 Nov (2027 quotas)."},
    {"tag": "Red Sea", "theatre": "red_sea", "level": "HIGH",
     "what": "Houthis claimed an attack on Aramco offices in Riyadh (8 Nov). Suez transits are down by more than 50%. Houthis hold Yemen's Red Sea coast.",
     "so_what": "Both chokepoints are impaired at once. Saudi Arabia's Yanbu bypass is the system's single point of failure. Container freight and European goods inflation stay elevated.",
     "next": "Any strike near Yanbu/Jeddah would be a step-change for crude. The coalition is expected to answer with an air campaign."},
    {"tag": "Russia–Ukraine", "theatre": "russia_ukraine", "level": "SEVERE",
     "what": "Trilateral US–Russia–Ukraine talks in Abu Dhabi (10–11 Nov), without European representation. They follow Russian strikes on Kyiv (6–8 Nov: 36 ballistic missiles, 172 drones; 600k+ without power) and Ukrainian deep strikes on Yaroslavl refining and Oryol microelectronics.",
     "so_what": "A moratorium on energy-infrastructure strikes is the market variable: bearish for TTF and diesel cracks, bullish for Ukrainian Eurobonds, and a mild headwind for European defence.",
     "next": "Moratorium (30%) vs winter infrastructure war (55%). European exclusion raises the odds of transatlantic friction."},
    {"tag": "US politics", "theatre": "us_china_trade", "level": "ELEVATED",
     "what": "The 3 Nov midterms produced Democratic gains and a divided Congress, which is now reviewing foreign security commitments and defence appropriations. Trump called the Iran war 'part of' the losses.",
     "so_what": "This raises the incentive for a deal-seeking posture on Iran and Ukraine. It also complicates tariff authority and war funding. Expect more executive-led foreign policy.",
     "next": "Appropriations fights, War Powers resolutions, and confirmation of Section 122 tariff extensions."},
    {"tag": "Macro / Fed", "theatre": None, "level": "ELEVATED",
     "what": "October payrolls came in at +165k (more than double consensus), with unemployment at 4.1%. Markets price ~80% odds of a Fed hike in December. CPI is due 10 Nov.",
     "so_what": "An energy-led 'stagflation lock' narrows policy options. The S&P fell 2.7% w/w, the Nasdaq is in correction, and the energy sector lost ~12% w/w as oil fell.",
     "next": "CPI and PPI this week. A hot print alongside a Hormuz flare-up is the worst combination for risk assets."},
    {"tag": "Taiwan Strait", "theatre": "taiwan", "level": "HIGH",
     "what": "More than 50 PLAN and China Coast Guard vessels are deployed from southern Japan to the Philippine Sea, with the Liaoning group east of the Philippines. The PRC is staging repeated Pratas incursions and interfering in Taiwan's 28 Nov local elections.",
     "so_what": "Nov–Dec is the historical window for encirclement drills. A named drill typically knocks 8–12% off TSMC and 6% off the SOX before fading. The $14bn US arms package remains a trigger.",
     "next": "Gray-zone status quo 60%; large drill/quarantine scare 32%; blockade tail 8%."},
    {"tag": "China politics", "theatre": "taiwan", "level": "ELEVATED",
     "what": "The Fifth Plenum expelled 33 senior officials, including CMC Vice Chairman Zhang Youxia. The active CMC leadership is now just Xi and Zhang Shengmin. October PPI was +5.7% against CPI of +0.7%.",
     "so_what": "Command-cohesion questions cut both ways: they reduce near-term invasion readiness but increase the risk of signalling through coercion. Rising producer prices erode China's export-deflation tailwind for the world.",
     "next": "Watch PLA appointments and Eastern Theater announcements."},
    {"tag": "US–China trade", "theatre": "us_china_trade", "level": "ELEVATED",
     "what": "The Busan tariff truce, due to lapse on 10 Nov, has reportedly been extended about two months to January 2027 with the 10% tariff kept. Chips, rare earths and shipbuilding remain contested.",
     "so_what": "A tariff cliff in early Q1 2027 drives inventory front-loading and holds back capex. China keeps rare-earth leverage in reserve.",
     "next": "Watch for BIS chip-control actions and Chinese rare-earth licensing data. Snap-back risk is ~30%."},
    {"tag": "OPEC+", "theatre": "hormuz", "level": "MODERATE",
     "what": "OPEC+ held December quotas at baseline (Saudi Arabia 10.5 mb/d, Russia 9.9, Iraq 4.4). The 2027 quota meeting is on 29 Nov.",
     "so_what": "No supply offset to Gulf disruption. If Hormuz reopens, a looming 2027 surplus caps the upside, which is why analysts see a downside bias on any deal.",
     "next": "29 Nov ministerial. Watch Saudi rhetoric on market share."},
    {"tag": "Venezuela", "theatre": "venezuela", "level": "ELEVATED",
     "what": "After Maduro's capture (3 Jan), acting president Delcy Rodríguez governs with US recognition. The oil sector has partially reopened, but majors are cautious and no election date has been set.",
     "so_what": "Heavy-crude upside is slow. PDVSA and sovereign bonds trade on the recovery path. Colectivos and the ELN pose security risks to US personnel.",
     "next": "OFAC licensing, PDVSA output, and any election roadmap."},
    {"tag": "Africa / health", "theatre": "great_lakes", "level": "HIGH",
     "what": "The Bundibugyo Ebola outbreak in the DRC has caused more than 5,230 deaths across eight provinces, with cross-border cases in Kenya, Uganda and Nigeria. WHO holds an emergency briefing on 12 Nov. In the Sahel, JNIM continues to strangle Bamako.",
     "so_what": "A PHEIC declaration would bring travel and trade restrictions, hitting cobalt logistics, airlines and African FX. Sahel gold and uranium assets face nationalisation and security risk.",
     "next": "WHO decision on 12 Nov. Urban transmission in Nairobi, Kampala or Lagos would be the escalation signal."},
]
CALENDAR = [
    (date(2026, 11, 10), "US CPI (October)", "Macro", "Fed December hike pricing (~80%)"),
    (date(2026, 11, 10), "Abu Dhabi trilateral talks · day 1", "Russia–Ukraine", "Energy-strike moratorium?"),
    (date(2026, 11, 11), "Abu Dhabi trilateral talks · day 2", "Russia–Ukraine", "Framework readout"),
    (date(2026, 11, 11), "Veterans Day — US bond market closed", "Macro", "Thin liquidity"),
    (date(2026, 11, 12), "WHO emergency briefing on Ebola (DRC)", "Great Lakes", "Possible PHEIC"),
    (date(2026, 11, 12), "UK preliminary Q3 GDP", "Macro", ""),
    (date(2026, 11, 13), "US PPI · Euro-area GDP", "Macro", ""),
    (date(2026, 11, 19), "Future of Defense Summit (Washington)", "US defence", "Post-midterm defence posture"),
    (date(2026, 11, 28), "Taiwan local elections", "Taiwan", "PRC interference; drill trigger"),
    (date(2026, 11, 29), "OPEC+ ministerial — 2027 quotas", "Energy", "Supply response to Gulf disruption"),
    (date(2026, 12, 9), "FOMC decision (approx. — verify)", "Macro", "Hike risk"),
    (date(2027, 1, 10), "US–China truce extension expiry (approx.)", "US–China", "Tariff cliff"),
    (date(2027, 3, 1), "KSG Intelligence & Strategy internship starts", "—", ""),
]

SOURCES = [
    ("Saxo Morning Brew, 9 Nov 2026", "https://www.home.saxo/en-ch/content/articles/morning-brew/november-9-2026-09112026"),
    ("Au79 Geopolitical Intelligence, 9 Nov 2026", "https://martyau79.substack.com/p/09nov2026-geopolitical-intelligence"),
    ("Hormuz Strait Monitor — crisis timeline", "https://hormuzstraitmonitor.com/crisis-timeline/"),
    ("2026 Strait of Hormuz crisis (wiki mirror)", "https://www.doc.surf/wiki/2026-strait-of-hormuz-crisis"),
    ("PSU Watch — crude tumbles on US–Iran diplomacy, 9 Nov", "https://psuwatch.com/newsupdates/crude-oil-futures-tumble-5-as-us-iran-diplomacy-hopes-ease-supply-fears"),
    ("Political.org China–Taiwan briefing, 3 Nov 2026", "https://political.org/china-taiwan-archive/cn-briefing-2026-11-03/"),
    ("2026 US intervention in Venezuela (wiki mirror)", "https://www.doc.surf/wiki/2026-united-states-intervention-in-venezuela"),
    ("The Global Angle — countries at war (Jul 2026 update)", "https://theglobalangle.com/countries-currently-at-war-2026-conflict/"),
    ("Quartz — China extends US trade truce through January", "https://qz.com/china-extends-trade-truce-january-tariffs-110926"),
    ("JBizNews — US–China truce through Nov 2026", "https://jbiznews.com/?p=366330"),
    ("Al Jazeera — Iran war live, 31 Oct 2026", "https://www.aljazeera.com/news/liveblog/2026/10/31/iran-war-live-oil-tankers-hit-in-hormuz-trump-says-conflict-will-end-soon"),
    ("CNBC — Iran claims four tankers struck mines, 30 Oct 2026", "https://www.cnbc.com/2026/10/30/iran-trump-hormuz-oil-middle-east-.html"),
    ("Knightsbridge Strategic Group — careers & palette", "https://www.knightsbridgesg.com/careers"),
]
