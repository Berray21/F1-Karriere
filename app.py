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

# Custom Styling für F1-Ästhetik
st.markdown(
    """
    <style>
        .stApp { background-color: #0b0e14; color: #f1f1f1; }
        .main-header {
            background: linear-gradient(90deg, #e10600 0%, #1e222d 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 8px solid #ff1801;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
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

OFFICIAL_GRID = {
    "Ferrari": ["Charles Leclerc", "Lewis Hamilton"],
    "McLaren": ["Lando Norris", "Oscar Piastri"],
    "Red Bull": ["Max Verstappen", "Liam Lawson"],
    "Mercedes": ["George Russell", "Kimi Antonelli"],
    "Aston Martin": ["Fernando Alonso", "Lance Stroll"],
    "Williams": ["Carlos Sainz", "Alex Albon"],
    "Alpine": ["Pierre Gasly", "Jack Doohan"],
    "RB": ["Yuki Tsunoda", "Isack Hadjar"],
    "Sauber": ["Nico Hülkenberg", "Gabriel Bortoleto"],
    "Haas": ["Esteban Ocon", "Oliver Bearman"],
}

# Offizieller F1-Kalender 2026 (24 Grands Prix inklusive Barcelona & Madrid)
SEASON_2026_CALENDAR = [
    "🇧🇭 1. Bahrain (Sakhir)",
    "🇸🇦 2. Saudi-Arabien (Dschidda)",
    "🇦🇺 3. Australien (Melbourne)",
    "🇯🇵 4. Japan (Suzuka)",
    "🇨🇳 5. China (Shanghai)",
    "🇺🇸 6. USA (Miami)",
    "🇮🇹 7. Italien (Imola / Emilia-Romagna)",
    "🇲🇨 8. Monaco (Monte Carlo)",
    "🇪🇸 9. Spanien (Barcelona-Catalunya)",
    "🇨🇦 10. Kanada (Montreal)",
    "🇦🇹 11. Österreich (Spielberg)",
    "🇬🇧 12. Großbritannien (Silverstone)",
    "🇧🇪 13. Belgien (Spa-Francorchamps)",
    "🇭🇺 14. Ungarn (Budapest)",
    "🇳🇱 15. Niederlande (Zandvoort)",
    "🇮🇹 16. Italien (Monza)",
    "🇪🇸 17. Spanien (Madrid - IFEMA)",
    "🇦🇿 18. Aserbaidschan (Baku)",
    "🇸🇬 19. Singapur (Marina Bay)",
    "🇺🇸 20. USA (Austin)",
    "🇲🇽 21. Mexiko (Mexiko-Stadt)",
    "🇧🇷 22. Brasilien (São Paulo)",
    "🇶🇦 23. Katar (Lusail)",
    "🇦🇪 24. Abu Dhabi (Yas Marina)",
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

# Header
st.markdown(
    """
    <div class="main-header">
        <h1 style="margin:0; font-size: 2.1rem;">🏎️ FORMULA 1 KOOP-KARRIERE 2026</h1>
        <p style="margin:4px 0 0 0; opacity: 0.85;">Offizielles Meisterschafts-Hub für Lucas & Tim</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- SEITENLEISTE MIT ADMIN-RESET ---
with st.sidebar:
    st.markdown("### ⚙️ Steuerung & Test-Reset")
    st.caption("Hier kannst du gefahrlos alles testen und komplett zurücksetzen.")
    if st.button("💣 Karriere komplett zurücksetzen", use_container_width=True):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.warning("Spielstand gelöscht! Frischer Neustart...")
        st.rerun()

# ----------------------------------------------------
# 1. SETUP-BILDSCHIRM (BEIM ERSTEN START)
# ----------------------------------------------------
if not data.get("career_started", False):
    st.subheader("🏁 Karriere-Setup: Wählt eure Cockpits")
    st.write("Wählt euer Team und welchen Stammfahrer ihr dort ersetzt:")

    with st.form("setup_form"):
        col_l, col_t = st.columns(2)
        teams = sorted(list(OFFICIAL_GRID.keys()))

        with col_l:
            st.markdown("### 🟢 Cockpit: Lucas")
            lucas_team = st.selectbox("Team für Lucas", teams, key="l_team")
            lucas_seat = st.selectbox(
                "Welchen Fahrer ersetzt Lucas?",
                OFFICIAL_GRID[lucas_team],
                key="l_seat",
            )

        with col_t:
            st.markdown("### 🟠 Cockpit: Tim")
            tim_team = st.selectbox("Team für Tim", teams, key="t_team")
            avail_tim = [d for d in OFFICIAL_GRID[tim_team] if d != lucas_seat]
            if not avail_tim:
                avail_tim = OFFICIAL_GRID[tim_team]
            tim_seat = st.selectbox(
                "Welchen Fahrer ersetzt Tim?", avail_tim, key="t_seat"
            )

        if st.form_submit_button(
            "🚀 Saison 2026 starten", type="primary", use_container_width=True
        ):
            if lucas_seat == tim_seat:
                st.error(
                    "Ihr könnt nicht denselben Fahrer im selben Team ersetzen!"
                )
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
                st.success("Karriere gestartet!")
                st.rerun()

    st.stop()

# ----------------------------------------------------
# 2. AKTIVES STARTERFELD ZUSAMMENSTELLEN
# ----------------------------------------------------
active_drivers = {}
for team, drivers in OFFICIAL_GRID.items():
    for d in drivers:
        if d != data["lucas"]["replaces"] and d != data["tim"]["replaces"]:
            active_drivers[d] = team

active_drivers["Lucas"] = data["lucas"]["current_team"]
active_drivers["Tim"] = data["tim"]["current_team"]

# ----------------------------------------------------
# 3. PUNKTE & BERECHNUNG
# ----------------------------------------------------
driver_stats = {
    d: {
        "Punkte": 0,
        "Siege": 0,
        "Podien": 0,
        "Fastest Laps": 0,
        "Team": active_drivers[d],
    }
    for d in active_drivers
}
constructor_points = {t: 0 for t in OFFICIAL_GRID.keys()}

for race in data["races"]:
    res = race["results"]
    fl = race.get("fastest_lap")
    race_teams = race.get("driver_teams", active_drivers)

    if fl and fl in driver_stats and fl in res[:10]:
        driver_stats[fl]["Fastest Laps"] += 1
        driver_stats[fl]["Punkte"] += 1
        t = race_teams.get(fl, active_drivers.get(fl))
        if t:
            constructor_points[t] += 1

    for pos, driver in enumerate(res, start=1):
        if driver in driver_stats:
            pts = POINTS_SYSTEM.get(pos, 0)
            driver_stats[driver]["Punkte"] += pts
            t = race_teams.get(driver, active_drivers.get(driver))
            if t:
                constructor_points[t] += pts
            if pos == 1:
                driver_stats[driver]["Siege"] += 1
            if pos <= 3:
                driver_stats[driver]["Podien"] += 1

# Sortierte Fahrer nach aktuellem WM-Stand (für X-Achse der Matrix)
sorted_drivers = sorted(
    active_drivers.keys(),
    key=lambda d: (
        driver_stats[d]["Punkte"],
        driver_stats[d]["Siege"],
        driver_stats[d]["Podien"],
    ),
    reverse=True,
)

# ----------------------------------------------------
# 4. TABS
# ----------------------------------------------------
tab_tables, tab_matrix, tab_duel, tab_input, tab_market, tab_history = st.tabs(
    [
        "📊 WM-Stände",
        "🏁 Rennergebnisse (Matrix)",
        "⚔️ Teamduell",
        "➕ Nächstes Rennen",
        "🔄 Fahrermarkt",
        "🗓️ Kalender & Historie",
    ]
)

# --- TAB 1: WM-STÄNDE ---
with tab_tables:
    c_d, c_t = st.columns([3, 2], gap="large")
    with c_d:
        st.subheader("Fahrerwertung")
        df_d = (
            pd.DataFrame.from_dict(driver_stats, orient="index")
            .reset_index()
            .rename(columns={"index": "Fahrer"})
        )
        df_d = df_d.sort_values(
            by=["Punkte", "Siege", "Podien"], ascending=False
        ).reset_index(drop=True)
        df_d.index += 1
        st.dataframe(
            df_d[
                [
                    "Fahrer",
                    "Team",
                    "Punkte",
                    "Siege",
                    "Podien",
                    "Fastest Laps",
                ]
            ],
            use_container_width=True,
            height=520,
        )

    with c_t:
        st.subheader("Konstrukteurswertung")
        df_c = (
            pd.DataFrame(
                list(constructor_points.items()), columns=["Team", "Punkte"]
            )
            .sort_values(by="Punkte", ascending=False)
            .reset_index(drop=True)
        )
        df_c.index += 1
        st.dataframe(df_c, use_container_width=True, height=520)

# --- TAB 2: RENNERGEBNISSE (MATRIX-HEATMAP) ---
with tab_matrix:
    st.subheader("🏁 Rennergebnis-Matrix (Saison 2026)")
    st.caption(
        "Legende: 🟨 P1 (Gold) | 🥈 P2 (Silber) | 🥉 P3 (Bronze) | 🟩 Top 10 | 🟪 Schnellste Runde (Lila)"
    )

    if not data["races"]:
        st.info(
            "Noch keine Rennen gefahren. Sobald Rennen eingetragen sind, füllt sich die Matrix!"
        )
    else:
        # Matrix-Daten aufbauen: Y = Rennen, X = Fahrer
        race_rows = []
        for r in data["races"]:
            row = {"Grand Prix": r["track"]}
            fl_driver = r.get("fastest_lap")

            for d in sorted_drivers:
                if d in r["results"]:
                    pos = r["results"].index(d) + 1
                    txt = f"P{pos}"
                    if d == fl_driver:
                        txt += " 🟣"  # Lila Markierung
                    row[d] = txt
                else:
                    row[d] = "-"
            race_rows.append(row)

        df_matrix = pd.DataFrame(race_rows).set_index("Grand Prix")

        # Style-Funktion für F1-Farben
        def color_f1_cells(val):
            if not isinstance(val, str) or val == "-":
                return "color: #555555; text-align: center;"

            # Schnellste Runde hat Vorrang -> Pirelli Purple
            if "🟣" in val:
                return "background-color: #8A2BE2; color: #ffffff; font-weight: bold; text-align: center; border-radius: 4px;"

            if val == "P1":
                return "background-color: #FFD700; color: #000000; font-weight: bold; text-align: center; border-radius: 4px;"
            elif val == "P2":
                return "background-color: #C0C0C0; color: #000000; font-weight: bold; text-align: center; border-radius: 4px;"
            elif val == "P3":
                return "background-color: #CD7F32; color: #ffffff; font-weight: bold; text-align: center; border-radius: 4px;"
            elif val.startswith("P"):
                return "background-color: #1e4d2b; color: #81c784; font-weight: 500; text-align: center; border-radius: 4px;"

            return "text-align: center;"

        styled_matrix = df_matrix.style.applymap(color_f1_cells)
        st.dataframe(styled_matrix, use_container_width=True, height=520)

# --- TAB 3: TEAM-DUELL ---
with tab_duel:
    st.subheader("Head-to-Head: Lucas vs. Tim")
    l_pts = driver_stats["Lucas"]["Punkte"]
    t_pts = driver_stats["Tim"]["Punkte"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Punkte",
        f"{l_pts} : {t_pts}",
        delta=f"{l_pts - t_pts} Differenz",
    )
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
        f"**Cockpits:** Lucas fährt für **{data['lucas']['current_team']}** | Tim fährt für **{data['tim']['current_team']}**"
    )

# --- TAB 4: NÄCHSTES RENNEN EINTRAGEN ---
with tab_input:
    completed_races_count = len(data["races"])

    if completed_races_count >= len(SEASON_2026_CALENDAR):
        st.success(
            "🎉 Die Saison 2026 ist komplett beendet! Prüft die WM-Stände oder startet im Fahrermarkt eine neue Saison."
        )
    else:
        current_track = SEASON_2026_CALENDAR[completed_races_count]

        st.markdown(
            f"""
            <div class="current-race-box">
                <h3 style="margin:0; color:#e10600;">ANSTEHENDER GRAND PRIX</h3>
                <h2 style="margin:5px 0 0 0;">{current_track}</h2>
                <p style="margin:2px 0 0 0; opacity:0.8;">Rennen {completed_races_count + 1} von {len(SEASON_2026_CALENDAR)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("race_input_form"):
            st.write("Wähle die Top 10 Zieldurchfahrt:")
            all_d = sorted(list(active_drivers.keys()))
            col1, col2 = st.columns(2)
            results = []

            for i in range(1, 11):
                with col1 if i <= 5 else col2:
                    default_d = (
                        "Lucas"
                        if i == 1
                        else ("Tim" if i == 2 else all_d[i])
                    )
                    default_idx = (
                        all_d.index(default_d) if default_d in all_d else 0
                    )
                    choice = st.selectbox(
                        f"Platz {i}", all_d, index=default_idx, key=f"place_{i}"
                    )
                    results.append(choice)

            st.markdown("---")
            fl_pick = st.selectbox(
                "🟣 Schnellste Runde (+1 Punkt)",
                ["Keine / Außerhalb Top 10"] + results,
            )

            if st.form_submit_button(
                "💾 Grand Prix werten & Weiter zum nächsten Rennen",
                type="primary",
                use_container_width=True,
            ):
                if len(set(results)) != 10:
                    st.error(
                        "Fehler: Ein Fahrer darf nicht doppelt in den Top 10 stehen!"
                    )
                else:
                    data["races"].append(
                        {
                            "track": current_track,
                            "results": results,
                            "fastest_lap": (
                                fl_pick
                                if fl_pick != "Keine / Außerhalb Top 10"
                                else None
                            ),
                            "driver_teams": dict(active_drivers),
                        }
                    )
                    save_data(data)
                    st.success(f"{current_track} gewertet!")
                    st.rerun()

# --- TAB 5: FAHRERMARKT ---
with tab_market:
    st.subheader("Fahrermarkt (1 Wechsel pro Fahrer pro Saison)")
    col_tl, col_tt = st.columns(2)

    with col_tl:
        st.markdown(
            f"### Lucas (Aktuell: **{data['lucas']['current_team']}**)"
        )
        if data["lucas"]["transfers_used"] >= 1:
            st.warning("🔒 Wechsel-Joker für diese Saison verbraucht.")
        else:
            with st.form("t_lucas"):
                new_t = st.selectbox(
                    "Neues Team",
                    [
                        t
                        for t in OFFICIAL_GRID.keys()
                        if t != data["lucas"]["current_team"]
                    ],
                )
                rep = st.selectbox(
                    "Wen ersetzt du dort?", OFFICIAL_GRID[new_t]
                )
                if st.form_submit_button("Teamwechsel vollziehen"):
                    data["lucas"]["current_team"] = new_t
                    data["lucas"]["replaces"] = rep
                    data["lucas"]["transfers_used"] += 1
                    save_data(data)
                    st.rerun()

    with col_tt:
        st.markdown(f"### Tim (Aktuell: **{data['tim']['current_team']}**)")
        if data["tim"]["transfers_used"] >= 1:
            st.warning("🔒 Wechsel-Joker für diese Saison verbraucht.")
        else:
            with st.form("t_tim"):
                new_t = st.selectbox(
                    "Neues Team",
                    [
                        t
                        for t in OFFICIAL_GRID.keys()
                        if t != data["tim"]["current_team"]
                    ],
                )
                rep = st.selectbox(
                    "Wen ersetzt du dort?", OFFICIAL_GRID[new_t]
                )
                if st.form_submit_button("Teamwechsel vollziehen"):
                    data["tim"]["current_team"] = new_t
                    data["tim"]["replaces"] = rep
                    data["tim"]["transfers_used"] += 1
                    save_data(data)
                    st.rerun()

# --- TAB 6: KALENDER & HISTORIE ---
with tab_history:
    st.subheader("Offizieller Saisonkalender 2026")
    for idx, tr in enumerate(SEASON_2026_CALENDAR):
        if idx < len(data["races"]):
            r = data["races"][idx]
            with st.expander(
                f"✅ {tr} — Sieger: 🏆 {r['results'][0]} (FL: {r.get('fastest_lap', '-')})"
            ):
                st.table(
                    pd.DataFrame(
                        {
                            "Platz": [f"P{n}" for n in range(1, 11)],
                            "Fahrer": r["results"],
                        }
                    )
                )
                if st.button("Dieses Rennen löschen", key=f"del_{idx}"):
                    data["races"].pop(idx)
                    save_data(data)
                    st.rerun()
        else:
            st.markdown(f"⚪ *{tr}* (Noch ausstehend)")
