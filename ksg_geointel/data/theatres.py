"""
Escalation theatres, retaliation ("strike-back") options and scenario trees.

Analyst seed as of 10 November 2026. Probabilities are subjective judgements
for the stated horizon (default: next 90 days). Scenario probabilities in each
theatre sum to 1.0. Market impacts are indicative first-order moves versus the
current level, NOT forecasts or advice.

Fields
------
intensity      0-100 current heat of the theatre
current_rung   index into `ladder` (0 = lowest rung)
participants   {iso3: exposure weight 0-1} used by the risk engine
retaliation    list of strike-back options
scenarios      mutually exclusive outcomes with indicative market impacts:
               brent ($/bbl change), gold (%), spx (% S&P 500), plus free text
"""

LADDER_GENERIC = [
    "Rhetoric & signalling",
    "Sanctions / economic coercion",
    "Gray-zone & hybrid (cyber, sabotage, militia)",
    "Limited kinetic strikes",
    "Sustained strike campaign / blockade",
    "Strikes on critical economic infrastructure",
    "Regional war (multi-state)",
    "Strategic / existential (WMD, regime change)",
]

THEATRES = [
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "hormuz",
        "name": "Iran ↔ US/Israel · Strait of Hormuz",
        "region": "Middle East",
        "intensity": 94,
        "status": "Active war at sea; US blockade of Iranian ports; Qatar-mediated 48h de-escalation framework under review",
        "current_rung": 5,
        "ladder": LADDER_GENERIC,
        "participants": {"IRN": 1.0, "USA": 0.55, "ISR": 0.7, "SAU": 0.6, "ARE": 0.6, "QAT": 0.65, "KWT": 0.7,
                         "BHR": 0.7, "OMN": 0.55, "IRQ": 0.75, "YEM": 0.6, "JOR": 0.45, "IND": 0.3, "JPN": 0.3,
                         "KOR": 0.3, "CHN": 0.25, "PAK": 0.25, "EGY": 0.35},
        "summary": "Since Operation Epic Fury (28 Feb) the war has moved to a maritime contest: IRGC mines, drones and fast boats against a US blockade of Iranian ports. Two MOUs (June, August) collapsed. Limited US strikes on Qeshm air defences (2 and 6 Nov) came alongside renewed Qatari mediation after the US midterms. Brent has dropped ~7% w/w to ~$94–98 on deal hopes. That premium is binary: talks either produce a reopening or the US resumes a strike campaign that Iran has promised to answer 'without geographical limits'.",
        "retaliation": [
            {"actor": "Iran / IRGC Navy", "actor_iso": "IRN", "action": "Expanded mining & drone-boat attacks on tankers", "target": "Gulf shipping (Kuwait, Qatar, UAE lanes)", "target_iso": "QAT", "prob": 0.60, "severity": 4, "horizon": "0–30d", "channels": ["Brent", "Tanker rates (VLCC)", "War-risk premia"], "tripwire": "UKMTO incident count >3/day; new restricted-zone declaration"},
            {"actor": "Iran / IRGC Aerospace", "actor_iso": "IRN", "action": "Ballistic missile strikes on US bases", "target": "Bahrain, Kuwait, Jordan, Erbil", "target_iso": "BHR", "prob": 0.35, "severity": 4, "horizon": "0–30d (if US campaign resumes)", "channels": ["Gold", "USD", "Defence equities"], "tripwire": "Resumption order for US strike campaign"},
            {"actor": "Iran", "actor_iso": "IRN", "action": "Strike Saudi/UAE energy infrastructure (Abqaiq, Ras Tanura, Fujairah)", "target": "Saudi Arabia / UAE", "target_iso": "SAU", "prob": 0.20, "severity": 5, "horizon": "0–60d", "channels": ["Brent +$20–40", "Saudi CDS", "Asian importers"], "tripwire": "US strikes on Kharg Island or Iranian refineries"},
            {"actor": "Iraqi militias (Iran-aligned)", "actor_iso": "IRQ", "action": "Rocket/drone attacks on US sites and Kurdish oil fields", "target": "US forces Iraq/Syria", "target_iso": "USA", "prob": 0.45, "severity": 3, "horizon": "0–30d", "channels": ["Kurdish crude", "Iraqi exports"], "tripwire": "Killing of senior IRGC/militia commander"},
            {"actor": "United States / CENTCOM", "actor_iso": "USA", "action": "Resume sustained strike campaign on IRGC naval & missile assets", "target": "Iranian coast, islands (Qeshm, Larak, Abu Musa)", "target_iso": "IRN", "prob": 0.40, "severity": 4, "horizon": "0–30d", "channels": ["Brent spike then fade", "Gold", "VIX"], "tripwire": "Collapse of Qatar framework; US casualties"},
            {"actor": "United States", "actor_iso": "USA", "action": "Strike Iranian energy infrastructure (Kharg terminal, power plants)", "target": "Iran oil export capacity", "target_iso": "IRN", "prob": 0.15, "severity": 5, "horizon": "0–60d", "channels": ["Brent", "Dubai–Brent spread", "China teapot margins"], "tripwire": "Iranian strike on Gulf energy assets"},
            {"actor": "Israel", "actor_iso": "ISR", "action": "Unilateral strikes on Iranian leadership / nuclear sites", "target": "Iran", "target_iso": "IRN", "prob": 0.25, "severity": 5, "horizon": "0–90d", "channels": ["Gold", "ILS", "Brent"], "tripwire": "US–Iran deal seen as conceding enrichment; Netanyahu regime-change order"},
            {"actor": "Iran (cyber)", "actor_iso": "IRN", "action": "Cyber attacks on Gulf/US utilities, banks, ports", "target": "GCC & US critical infrastructure", "target_iso": "ARE", "prob": 0.50, "severity": 3, "horizon": "0–90d", "channels": ["Cyber insurers", "Gulf banks"], "tripwire": "Ongoing — low threshold"},
        ],
        "scenarios": [
            {"name": "Negotiated reopening (Qatar framework → MOU-3)", "prob": 0.35, "brent": -12, "gold": -3, "spx": 2.5, "desc": "48h framework turns into phased reopening; blockade eased; mines cleared. Brent towards low-$80s; tanker rates normalise over 4–8 weeks."},
            {"name": "Armed stalemate (status quo)", "prob": 0.40, "brent": 3, "gold": 1, "spx": -0.5, "desc": "Blockade continues; intermittent mine/tanker incidents; limited US strikes. Brent $95–105 range, elevated vol."},
            {"name": "Renewed US campaign + Iranian regional retaliation", "prob": 0.25, "brent": 25, "gold": 6, "spx": -6, "desc": "US resumes strikes; Iran hits Gulf infrastructure and bases. Brent retests $120–126 high; Fed stagflation dilemma; EM importers hit."},
        ],
        "indicators": ["Qatar/US statements on 48h framework", "UKMTO/JMIC incident reports", "Task Force Iron Gate operations", "CENTCOM transit counts vs 39.7 vessels/day pre-war", "Iranian supreme leader rhetoric", "War-risk premium quotes (Lloyd's JWC)"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "red_sea",
        "name": "Houthis ↔ Saudi coalition · Red Sea / Bab el-Mandeb",
        "region": "Middle East",
        "intensity": 78,
        "status": "Houthis hold the Red Sea coast; attacks on Saudi territory; Suez transits down >50%",
        "current_rung": 5,
        "ladder": LADDER_GENERIC,
        "participants": {"YEM": 1.0, "SAU": 0.7, "EGY": 0.6, "ERI": 0.3, "DJI": 0.3, "ISR": 0.3, "USA": 0.2, "SDN": 0.2},
        "summary": "The Houthis took Yemen's Red Sea coast in September and now strike Saudi territory. They claimed an attack on Aramco offices in Riyadh on 8 Nov. Bab el-Mandeb is severely restricted, which together with Hormuz forces Cape routing. That adds 10–14 days to Asia–Europe voyages.",
        "retaliation": [
            {"actor": "Houthis", "actor_iso": "YEM", "action": "Missile/drone strikes on Saudi oil & desalination", "target": "Saudi Arabia (Yanbu bypass!)", "target_iso": "SAU", "prob": 0.55, "severity": 4, "horizon": "0–30d", "channels": ["Brent", "Saudi export capacity via Red Sea"], "tripwire": "Saudi coalition offensive on Hodeidah"},
            {"actor": "Houthis", "actor_iso": "YEM", "action": "Anti-ship attacks on Suez-bound traffic", "target": "Red Sea commercial shipping", "target_iso": "EGY", "prob": 0.70, "severity": 3, "horizon": "0–30d", "channels": ["Container rates (SCFI/WCI)", "Suez receipts", "European inflation"], "tripwire": "Ongoing"},
            {"actor": "Saudi-led coalition", "actor_iso": "SAU", "action": "Air campaign on Houthi launch sites & ports", "target": "Yemen", "target_iso": "YEM", "prob": 0.65, "severity": 3, "horizon": "0–30d", "channels": ["Regional risk premium"], "tripwire": "Further strikes on Riyadh"},
            {"actor": "Egypt", "actor_iso": "EGY", "action": "Direct military support to Saudi Arabia", "target": "Houthis", "target_iso": "YEM", "prob": 0.25, "severity": 3, "horizon": "0–90d", "channels": ["EGP", "Egypt Eurobonds"], "tripwire": "Attack on Suez-bound Egyptian-flag vessel"},
        ],
        "scenarios": [
            {"name": "Contained harassment", "prob": 0.50, "brent": 1, "gold": 0.5, "spx": 0, "desc": "Sporadic strikes; Cape routing persists; freight elevated but stable."},
            {"name": "Yanbu/Red Sea export disruption", "prob": 0.25, "brent": 12, "gold": 2, "spx": -2, "desc": "Strikes hit Saudi Red Sea bypass — removes Hormuz workaround; acute crude tightness."},
            {"name": "Coupled de-escalation with Iran deal", "prob": 0.25, "brent": -4, "gold": -1, "spx": 1, "desc": "Houthi pause tied to US–Iran framework; Suez transits recover gradually."},
        ],
        "indicators": ["Suez Canal Authority transit data", "Strikes near Yanbu/Jeddah", "Houthi military spokesman statements", "Drewry WCI"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "russia_ukraine",
        "name": "Russia ↔ Ukraine",
        "region": "Europe/Eurasia",
        "intensity": 86,
        "status": "High-intensity war; infrastructure war; Abu Dhabi US–Russia–Ukraine talks 10–11 Nov (no Europeans)",
        "current_rung": 5,
        "ladder": LADDER_GENERIC,
        "participants": {"UKR": 1.0, "RUS": 0.9, "BLR": 0.5, "POL": 0.35, "MDA": 0.35, "PRK": 0.4, "ROU": 0.25,
                         "DEU": 0.2, "FRA": 0.15, "GBR": 0.2, "USA": 0.25, "ARE": 0.15, "KAZ": 0.2, "HUN": 0.15},
        "summary": "Russia struck Kyiv on 6–8 Nov with 36 ballistic missiles and 172 drones, cutting power and heat to more than 600,000 people. Ukraine answered with deep strikes on Yaroslavl refining, Bryansk launch sites and Oryol microelectronics. The Abu Dhabi trilateral talks may yield an energy-infrastructure strike moratorium, which is the key market variable for European gas and diesel. Russia's advance slowed by more than half in 2026, and North Korea is mass-producing attack drones for Moscow.",
        "retaliation": [
            {"actor": "Russia", "actor_iso": "RUS", "action": "Mass missile/drone strikes on Ukrainian grid & gas storage", "target": "Ukraine energy system", "target_iso": "UKR", "prob": 0.80, "severity": 4, "horizon": "0–30d (winter)", "channels": ["TTF gas", "EU power", "UKR Eurobonds"], "tripwire": "Talks stall; Ukrainian refinery strikes"},
            {"actor": "Ukraine", "actor_iso": "UKR", "action": "Deep strikes on refineries & export ports (Primorsk, Novorossiysk, Ust-Luga)", "target": "Russian oil & product exports", "target_iso": "RUS", "prob": 0.70, "severity": 4, "horizon": "0–30d", "channels": ["Diesel cracks", "Urals discount", "CPC Blend"], "tripwire": "Absence of moratorium"},
            {"actor": "Russia", "actor_iso": "RUS", "action": "Hybrid sabotage in Europe (rail, cables, arson, drones over airports)", "target": "NATO Europe", "target_iso": "POL", "prob": 0.60, "severity": 3, "horizon": "0–90d", "channels": ["European defence equities", "Insurance"], "tripwire": "New EU sanctions package; frozen-asset loan to Ukraine"},
            {"actor": "Russia", "actor_iso": "RUS", "action": "Nuclear signalling / Oreshnik use", "target": "Ukraine / NATO", "target_iso": "UKR", "prob": 0.15, "severity": 5, "horizon": "0–90d", "channels": ["Gold", "CHF", "EUR"], "tripwire": "Long-range Western missiles approved for Ukraine"},
            {"actor": "Ukraine", "actor_iso": "UKR", "action": "Strikes on Black Sea shadow-fleet tankers", "target": "Russian seaborne crude", "target_iso": "RUS", "prob": 0.40, "severity": 3, "horizon": "0–60d", "channels": ["Tanker rates", "Brent–Urals spread"], "tripwire": "Russian attacks on Odesa ports"},
        ],
        "scenarios": [
            {"name": "Energy-strike moratorium + framework talks", "prob": 0.30, "brent": -3, "gold": -1, "spx": 1.5, "desc": "Abu Dhabi yields partial moratorium; TTF falls; EU defence names wobble; Ukrainian bonds rally."},
            {"name": "Winter infrastructure war continues", "prob": 0.55, "brent": 2, "gold": 1, "spx": -0.5, "desc": "No deal; reciprocal energy strikes; diesel tight; European gas risk premium persists."},
            {"name": "Escalation to NATO-border incident", "prob": 0.15, "brent": 5, "gold": 4, "spx": -4, "desc": "Drone/missile incident on NATO territory or Baltic clash; EUR weakens; haven bid."},
        ],
        "indicators": ["Abu Dhabi talks readout (Peskov/Umerov)", "Ukrenergo outage data", "Russian refinery runs", "EU 20th sanctions package", "North Korean shipments"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "baltic_hybrid",
        "name": "Russia ↔ NATO · Baltic hybrid front",
        "region": "Europe/Eurasia",
        "intensity": 55,
        "status": "Cable sabotage, shadow-fleet confrontations, airspace violations",
        "current_rung": 2,
        "ladder": LADDER_GENERIC,
        "participants": {"RUS": 0.6, "FIN": 0.7, "EST": 0.8, "LVA": 0.7, "LTU": 0.8, "POL": 0.6, "SWE": 0.5,
                         "DNK": 0.4, "DEU": 0.3, "BLR": 0.5, "NOR": 0.3},
        "summary": "A Helsinki court sentenced the crew of the Fitburg on 5 Nov for severing a subsea cable. Moscow is responding to interdictions of its shadow fleet in the Baltic with naval escorts and airspace probes. Belarus is running balloon and drone harassment of Lithuania and Poland.",
        "retaliation": [
            {"actor": "Russia", "actor_iso": "RUS", "action": "Naval escort of shadow fleet / boarding stand-off", "target": "Estonia / Finland", "target_iso": "EST", "prob": 0.45, "severity": 3, "horizon": "0–90d", "channels": ["Baltic spreads", "Tanker insurance"], "tripwire": "Another tanker detention"},
            {"actor": "Russia", "actor_iso": "RUS", "action": "Further subsea cable/pipeline sabotage", "target": "Baltic infrastructure", "target_iso": "FIN", "prob": 0.40, "severity": 3, "horizon": "0–90d", "channels": ["Nordic power", "Telecoms"], "tripwire": "Winter storms give deniability"},
            {"actor": "Belarus", "actor_iso": "BLR", "action": "Border/airspace harassment, migrant instrumentalisation", "target": "Lithuania / Poland", "target_iso": "LTU", "prob": 0.60, "severity": 2, "horizon": "0–30d", "channels": ["Regional sentiment"], "tripwire": "Sanctions on potash transit"},
            {"actor": "NATO frontline states", "actor_iso": "POL", "action": "Closure of borders / interdiction of shadow-fleet tankers", "target": "Russia", "target_iso": "RUS", "prob": 0.35, "severity": 2, "horizon": "0–90d", "channels": ["Urals flows via Primorsk"], "tripwire": "Sabotage attribution"},
        ],
        "scenarios": [
            {"name": "Managed hybrid pressure", "prob": 0.70, "brent": 0, "gold": 0.5, "spx": 0, "desc": "Incidents continue below Article 5 threshold."},
            {"name": "Kinetic naval incident", "prob": 0.20, "brent": 3, "gold": 2, "spx": -2, "desc": "Shots fired between Russian and NATO vessels; Baltic shipping insurance spikes."},
            {"name": "Détente via Ukraine talks", "prob": 0.10, "brent": -1, "gold": -0.5, "spx": 0.5, "desc": "Hybrid activity eases as US–Russia channel opens."},
        ],
        "indicators": ["Detentions of shadow-fleet tankers", "Cable outage reports", "Kaliningrad naval movements"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "taiwan",
        "name": "China ↔ Taiwan / US / Japan",
        "region": "Asia-Pacific",
        "intensity": 64,
        "status": "Elevated gray-zone pressure and naval saturation; no blockade; Nov–Dec drill window; 28 Nov Taiwan local elections",
        "current_rung": 2,
        "ladder": LADDER_GENERIC,
        "participants": {"TWN": 1.0, "CHN": 0.7, "USA": 0.4, "JPN": 0.55, "PHL": 0.4, "KOR": 0.3, "NLD": 0.15, "VNM": 0.2, "AUS": 0.2},
        "summary": "Taiwan's NSC reported more than 50 PLAN and China Coast Guard vessels between southern Japan and the Philippine Sea, plus the Liaoning carrier group. Chinese vessels around Taiwan rose from 55 in June to 244 in September. Beijing's rhetoric has hardened to 'crack down on' independence. US Marines have deployed NMESIS to Yonaguni. The $14bn US arms package is stalled. The PLA purge, which leaves the CMC as Xi plus Zhang Shengmin, raises questions about command cohesion. US officials say pre-2028 invasion risk is overpriced, but blockade and quarantine drills remain plausible.",
        "retaliation": [
            {"actor": "China / PLA", "actor_iso": "CHN", "action": "Named encirclement drill ('Strait Thunder'/'Justice Mission' type)", "target": "Taiwan", "target_iso": "TWN", "prob": 0.45, "severity": 3, "horizon": "0–60d", "channels": ["TSMC", "TWD", "SOX", "CNH"], "tripwire": "US arms package approval; Lai transit; post-28 Nov election outcome"},
            {"actor": "China Coast Guard", "actor_iso": "CHN", "action": "'Law-enforcement quarantine' / inspections near Kinmen, Pratas", "target": "Taiwan outlying islands", "target_iso": "TWN", "prob": 0.20, "severity": 4, "horizon": "0–90d", "channels": ["Semis supply chain", "Shipping insurance"], "tripwire": "Taiwan coast guard use of force; DPP win in key races"},
            {"actor": "China (economic)", "actor_iso": "CHN", "action": "Rare-earth / critical-mineral export controls re-imposed", "target": "US, Japan, EU manufacturers", "target_iso": "USA", "prob": 0.30, "severity": 4, "horizon": "0–90d", "channels": ["Rare earths (NdPr)", "Defence & EV supply chains"], "tripwire": "Truce lapse (Jan 2027); new US chip controls"},
            {"actor": "China", "actor_iso": "CHN", "action": "Sanctions on US defence firms / Japanese entities", "target": "US & Japan", "target_iso": "JPN", "prob": 0.55, "severity": 2, "horizon": "0–60d", "channels": ["Defence primes (limited)", "JPY"], "tripwire": "Arms sale; Yonaguni deployments"},
            {"actor": "Japan / US", "actor_iso": "JPN", "action": "Forward missile deployments, joint FONOPs in Strait", "target": "China", "target_iso": "CHN", "prob": 0.50, "severity": 2, "horizon": "0–90d", "channels": ["Japanese defence equities"], "tripwire": "PLA drill"},
        ],
        "scenarios": [
            {"name": "Gray-zone status quo", "prob": 0.60, "brent": 0, "gold": 0.5, "spx": 0, "desc": "Daily ADIZ/vessel pressure, election interference; markets largely look through."},
            {"name": "Large encirclement drill / quarantine scare", "prob": 0.32, "brent": 2, "gold": 2, "spx": -3, "desc": "Named drill with live fire; TSMC −8–12%, SOX −6%; TWD weaker; insurance spikes then fades."},
            {"name": "Blockade / kinetic crisis", "prob": 0.08, "brent": 10, "gold": 10, "spx": -15, "desc": "Tail risk: semis supply shock; global equity drawdown; USD/JPY haven dynamics complex."},
        ],
        "indicators": ["Taiwan MND daily sortie & vessel counts", "PLA Eastern Theater announcements", "MSA navigation warnings", "US arms sale notification", "28 Nov election results"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "scs",
        "name": "China ↔ Philippines · South China Sea",
        "region": "Asia-Pacific",
        "intensity": 52,
        "status": "Vessel surges, water-cannon incidents, Paracels runway build",
        "current_rung": 2,
        "ladder": LADDER_GENERIC,
        "participants": {"PHL": 0.9, "CHN": 0.5, "VNM": 0.4, "USA": 0.25, "JPN": 0.2, "MYS": 0.2, "IDN": 0.15},
        "summary": "The Philippines counted 54 Chinese vessels in the West Philippine Sea in late October, up from 31 the week before. China is building a runway at Antelope Reef in the Paracels, with a possible first landing by mid-2027. Manila is buying more frigates.",
        "retaliation": [
            {"actor": "China Coast Guard", "actor_iso": "CHN", "action": "Water-cannon / ramming at Second Thomas & Scarborough", "target": "Philippines", "target_iso": "PHL", "prob": 0.70, "severity": 2, "horizon": "0–30d", "channels": ["PHP", "Regional sentiment"], "tripwire": "Resupply mission"},
            {"actor": "Philippines + US", "actor_iso": "PHL", "action": "Mutual Defense Treaty invocation drills / joint sails", "target": "China", "target_iso": "CHN", "prob": 0.40, "severity": 2, "horizon": "0–90d", "channels": ["—"], "tripwire": "Filipino casualty"},
        ],
        "scenarios": [
            {"name": "Routine coercion", "prob": 0.80, "brent": 0, "gold": 0, "spx": 0, "desc": "Incidents without casualties."},
            {"name": "Fatal incident / MDT crisis", "prob": 0.20, "brent": 1, "gold": 1.5, "spx": -1.5, "desc": "US alliance credibility test; Asia risk-off."},
        ],
        "indicators": ["AMTI imagery", "PCG statements", "Resupply missions"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "us_china_trade",
        "name": "US ↔ China · trade, tech & tariffs",
        "region": "Global",
        "intensity": 50,
        "status": "Truce reportedly extended ~2 months to January 2027; 10% reciprocal tariff retained; chips/rare earths contested",
        "current_rung": 1,
        "ladder": LADDER_GENERIC,
        "participants": {"CHN": 0.6, "USA": 0.5, "TWN": 0.3, "KOR": 0.25, "JPN": 0.2, "NLD": 0.3, "VNM": 0.3, "MEX": 0.25, "DEU": 0.2, "AUS": 0.15, "BRA": 0.15},
        "summary": "The tariff truce from the Busan summit lapsed on 10 Nov and has reportedly been extended to January 2027 with the 10% tariff kept. That creates a tariff cliff in early 2027. The Supreme Court's February IEEPA ruling pushed the administration onto Section 122, which is time-limited. Divided government after the midterms complicates any extension by Congress. China retains rare-earth leverage and can return to entity-list moves.",
        "retaliation": [
            {"actor": "United States", "actor_iso": "USA", "action": "New chip/AI export controls or entity listings", "target": "China tech", "target_iso": "CHN", "prob": 0.35, "severity": 3, "horizon": "0–90d", "channels": ["SOX", "Chinese tech ADRs"], "tripwire": "Truce talks stall"},
            {"actor": "China", "actor_iso": "CHN", "action": "Rare-earth licensing slowdown / soybean purchase halt", "target": "US industry & farmers", "target_iso": "USA", "prob": 0.30, "severity": 3, "horizon": "0–90d", "channels": ["NdPr prices", "Soybeans (CBOT)"], "tripwire": "US controls; Taiwan arms sale"},
            {"actor": "United States", "actor_iso": "USA", "action": "Tariff snap-back after truce expiry", "target": "China", "target_iso": "CHN", "prob": 0.25, "severity": 4, "horizon": "Jan 2027", "channels": ["CNH", "S&P 500", "Freight front-loading"], "tripwire": "No deal by expiry"},
        ],
        "scenarios": [
            {"name": "Rolling extensions", "prob": 0.55, "brent": 0, "gold": 0, "spx": 0.5, "desc": "Muddle-through; uncertainty tax on capex."},
            {"name": "Comprehensive deal (semis + soybeans + fentanyl)", "prob": 0.15, "brent": 1, "gold": -1, "spx": 3, "desc": "Risk-on; CNH stronger; copper bid."},
            {"name": "Snap-back / tech war escalation", "prob": 0.30, "brent": -2, "gold": 3, "spx": -5, "desc": "Tariffs re-escalate; rare-earth squeeze; global growth downgrade."},
        ],
        "indicators": ["USTR/MOFCOM statements", "BIS Federal Register entries", "China rare-earth export data", "CBOT soybean export sales to China"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "israel_lebanon",
        "name": "Israel ↔ Hezbollah / Gaza",
        "region": "Middle East",
        "intensity": 76,
        "status": "Israeli ground operations in south Lebanon; Gaza humanitarian crisis",
        "current_rung": 4,
        "ladder": LADDER_GENERIC,
        "participants": {"ISR": 0.8, "LBN": 1.0, "PSE": 0.9, "SYR": 0.4, "IRN": 0.4, "JOR": 0.3, "EGY": 0.3},
        "summary": "The northern front is part of the wider Iran war. Israel runs ground operations in south Lebanon and holds Gaza under military control. A collapse of the US–Iran talks would probably bring heavier Hezbollah fire.",
        "retaliation": [
            {"actor": "Hezbollah", "actor_iso": "LBN", "action": "Rocket/drone barrages on northern Israel & Haifa", "target": "Israel", "target_iso": "ISR", "prob": 0.55, "severity": 3, "horizon": "0–30d", "channels": ["ILS", "Israeli gas fields (Karish)"], "tripwire": "IDF advance north of Litani"},
            {"actor": "Israel (IDF)", "actor_iso": "ISR", "action": "Strikes on Beirut Dahiyeh / Lebanese infrastructure", "target": "Lebanon", "target_iso": "LBN", "prob": 0.60, "severity": 4, "horizon": "0–30d", "channels": ["Regional sentiment"], "tripwire": "Mass-casualty attack in Israel"},
        ],
        "scenarios": [
            {"name": "Grinding ground war", "prob": 0.55, "brent": 1, "gold": 0.5, "spx": 0, "desc": "Contained to south Lebanon."},
            {"name": "Ceasefire linked to Iran deal", "prob": 0.30, "brent": -2, "gold": -0.5, "spx": 0.5, "desc": "Northern front pauses."},
            {"name": "Full-scale Hezbollah escalation", "prob": 0.15, "brent": 4, "gold": 2, "spx": -1.5, "desc": "Strikes on Israeli energy infrastructure; East Med gas offline."},
        ],
        "indicators": ["IDF evacuation orders", "UNIFIL reports", "Hezbollah launch counts"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "india_pakistan",
        "name": "India ↔ Pakistan",
        "region": "Asia-Pacific",
        "intensity": 45,
        "status": "Post-Pahalgam deterrence instability; Indus Waters Treaty suspended",
        "current_rung": 1,
        "ladder": LADDER_GENERIC,
        "participants": {"IND": 0.6, "PAK": 0.8, "CHN": 0.15, "AFG": 0.1, "USA": 0.1},
        "summary": "After the 2025 strikes the two sides keep a fragile deterrence balance. Pakistan is stretched on its Afghan front and acts as the US–Iran back channel. Think tanks put the risk of an armed clash in 2026 well above the historical baseline. A mass-casualty attack in Kashmir is the classic trigger.",
        "retaliation": [
            {"actor": "India", "actor_iso": "IND", "action": "Cross-border strikes after terror attack ('Op Sindoor' doctrine)", "target": "Pakistan", "target_iso": "PAK", "prob": 0.15, "severity": 4, "horizon": "0–90d (conditional on attack)", "channels": ["INR", "Nifty", "PKR bonds"], "tripwire": "Mass-casualty attack in J&K"},
            {"actor": "Pakistan", "actor_iso": "PAK", "action": "Retaliatory missile/air strikes", "target": "India", "target_iso": "IND", "prob": 0.12, "severity": 4, "horizon": "Conditional", "channels": ["Gold", "Regional risk"], "tripwire": "Indian strike"},
        ],
        "scenarios": [
            {"name": "Armed deterrence holds", "prob": 0.85, "brent": 0, "gold": 0, "spx": 0, "desc": "Rhetoric, water disputes."},
            {"name": "Limited military exchange", "prob": 0.15, "brent": 1, "gold": 2, "spx": -1, "desc": "4-day 2025-style clash; INR/PKR hit."},
        ],
        "indicators": ["LoC ceasefire violations", "Terror incidents in J&K", "DGMO hotline use"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "afpak",
        "name": "Pakistan ↔ Afghan Taliban / TTP",
        "region": "Asia-Pacific",
        "intensity": 66,
        "status": "~200 Pakistani strikes; Taliban drone retaliation into KP & Balochistan",
        "current_rung": 3,
        "ladder": LADDER_GENERIC,
        "participants": {"PAK": 0.7, "AFG": 1.0, "TJK": 0.2, "CHN": 0.1},
        "summary": "Cross-border war driven by TTP attacks. Chinese CPEC assets in Balochistan are exposed.",
        "retaliation": [
            {"actor": "Pakistan", "actor_iso": "PAK", "action": "Air & artillery strikes on TTP sanctuaries", "target": "Afghanistan", "target_iso": "AFG", "prob": 0.75, "severity": 3, "horizon": "0–30d", "channels": ["PKR Eurobonds"], "tripwire": "TTP attack"},
            {"actor": "Afghan Taliban", "actor_iso": "AFG", "action": "Drone strikes / border offensives", "target": "Pakistan", "target_iso": "PAK", "prob": 0.55, "severity": 3, "horizon": "0–30d", "channels": ["CPEC risk"], "tripwire": "Civilian casualties from Pakistani strikes"},
        ],
        "scenarios": [
            {"name": "Persistent border war", "prob": 0.70, "brent": 0, "gold": 0, "spx": 0, "desc": "Local impact; Pakistan fiscal stress."},
            {"name": "Mediated de-escalation (Qatar/Türkiye)", "prob": 0.30, "brent": 0, "gold": 0, "spx": 0, "desc": "Temporary ceasefire."},
        ],
        "indicators": ["ISPR statements", "TTP attack tempo", "Torkham crossing status"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "venezuela",
        "name": "US ↔ Venezuela / cartels · Caribbean",
        "region": "Americas",
        "intensity": 55,
        "status": "Post-Maduro transition under acting president Rodríguez; US recognition; colectivos/ELN risk",
        "current_rung": 3,
        "ladder": LADDER_GENERIC,
        "participants": {"VEN": 1.0, "USA": 0.25, "COL": 0.45, "CUB": 0.5, "MEX": 0.35, "PAN": 0.15},
        "summary": "Maduro was captured on 3 Jan and faces trial in New York. The US recognises Delcy Rodríguez as head of state. The hydrocarbon law reopened the oil sector, but majors are cautious. Chavista security chiefs keep their posts. The US campaign against cartels could spread to Mexican territory.",
        "retaliation": [
            {"actor": "Colectivos / ELN", "actor_iso": "VEN", "action": "Attacks on US personnel, oil installations", "target": "US presence / oil sector", "target_iso": "USA", "prob": 0.25, "severity": 3, "horizon": "0–90d", "channels": ["Venezuelan crude ramp-up", "PDVSA bonds"], "tripwire": "Purge of Cabello faction"},
            {"actor": "United States", "actor_iso": "USA", "action": "Unilateral strikes on cartel targets in Mexico", "target": "Mexico", "target_iso": "MEX", "prob": 0.15, "severity": 4, "horizon": "0–90d", "channels": ["MXN", "USMCA supply chains"], "tripwire": "Mass-casualty fentanyl incident / attack on US citizens"},
        ],
        "scenarios": [
            {"name": "Managed transition, gradual oil recovery", "prob": 0.55, "brent": -1, "gold": 0, "spx": 0, "desc": "Heavy crude supply edges up; bond recovery trade."},
            {"name": "Fragmentation & violence", "prob": 0.30, "brent": 1, "gold": 0.5, "spx": 0, "desc": "Security deteriorates; oil investment freezes."},
            {"name": "Election roadmap agreed", "prob": 0.15, "brent": -1.5, "gold": 0, "spx": 0.2, "desc": "Sanctions on production lifted; majors return."},
        ],
        "indicators": ["OFAC licences", "PDVSA output", "Election date announcement"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "korea",
        "name": "North Korea ↔ South Korea / US / Japan",
        "region": "Asia-Pacific",
        "intensity": 42,
        "status": "DPRK supplying Russia; missile testing; Russia–DPRK defence pact",
        "current_rung": 1,
        "ladder": LADDER_GENERIC,
        "participants": {"PRK": 0.8, "KOR": 0.5, "JPN": 0.35, "USA": 0.15, "RUS": 0.15},
        "summary": "Pyongyang is mass-producing attack drones for Russia and receiving technology in return. A 7th nuclear test is a recurring tail risk.",
        "retaliation": [
            {"actor": "North Korea", "actor_iso": "PRK", "action": "ICBM / hypersonic test or 7th nuclear test", "target": "US / Japan", "target_iso": "JPN", "prob": 0.30, "severity": 3, "horizon": "0–90d", "channels": ["KRW", "JPY", "KOSPI"], "tripwire": "US–ROK drills"},
        ],
        "scenarios": [
            {"name": "Testing & rhetoric", "prob": 0.85, "brent": 0, "gold": 0.3, "spx": 0, "desc": "Markets largely desensitised."},
            {"name": "Nuclear test / border clash", "prob": 0.15, "brent": 0, "gold": 1.5, "spx": -1, "desc": "Short-lived KRW sell-off."},
        ],
        "indicators": ["KCNA announcements", "Punggye-ri imagery", "Russian shipments"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "sahel",
        "name": "Sahel juntas ↔ jihadists · coastal spillover",
        "region": "Africa",
        "intensity": 70,
        "status": "JNIM blockade of Bamako; expanding insurgency; Russian Africa Corps",
        "current_rung": 4,
        "ladder": LADDER_GENERIC,
        "participants": {"MLI": 1.0, "BFA": 1.0, "NER": 0.9, "TCD": 0.4, "NGA": 0.3, "GHA": 0.2, "CIV": 0.25, "BEN": 0.3, "TGO": 0.3, "RUS": 0.1},
        "summary": "JNIM's fuel blockade threatens Bamako. Juntas are nationalising gold and uranium assets. The jihadist threat is spreading to the coastal states of Benin, Togo, Ghana and Côte d'Ivoire.",
        "retaliation": [
            {"actor": "JNIM / ISSP", "actor_iso": "MLI", "action": "Blockades & attacks on mines, convoys, capitals", "target": "Mali / Burkina / Niger", "target_iso": "MLI", "prob": 0.80, "severity": 3, "horizon": "0–30d", "channels": ["Gold miners (Barrick, B2Gold)", "Uranium"], "tripwire": "Ongoing"},
            {"actor": "Sahel juntas", "actor_iso": "NER", "action": "Asset seizures / licence revocations of Western miners", "target": "Foreign miners", "target_iso": "FRA", "prob": 0.40, "severity": 3, "horizon": "0–90d", "channels": ["Uranium (Orano)", "Gold equities"], "tripwire": "Fiscal pressure"},
        ],
        "scenarios": [
            {"name": "Slow deterioration", "prob": 0.60, "brent": 0, "gold": 0.3, "spx": 0, "desc": "Mines operate under heavy security costs."},
            {"name": "Fall of Bamako / junta collapse", "prob": 0.15, "brent": 0, "gold": 0.8, "spx": 0, "desc": "Regional shock; gold supply disruption; coastal spillover."},
            {"name": "Negotiated local truces", "prob": 0.25, "brent": 0, "gold": 0, "spx": 0, "desc": "Juntas strike deals with jihadist factions."},
        ],
        "indicators": ["ACLED event counts", "Fuel prices in Bamako", "Mining licence decrees"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "great_lakes",
        "name": "DR Congo ↔ M23/Rwanda · Ebola",
        "region": "Africa",
        "intensity": 68,
        "status": "M23 in the east; Bundibugyo Ebola outbreak with cross-border cases (Kenya, Uganda, Nigeria); WHO briefing 12 Nov",
        "current_rung": 4,
        "ladder": LADDER_GENERIC,
        "participants": {"COD": 1.0, "RWA": 0.6, "UGA": 0.5, "KEN": 0.35, "BDI": 0.4, "NGA": 0.2},
        "summary": "The eastern DRC conflict and the Ebola outbreak, now past 5,230 deaths, are compounding each other. Both threaten cobalt and copper logistics, and the outbreak could trigger travel and trade restrictions across East Africa.",
        "retaliation": [
            {"actor": "M23 / Rwanda", "actor_iso": "RWA", "action": "New offensive toward mining hubs", "target": "DR Congo", "target_iso": "COD", "prob": 0.40, "severity": 3, "horizon": "0–90d", "channels": ["Cobalt", "Coltan"], "tripwire": "Collapse of Washington/Doha process"},
            {"actor": "WHO / states", "actor_iso": "COD", "action": "PHEIC declaration / travel restrictions", "target": "East & Central Africa", "target_iso": "KEN", "prob": 0.35, "severity": 3, "horizon": "0–30d", "channels": ["Airlines", "EM Africa FX"], "tripwire": "Urban transmission in Nairobi/Kampala/Lagos"},
        ],
        "scenarios": [
            {"name": "Contained outbreak, frozen front", "prob": 0.50, "brent": 0, "gold": 0, "spx": 0, "desc": "Localised impact."},
            {"name": "PHEIC + regional spread", "prob": 0.30, "brent": -0.5, "gold": 0.5, "spx": -0.5, "desc": "Travel bans; cobalt logistics disrupted."},
            {"name": "M23 offensive on Katanga corridor", "prob": 0.20, "brent": 0, "gold": 0.3, "spx": 0, "desc": "Cobalt price spike."},
        ],
        "indicators": ["WHO situation reports", "M23 front lines", "Cobalt export permits"],
    },
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "sudan",
        "name": "Sudan · SAF ↔ RSF",
        "region": "Africa",
        "intensity": 82,
        "status": "War with famine conditions; El Fasher atrocities; external sponsors",
        "current_rung": 6,
        "ladder": LADDER_GENERIC,
        "participants": {"SDN": 1.0, "TCD": 0.5, "SSD": 0.5, "EGY": 0.3, "ARE": 0.2, "ETH": 0.2, "LBY": 0.2},
        "summary": "The world's largest humanitarian crisis, with Red Sea access and gold smuggling networks at stake. RSF drone strikes on Port Sudan threaten Red Sea facilities.",
        "retaliation": [
            {"actor": "RSF", "actor_iso": "SDN", "action": "Drone strikes on Port Sudan infrastructure", "target": "SAF / Red Sea port", "target_iso": "SDN", "prob": 0.50, "severity": 3, "horizon": "0–30d", "channels": ["South Sudan crude exports", "Red Sea"], "tripwire": "SAF offensive in Kordofan"},
        ],
        "scenarios": [
            {"name": "War of attrition", "prob": 0.75, "brent": 0, "gold": 0, "spx": 0, "desc": "Humanitarian catastrophe; limited market impact."},
            {"name": "Quad-mediated truce", "prob": 0.25, "brent": 0, "gold": 0, "spx": 0, "desc": "Humanitarian corridors."},
        ],
        "indicators": ["IPC famine data", "Port Sudan incidents", "Quad (US/KSA/UAE/Egypt) statements"],
    },
]

THEATRE_BY_ID = {t["id"]: t for t in THEATRES}
