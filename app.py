import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="F1 26 Coop Championship",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp { background-color: #0b0e14; color: #f1f1f1; }
        .main-header {
            background: linear-gradient(90deg, #e10600 0%, #1e222d 100%);
            padding: 18px 22px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 8px solid #ff1801;
        }
        .current-race-box {
            background: #151922;
            border: 2px solid #e10600;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
""",
    unsafe_allow_html=True,
)

POINTS_SYSTEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

# 11 Teams & 22 Fahrer (Cadillac mit Bottas & Pérez)
OFFICIAL_GRID = {
    "Ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    "McLaren": ["Lando Norris", "Oscar Piastri"],
    "Red Bull": ["Max Verstappen", "Liam Lawson"],
    "Mercedes": ["George Russell", "Kimi Antonelli"],
    "Aston Martin": ["Fernando Alonso", "Lance Stroll"],
    "Williams": ["Carlos Sainz", "Alex Albon"],
    "Alpine": ["Pierre Gasly", "Jack Doohan"],
    "RB": ["Yuki Tsunoda", "Isack Hadjar"],
    "Sauber / Audi": ["Nico Hülkenberg", "Gabriel Bortoleto"],
    "Haas": ["Esteban Ocon", "Oliver Bearman"],
    "Cadillac": ["Valtteri Bottas", "Sergio Pérez"],
}

# Dezente, blasse Teamfarben für die Zeilen-Hinterlegung
TEAM_TINTS = {
    "Ferrari": "rgba(232, 0, 32, 0.18)",
    "McLaren": "rgba(255, 128, 0, 0.18)",
    "Red Bull": "rgba(54, 113, 198, 0.18)",
    "Mercedes": "rgba(39, 244, 210, 0.18)",
    "Aston Martin": "rgba(34, 153, 113, 0.18)",
    "Williams": "rgba(100, 196, 255, 0.18)",
    "Alpine": "rgba(0, 147, 204, 0.18)",
    "RB": "rgba(102, 146, 255, 0.18)",
    "Sauber / Audi": "rgba(82, 226, 82, 0.18)",
    "Haas": "rgba(182, 186, 189, 0.18)",
    "Cadillac": "rgba(218, 165, 32, 0.18)",
}

SEASON_2026_CALENDAR = [
    "🇧🇭 1. Bahrain",
    "🇸🇦 2. Saudi-Arabien",
    "🇦🇺 3. Australien",
    "🇯🇵 4. Japan",
    "🇨🇳 5. China",
    "🇺🇸 6. Miami",
    "🇮🇹 7. Imola",
    "🇲🇨 8. Monaco",
    "🇪🇸 9. Barcelona",
    "🇨🇦 10. Montreal",
    "🇦🇹 11. Österreich",
    "🇬🇧 12. Silverstone",
    "🇧🇪 13. Spa",
    "🇭🇺 14. Budapest",
    "🇳🇱 15. Zandvoort",
    "🇮🇹 16. Monza",
    "🇪🇸 17. Madrid",
    "🇦🇿 18. Baku",
    "🇸🇬 19. Singapur",
    "🇺🇸 20. Austin",
    "🇲🇽 21. Mexiko",
    "🇧🇷 22. São Paulo",
    "🇶🇦 23. Katar",
    "🇦🇪 24. Abu Dhabi",
]

DATA_FILE = "career_save.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"career_started": False, "races": []}


def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)


data = load_data()

st.markdown(
    """
    <div class="main-header">
        <h1 style="margin:0; font-size: 2rem;">🏎️ FORMULA 1 KOOP-KARRIERE 2026</h1>
        <p style="margin:4px 0 0 0; opacity: 0.85;">Meisterschafts-Hub für Lucas & Tim</p>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### ⚙️ Steuerung")
    if st.button("💣 Karriere komplett zurücksetzen", use_container_width=True):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

# ----------------------------------------------------
# 1. SETUP
# ----------------------------------------------------
if not data.get("career_started", False):
    st.subheader("🏁 Cockpit-Setup")
    with st.form("setup_form"):
        col_l, col_t = st.columns(2)
        teams = sorted(list(OFFICIAL_GRID.keys()))

        with col_l:
            st.markdown("### Cockpit: Lucas")
            lucas_team = st.selectbox("Team", teams, key="l_team")
            lucas_seat = st.selectbox(
                "Ersetzt Fahrer", OFFICIAL_GRID[lucas_team], key="l_seat"
            )

        with col_t:
            st.markdown("### Cockpit: Tim")
            tim_team = st.selectbox("Team", teams, key="t_team")
            avail_tim = [d for d in OFFICIAL_GRID[tim_team] if d != lucas_seat]
            if not avail_tim:
                avail_tim = OFFICIAL_GRID[tim_team]
            tim_seat = st.selectbox(
                "Ersetzt Fahrer", avail_tim, key="t_seat"
            )

        if st.form_submit_button(
            "Saison starten", type="primary", use_container_width=True
        ):
            if lucas_seat == tim_seat:
                st.error("Ihr könnt nicht denselben Fahrer im selben Team ersetzen.")
            else:
                data["career_started"] = True
                data["lucas"] = {
                    "current_team": lucas_team,
                    "replaces": lucas_seat,
                    "transfers_used": 0,
                }
                data["tim"] = {
                    "current_team": tim_team,
                    "replaces": tim_seat,
                    "transfers_used": 0,
                }
                data["races"] = []
                save_data(data)
                st.rerun()
    st.stop()

# ----------------------------------------------------
# 2. STARTERFELD & PUNKTE
# ----------------------------------------------------
active_drivers = {}
for team, drivers in OFFICIAL_GRID.items():
    for d in drivers:
        if d != data["lucas"]["replaces"] and d != data["tim"]["replaces"]:
            active_drivers[d] = team

active_drivers["Lucas"] = data["lucas"]["current_team"]
active_drivers["Tim"] = data["tim"]["current_team"]

driver_stats = {
    d: {
        "Punkte": 0,
        "Siege": 0,
        "Podien": 0,
        "Top 10": 0,
        "Fastest Laps": 0,
        "DNFs": 0,
        "Team": active_drivers[d],
    }
    for d in active_drivers
}
constructor_points = {t: 0 for t in OFFICIAL_GRID.keys()}

for race in data["races"]:
    res = race["results"]
    dnfs = race.get("dnfs", [])
    fl = race.get("fastest_lap")
    race_teams = race.get("driver_teams", active_drivers)

    if fl and fl in driver_stats and fl in res[:10]:
        driver_stats[fl]["Fastest Laps"] += 1
        driver_stats[fl]["Punkte"] += 1
        t = race_teams.get(fl, active_drivers.get(fl))
        if t:
            constructor_points[t] += 1

    for dnf_driver in dnfs:
        if dnf_driver in driver_stats:
            driver_stats[dnf_driver]["DNFs"] += 1

    for pos, driver in enumerate(res, start=1):
        if driver in driver_stats:
            pts = POINTS_SYSTEM.get(pos, 0)
            driver_stats[driver]["Punkte"] += pts
            t = race_teams.get(driver, active_drivers.get(driver))
            if t:
                constructor_points[t] += pts

            if pos <= 10:
                driver_stats[driver]["Top 10"] += 1
            if pos == 1:
                driver_stats[driver]["Siege"] += 1
            if pos <= 3:
                driver_stats[driver]["Podien"] += 1

sorted_drivers = sorted(
    active_drivers.keys(),
    key=lambda d: (
        driver_stats[d]["Punkte"],
        driver_stats[d]["Siege"],
        driver_stats[d]["Podien"],
        driver_stats[d]["Top 10"],
    ),
    reverse=True,
)

tab_tables, tab_matrix, tab_duel, tab_input, tab_market, tab_history = st.tabs(
    [
        "📊 WM-Stände",
        "🏁 Rennergebnisse",
        "⚔️ Teamduell",
        "➕ Nächstes Rennen",
        "🔄 Fahrermarkt",
        "🗓️ Kalender",
    ]
)

# --- TAB 1: WM-STÄNDE MIT DEZENTER ZEILENFARBE ---
with tab_tables:
    col_drivers, col_constructors = st.columns([3, 2], gap="large")

    with col_drivers:
        st.subheader("Fahrerwertung")
        drivers_rows = []
        for rank, d in enumerate(sorted_drivers, start=1):
            s = driver_stats[d]
            drivers_rows.append(
                {
                    "#": rank,
                    "Fahrer": d,
                    "Team": s["Team"],
                    "Punkte": s["Punkte"],
                    "Siege": s["Siege"],
                    "Podien": s["Podien"],
                    "FL": s["Fastest Laps"],
                    "DNF": s["DNFs"],
                }
            )
        df_display_drivers = pd.DataFrame(drivers_rows).set_index("#")

        # Färbt die Zeile dezent in der jeweiligen Teamfarbe ein
        def highlight_user_rows(row):
            driver_name = row["Fahrer"]
            if driver_name in ["Lucas", "Tim"]:
                team = active_drivers.get(driver_name)
                bg_color = TEAM_TINTS.get(team, "rgba(255, 255, 255, 0.12)")
                return [
                    f"background-color: {bg_color}; font-weight: bold;"
                ] * len(row)
            return [""] * len(row)

        styled_drivers = df_display_drivers.style.apply(
            highlight_user_rows, axis=1
        )
        st.table(styled_drivers)

    with col_constructors:
        st.subheader("Konstrukteurswertung")
        sorted_teams = sorted(
            constructor_points.items(), key=lambda x: x[1], reverse=True
        )
        teams_rows = []
        for rank, (team, pts) in enumerate(sorted_teams, start=1):
            teams_rows.append({"#": rank, "Team": team, "Punkte": pts})
        df_display_teams = pd.DataFrame(teams_rows).set_index("#")

        def highlight_user_teams(row):
            team_name = row["Team"]
            if team_name in [
                active_drivers["Lucas"],
                active_drivers["Tim"],
            ]:
                bg_color = TEAM_TINTS.get(
                    team_name, "rgba(255, 255, 255, 0.12)"
                )
                return [
                    f"background-color: {bg_color}; font-weight: bold;"
                ] * len(row)
            return [""] * len(row)

        styled_teams = df_display_teams.style.apply(
            highlight_user_teams, axis=1
        )
        st.table(styled_teams)

# --- TAB 2: RENNERGEBNISSE ---
with tab_matrix:
    st.subheader("Rennergebnis-Matrix")
    if not data["races"]:
        st.info("Noch keine Rennen erfasst.")
    else:
        race_rows = []
        for r in data["races"]:
            row = {"Grand Prix": r["track"]}
            fl_driver = r.get("fastest_lap")
            dnfs = r.get("dnfs", [])

            for d in sorted_drivers:
                if d in dnfs:
                    row[d] = "DNF"
                elif d in r["results"]:
                    pos = r["results"].index(d) + 1
                    txt = f"P{pos}"
                    if d == fl_driver:
                        txt += " 🟣"
                    row[d] = txt
                else:
                    row[d] = "-"
            race_rows.append(row)

        df_matrix = pd.DataFrame(race_rows).set_index("Grand Prix")

        def color_cells(val):
            if not isinstance(val, str) or val == "-":
                return "color: #444; text-align: center;"
            if val == "DNF":
                return "background-color: #8b0000; color: #ffffff; font-weight: bold; text-align: center;"
            if "🟣" in val:
                return "background-color: #8A2BE2; color: #ffffff; font-weight: bold; text-align: center;"
            if val == "P1":
                return "background-color: #FFD700; color: #000; font-weight: bold; text-align: center;"
            if val == "P2":
                return "background-color: #C0C0C0; color: #000; font-weight: bold; text-align: center;"
            if val == "P3":
                return "background-color: #CD7F32; color: #fff; font-weight: bold; text-align: center;"
            if any(val == f"P{i}" for i in range(4, 11)):
                return "background-color: #1e4d2b; color: #81c784; font-weight: 500; text-align: center;"
            if any(val == f"P{i}" for i in range(11, 23)):
                return "background-color: #1a1e26; color: #888888; text-align: center;"
            return "text-align: center;"

        st.dataframe(
            df_matrix.style.applymap(color_cells),
            use_container_width=True,
            height=580,
        )

# --- TAB 3: TEAM-DUELL ---
with tab_duel:
    st.subheader("Head-to-Head: Lucas vs. Tim")
    l_pts = driver_stats["Lucas"]["Punkte"]
    t_pts = driver_stats["Tim"]["Punkte"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Punkte", f"{l_pts} : {t_pts}", delta=f"{l_pts - t_pts} Differenz")
    m2.metric(
        "Siege",
        f"{driver_stats['Lucas']['Siege']} : {driver_stats['Tim']['Siege']}",
    )
    m3.metric(
        "Podien",
        f"{driver_stats['Lucas']['Podien']} : {driver_stats['Tim']['Podien']}",
    )
    m4.metric(
        "Schnellste Runden",
        f"{driver_stats['Lucas']['Fastest Laps']} : {driver_stats['Tim']['Fastest Laps']}",
    )

    st.write(
        f"**Teams:** Lucas fährt für **{data['lucas']['current_team']}** | Tim fährt für **{data['tim']['current_team']}**"
    )

# --- TAB 4: ERFASSUNG ---
with tab_input:
    completed = len(data["races"])
    if completed >= len(SEASON_2026_CALENDAR):
        st.success("Saison ist beendet.")
    else:
        current_track = SEASON_2026_CALENDAR[completed]

        st.markdown(
            f"""
            <div class="current-race-box">
                <h3 style="margin:0; color:#e10600;">ANSTEHENDER GRAND PRIX</h3>
                <h2 style="margin:5px 0 0 0;">{current_track}</h2>
                <p style="margin:2px 0 0 0; opacity:0.8;">Rennen {completed + 1} von {len(SEASON_2026_CALENDAR)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_drivers_list = sorted(list(active_drivers.keys()))

        with st.form("full_grid_form"):
            st.write("### Zieldurchfahrt Platz 1 bis 22")
            c1, c2, c3, c4 = st.columns(4)
            full_results = []

            for i in range(1, 23):
                col = (
                    c1
                    if i <= 6
                    else (c2 if i <= 12 else (c3 if i <= 18 else c4))
                )
                with col:
                    default_d = (
                        "Lucas"
                        if i == 1
                        else (
                            "Tim"
                            if i == 2
                            else all_drivers_list[(i - 1) % len(all_drivers_list)]
                        )
                    )
                    idx = (
                        all_drivers_list.index(default_d)
                        if default_d in all_drivers_list
                        else 0
                    )
                    picked = st.selectbox(
                        f"Platz {i}",
                        all_drivers_list,
                        index=idx,
                        key=f"grid_p_{i}",
                    )
                    full_results.append(picked)

            st.markdown("---")
            st.write("### Ausfälle")
            dnf_picks = st.multiselect(
                "Fahrer auswählen, die nicht ins Ziel kamen (DNF):",
                all_drivers_list,
            )

            st.markdown("---")
            fl_pick = st.selectbox(
                "🟣 Schnellste Rennrunde",
                ["Keine"] + [d for d in full_results if d not in dnf_picks],
            )

            submit = st.form_submit_button(
                "Grand Prix speichern & weiter",
                type="primary",
                use_container_width=True,
            )

            if submit:
                if len(set(full_results)) != 22:
                    st.error(
                        "Fehler: Jeder der 22 Plätze muss eindeutig belegt sein."
                    )
                else:
                    data["races"].append(
                        {
                            "track": current_track,
                            "results": full_results,
                            "dnfs": dnf_picks,
                            "fastest_lap": fl_pick if fl_pick != "Keine" else None,
                            "driver_teams": dict(active_drivers),
                        }
                    )
                    save_data(data)
                    st.rerun()

# --- TAB 5: FAHRERMARKT ---
with tab_market:
    st.subheader("Fahrermarkt")
    col_tl, col_tt = st.columns(2)

    with col_tl:
        st.markdown(f"### Lucas (Aktuell: {data['lucas']['current_team']})")
        if data["lucas"]["transfers_used"] >= 1:
            st.warning("Wechsel-Joker für diese Saison verbraucht.")
        else:
            with st.form("transfer_lucas"):
                new_team = st.selectbox(
                    "Neues Team",
                    [
                        t
                        for t in OFFICIAL_GRID.keys()
                        if t != data["lucas"]["current_team"]
                    ],
                )
                replaced = st.selectbox("Wen ersetzt du?", OFFICIAL_GRID[new_team])
                if st.form_submit_button("Zu diesem Team wechseln"):
                    data["lucas"]["current_team"] = new_team
                    data["lucas"]["replaces"] = replaced
                    data["lucas"]["transfers_used"] += 1
                    save_data(data)
                    st.rerun()

    with col_tt:
        st.markdown(f"### Tim (Aktuell: {data['tim']['current_team']})")
        if data["tim"]["transfers_used"] >= 1:
            st.warning("Wechsel-Joker für diese Saison verbraucht.")
        else:
            with st.form("transfer_tim"):
                new_team = st.selectbox(
                    "Neues Team",
                    [
                        t
                        for t in OFFICIAL_GRID.keys()
                        if t != data["tim"]["current_team"]
                    ],
                )
                replaced = st.selectbox("Wen ersetzt du?", OFFICIAL_GRID[new_team])
                if st.form_submit_button("Zu diesem Team wechseln"):
                    data["tim"]["current_team"] = new_team
                    data["tim"]["replaces"] = replaced
                    data["tim"]["transfers_used"] += 1
                    save_data(data)
                    st.rerun()

# --- TAB 6: KALENDER & HISTORIE ---
with tab_history:
    st.subheader("Saisonkalender")
    for idx, tr in enumerate(SEASON_2026_CALENDAR):
        if idx < len(data["races"]):
            r = data["races"][idx]
            with st.expander(
                f"✅ {tr} — Sieger: 🏆 {r['results'][0]} (FL: {r.get('fastest_lap', '-')})"
            ):
                res_df = pd.DataFrame(
                    {
                        "Pos": [f"P{n}" for n in range(1, 23)],
                        "Fahrer": r["results"],
                        "Status": [
                            "DNF" if d in r.get("dnfs", []) else "Ziel"
                            for d in r["results"]
                        ],
                    }
                )
                st.table(res_df)
                if st.button("Dieses Rennen löschen", key=f"del_{idx}"):
                    data["races"].pop(idx)
                    save_data(data)
                    st.rerun()
        else:
            st.markdown(f"⚪ *{tr}* (Noch ausstehend)")
