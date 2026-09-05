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
        .driver-card-lucas {
            background: #141822;
            border: 1px solid #232a38;
            border-left: 6px solid #00d2be;
            border-radius: 10px;
            padding: 15px 20px;
        }
        .driver-card-tim {
            background: #141822;
            border: 1px solid #232a38;
            border-right: 6px solid #ff8700;
            border-radius: 10px;
            padding: 15px 20px;
            text-align: right;
        }
        .danger-confirm-box {
            background: rgba(225, 6, 0, 0.15);
            border: 1px solid #e10600;
            border-radius: 8px;
            padding: 12px;
            margin-top: 10px;
            margin-bottom: 10px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

POINTS_SYSTEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

# 11 Teams & 22 Fahrer (Offizielles 2026er Grid mit Audi & aktuellem Red-Bull-Pool)
OFFICIAL_GRID = {
    "Ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    "McLaren": ["Lando Norris", "Oscar Piastri"],
    "Red Bull": ["Max Verstappen", "Isack Hadjar"],
    "Mercedes": ["George Russell", "Kimi Antonelli"],
    "Aston Martin": ["Fernando Alonso", "Lance Stroll"],
    "Williams": ["Carlos Sainz", "Alex Albon"],
    "Alpine": ["Pierre Gasly", "Franco Colapinto"],
    "Racing Bulls": ["Liam Lawson", "Arvid Lindblad"],
    "Audi": ["Nico Hülkenberg", "Gabriel Bortoleto"],
    "Haas": ["Esteban Ocon", "Oliver Bearman"],
    "Cadillac": ["Valtteri Bottas", "Sergio Pérez"],
}

TEAM_TINTS = {
    "Ferrari": "rgba(232, 0, 32, 0.18)",
    "McLaren": "rgba(255, 128, 0, 0.18)",
    "Red Bull": "rgba(54, 113, 198, 0.18)",
    "Mercedes": "rgba(39, 244, 210, 0.18)",
    "Aston Martin": "rgba(34, 153, 113, 0.18)",
    "Williams": "rgba(100, 196, 255, 0.18)",
    "Alpine": "rgba(0, 147, 204, 0.18)",
    "Racing Bulls": "rgba(102, 146, 255, 0.18)",
    "Audi": "rgba(235, 10, 30, 0.18)",
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

# ----------------------------------------------------
# SAVEGAME- & PROFILE-VERWALTUNG
# ----------------------------------------------------
SAVES_INDEX_FILE = "saves_index.json"


def get_available_saves():
    if os.path.exists(SAVES_INDEX_FILE):
        with open(SAVES_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return ["Saison 1 (2026)"]


def save_available_saves(saves_list):
    with open(SAVES_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(saves_list, f, indent=4, ensure_ascii=False)


all_saves = get_available_saves()

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

with st.sidebar:
    st.markdown("### 💾 Spielstand-Manager")
    selected_save = st.selectbox("Aktiver Spielstand / Saison:", all_saves)

    DATA_FILE = f"save_{selected_save.replace(' ', '_').replace('/', '_')}.json"

    with st.expander("➕ Neuer Spielstand"):
        new_save_name = st.text_input("Name für neue Saison/Karriere:")
        if st.button("Erstellen"):
            if new_save_name and new_save_name not in all_saves:
                all_saves.append(new_save_name)
                save_available_saves(all_saves)
                st.success(f"Spielstand '{new_save_name}' angelegt!")
                st.rerun()

    st.write("---")
    st.markdown("### ⚙️ Reset & Backup")

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            file_data = f.read()
        st.download_button(
            label="📥 Spielstand als Datei sichern",
            data=file_data,
            file_name=f"{selected_save}.json",
            mime="application/json",
            use_container_width=True,
        )

    if not st.session_state.confirm_delete:
        if st.button("💣 Aktiven Spielstand löschen", use_container_width=True):
            st.session_state.confirm_delete = True
            st.rerun()
    else:
        st.markdown(
            """
            <div class="danger-confirm-box">
                <b style="color: #ff4b4b;">⚠️ BIST DU DIR SICHER?</b><br>
                <small>Alle Daten dieses Spielstands werden unwiderruflich gelöscht!</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Ja, löschen", type="primary", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.session_state.confirm_delete = False
                st.rerun()
        with col_no:
            if st.button("Nein, abbrechen", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()


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
    f"""
    <div class="main-header">
        <h1 style="margin:0; font-size: 2rem;">🏎️ FORMULA 1 KOOP-KARRIERE</h1>
        <p style="margin:4px 0 0 0; opacity: 0.85;">Aktiver Spielstand: <b>{selected_save}</b></p>
    </div>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# 1. SETUP (DYNAMISCHE LIVE-AUSWAHL)
# ----------------------------------------------------
if not data.get("career_started", False):
    st.subheader(f"🏁 Cockpit-Setup für {selected_save}")
    col_l, col_t = st.columns(2)
    teams = sorted(list(OFFICIAL_GRID.keys()))

    with col_l:
        st.markdown("### Cockpit: Lucas")
        lucas_team = st.selectbox("Team für Lucas", teams, key="l_team_select")
        lucas_seat = st.selectbox(
            f"Welchen Fahrer ersetzt Lucas bei {lucas_team}?",
            OFFICIAL_GRID[lucas_team],
            key="l_seat_select",
        )

    with col_t:
        st.markdown("### Cockpit: Tim")
        tim_team = st.selectbox("Team für Tim", teams, key="t_team_select")
        if tim_team == lucas_team:
            avail_tim = [d for d in OFFICIAL_GRID[tim_team] if d != lucas_seat]
        else:
            avail_tim = OFFICIAL_GRID[tim_team]

        tim_seat = st.selectbox(
            f"Welchen Fahrer ersetzt Tim bei {tim_team}?",
            avail_tim,
            key="t_seat_select",
        )

    st.write("")
    if st.button("🚀 Saison starten", type="primary", use_container_width=True):
        if lucas_team == tim_team and lucas_seat == tim_seat:
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
        "⚔️ Head-to-Head",
        "➕ Nächstes Rennen",
        "🔄 Fahrermarkt",
        "🗓️ Kalender",
    ]
)

# --- TAB 1: WM-STÄNDE ---
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

# --- TAB 3: HEAD-TO-HEAD DUELL ---
with tab_duel:
    l_team = active_drivers["Lucas"]
    t_team = active_drivers["Tim"]
    l_rank = sorted_drivers.index("Lucas") + 1
    t_rank = sorted_drivers.index("Tim") + 1

    s_l = driver_stats["Lucas"]
    s_t = driver_stats["Tim"]

    l_ahead = 0
    t_ahead = 0
    for r in data["races"]:
        res = r["results"]
        dnfs = r.get("dnfs", [])
        l_pos = (
            999
            if "Lucas" in dnfs
            else (res.index("Lucas") if "Lucas" in res else 999)
        )
        t_pos = (
            999
            if "Tim" in dnfs
            else (res.index("Tim") if "Tim" in res else 999)
        )
        if l_pos < t_pos:
            l_ahead += 1
        elif t_pos < l_pos:
            t_ahead += 1

    c_card_l, c_vs, c_card_t = st.columns([5, 2, 5])

    with c_card_l:
        st.markdown(
            f"""
            <div class="driver-card-lucas">
                <div style="font-size: 0.8rem; text-transform: uppercase; color: #00d2be; font-weight: bold; letter-spacing: 1px;">COCKPIT 1</div>
                <div style="font-size: 1.8rem; font-weight: 900; margin: 2px 0; color: #ffffff;">LUCAS</div>
                <div style="color: #9aa5b5; font-size: 0.95rem;">{l_team} • <b style="color: #00d2be;">P{l_rank} in der WM</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_vs:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 25px;">
                <span style="background: #e10600; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 900; font-size: 0.9rem; letter-spacing: 1px;">VS</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_card_t:
        st.markdown(
            f"""
            <div class="driver-card-tim">
                <div style="font-size: 0.8rem; text-transform: uppercase; color: #ff8700; font-weight: bold; letter-spacing: 1px;">COCKPIT 2</div>
                <div style="font-size: 1.8rem; font-weight: 900; margin: 2px 0; color: #ffffff;">TIM</div>
                <div style="color: #9aa5b5; font-size: 0.95rem;">{t_team} • <b style="color: #ff8700;">P{t_rank} in der WM</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("---")
    st.subheader("📊 Leistungsvergleich")

    def display_duel_bar(category_name, val_l, val_t):
        total = val_l + val_t
        if total == 0:
            pct_l = 50.0
            pct_t = 50.0
        else:
            pct_l = round((val_l / total) * 100, 1)
            pct_t = round((val_t / total) * 100, 1)

        html_bar = f"""
        <div style="margin-bottom: 16px;">
            <div style="text-align: center; font-size: 0.85rem; font-weight: bold; letter-spacing: 1.5px; color: #8c96a5; text-transform: uppercase; margin-bottom: 6px;">
                {category_name}
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 14px;">
                <div style="font-size: 1.4rem; font-weight: 900; color: #00d2be; min-width: 45px; text-align: right;">
                    {val_l}
                </div>
                <div style="flex-grow: 1; height: 16px; border-radius: 8px; overflow: hidden; display: flex; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); background-color: #232936;">
                    <div style="width: {pct_l}%; background-color: #00d2be; height: 100%; transition: width 0.3s ease;"></div>
                    <div style="width: {pct_t}%; background-color: #ff8700; height: 100%; transition: width 0.3s ease;"></div>
                </div>
                <div style="font-size: 1.4rem; font-weight: 900; color: #ff8700; min-width: 45px; text-align: left;">
                    {val_t}
                </div>
            </div>
        </div>
        """
        st.markdown(html_bar, unsafe_allow_html=True)

    display_duel_bar("WM-Punkte", s_l["Punkte"], s_t["Punkte"])
    display_duel_bar("Rennsiege", s_l["Siege"], s_t["Siege"])
    display_duel_bar("Podiumsplätze", s_l["Podien"], s_t["Podien"])
    display_duel_bar("Top 10 Finishes", s_l["Top 10"], s_t["Top 10"])
    display_duel_bar(
        "Schnellste Rennrunden", s_l["Fastest Laps"], s_t["Fastest Laps"]
    )
    display_duel_bar("Besserer Zieleinlauf", l_ahead, t_ahead)
    display_duel_bar("Ausfälle (DNF)", s_l["DNFs"], s_t["DNFs"])

# --- TAB 4: ERFASSUNG ---
with tab_input:
    completed = len(data["races"])
    if completed >= len(SEASON_2026_CALENDAR):
        st.success(
            "🎉 Die Saison ist vollständig beendet! Ihr könnt im Fahrermarkt die nächste Saison freischalten."
        )
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
    st.subheader("Fahrermarkt (Maximal 1 Wechsel pro Fahrer pro Saison)")
    col_tl, col_tt = st.columns(2)

    with col_tl:
        st.markdown(f"### Lucas (Aktuell: {data['lucas']['current_team']})")
        if data["lucas"]["transfers_used"] >= 1:
            st.error(
                "🔒 Teamwechsel gesperrt: Dein Wechsel-Joker für diese Saison ist bereits aufgebraucht!"
            )
        else:
            avail_teams_l = [
                t for t in OFFICIAL_GRID.keys() if t != data["lucas"]["current_team"]
            ]
            new_team_l = st.selectbox("Neues Team für Lucas", avail_teams_l, key="m_tl")
            replaced_l = st.selectbox(
                f"Wen ersetzt du bei {new_team_l}?",
                OFFICIAL_GRID[new_team_l],
                key="m_rl",
            )
            if st.button("Zu diesem Team wechseln", key="btn_tl"):
                data["lucas"]["current_team"] = new_team_l
                data["lucas"]["replaces"] = replaced_l
                data["lucas"]["transfers_used"] = 1
                save_data(data)
                st.rerun()

    with col_tt:
        st.markdown(f"### Tim (Aktuell: {data['tim']['current_team']})")
        if data["tim"]["transfers_used"] >= 1:
            st.error(
                "🔒 Teamwechsel gesperrt: Tims Wechsel-Joker für diese Saison ist bereits aufgebraucht!"
            )
        else:
            avail_teams_t = [
                t for t in OFFICIAL_GRID.keys() if t != data["tim"]["current_team"]
            ]
            new_team_t = st.selectbox("Neues Team für Tim", avail_teams_t, key="m_tt")
            replaced_t = st.selectbox(
                f"Wen ersetzt du bei {new_team_t}?",
                OFFICIAL_GRID[new_team_t],
                key="m_rt",
            )
            if st.button("Zu diesem Team wechseln", key="btn_tt"):
                data["tim"]["current_team"] = new_team_t
                data["tim"]["replaces"] = replaced_t
                data["tim"]["transfers_used"] = 1
                save_data(data)
                st.rerun()

    st.write("---")
    completed_races = len(data.get("races", []))
    if completed_races >= len(SEASON_2026_CALENDAR):
        if st.button(
            "🏁 Saison beenden & Neue Saison freischalten (Joker zurücksetzen)"
        ):
            data["lucas"]["transfers_used"] = 0
            data["tim"]["transfers_used"] = 0
            save_data(data)
            st.success("Neue Saison gestartet! Die Wechsel-Joker sind wieder aktiv.")
            st.rerun()
    else:
        st.caption(
            f"ℹ️ Die Wechsel-Joker können erst nach Abschluss aller 24 Saisonrennen zurückgesetzt werden ({completed_races}/24 absolviert)."
        )

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
