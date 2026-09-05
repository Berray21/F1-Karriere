import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="F1 26 Coop Championship",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp { background-color: #0b0e14; color: #f1f1f1; }
        .main-header {
            background: linear-gradient(90deg, #e10600 0%, #1e222d 100%);
            padding: 22px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 8px solid #ff1801;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .setup-card {
            background: #151922;
            border: 1px solid #2e384d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
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

TRACKS = [
    "Bahrain (Sakhir)",
    "Saudi-Arabien (Jeddah)",
    "Australien (Melbourne)",
    "Japan (Suzuka)",
    "China (Shanghai)",
    "Miami",
    "Italien (Imola)",
    "Monaco",
    "Kanada (Montreal)",
    "Spanien (Barcelona)",
    "Österreich (Spielberg)",
    "Großbritannien (Silverstone)",
    "Ungarn (Hungaroring)",
    "Belgien (Spa-Francorchamps)",
    "Niederlande (Zandvoort)",
    "Italien (Monza)",
    "Aserbaidschan (Baku)",
    "Singapur (Marina Bay)",
    "USA (Austin)",
    "Mexiko (Mexiko-Stadt)",
    "Brasilien (Interlagos)",
    "Las Vegas",
    "Katar (Lusail)",
    "Abu Dhabi (Yas Marina)",
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
        <h1 style="margin:0; font-size: 2.1rem;">🏎️ FORMULA 1 KOOP-KARRIERE</h1>
        <p style="margin:4px 0 0 0; opacity: 0.85;">Offizielles Meisterschafts-Hub für Lucas & Tim</p>
    </div>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# 1. SETUP-BILDSCHIRM (WENN NOCH KEINE KARRIERE LÄUFT)
# ----------------------------------------------------
if not data.get("career_started", False):
    st.subheader("🏁 Karriere-Setup: Wählt eure Cockpits")
    st.write(
        "Ihr ersetzt zwei reale Fahrer im Starterfeld. Wählt euer Team und den Fahrer, dessen Sitz ihr übernehmt."
    )

    with st.form("career_start_form"):
        col_l, col_t = st.columns(2)

        teams_list = sorted(list(OFFICIAL_GRID.keys()))

        with col_l:
            st.markdown("### 🟢 Cockpit: Lucas")
            lucas_team = st.selectbox("Team für Lucas", teams_list, key="l_team")
            lucas_seat = st.selectbox(
                "Welchen Fahrer ersetzt Lucas?",
                OFFICIAL_GRID[lucas_team],
                key="l_seat",
            )

        with col_t:
            st.markdown("### 🟠 Cockpit: Tim")
            tim_team = st.selectbox("Team für Tim", teams_list, key="t_team")
            # Falls gleiches Team: Nur den anderen Fahrer zur Auswahl anbieten
            available_tim_seats = [
                d for d in OFFICIAL_GRID[tim_team] if d != lucas_seat
            ]
            if not available_tim_seats:
                available_tim_seats = OFFICIAL_GRID[tim_team]
            tim_seat = st.selectbox(
                "Welchen Fahrer ersetzt Tim?", available_tim_seats, key="t_seat"
            )

        start_btn = st.form_submit_button(
            "🚀 Saison starten", type="primary", use_container_width=True
        )

        if start_btn:
            if lucas_seat == tim_seat:
                st.error("Ihr könnt nicht denselben Fahrer im selben Team ersetzen!")
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
                st.success("Karriere gestartet! Viel Erfolg auf der Strecke.")
                st.rerun()

    st.stop()  # Bricht hier ab, bis das Setup abgeschlossen ist

# ----------------------------------------------------
# 2. AKTIVES STARTERFELD BERECHNEN
# ----------------------------------------------------
active_drivers = {}

# Alle echten Fahrer laden, außer die ersetzten
for team, drivers in OFFICIAL_GRID.items():
    for d in drivers:
        if d != data["lucas"]["replaces"] and d != data["tim"]["replaces"]:
            active_drivers[d] = team

# Lucas & Tim einfügen
active_drivers["Lucas"] = data["lucas"]["current_team"]
active_drivers["Tim"] = data["tim"]["current_team"]

# ----------------------------------------------------
# 3. PUNKTE & STATS BERECHNEN
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
    driver_teams_at_race = race.get(
        "driver_teams", active_drivers
    )  # Berücksichtigt historische Teams

    if fl and fl in driver_stats and fl in res[:10]:
        driver_stats[fl]["Fastest Laps"] += 1
        driver_stats[fl]["Punkte"] += 1
        team = driver_teams_at_race.get(fl, active_drivers.get(fl))
        if team:
            constructor_points[team] += 1

    for pos, driver in enumerate(res, start=1):
        if driver in driver_stats:
            pts = POINTS_SYSTEM.get(pos, 0)
            driver_stats[driver]["Punkte"] += pts

            team = driver_teams_at_race.get(driver, active_drivers.get(driver))
            if team:
                constructor_points[team] += pts

            if pos == 1:
                driver_stats[driver]["Siege"] += 1
            if pos <= 3:
                driver_stats[driver]["Podien"] += 1

# ----------------------------------------------------
# 4. TABS
# ----------------------------------------------------
tab_tables, tab_duel, tab_input, tab_market, tab_history = st.tabs(
    [
        "📊 WM-Stände",
        "⚔️ Teamduell",
        "➕ Rennen eintragen",
        "🔄 Fahrermarkt (Wechsel)",
        "🗓️ Historie",
    ]
)

# --- TAB 1: WM-STÄNDE ---
with tab_tables:
    col_d, col_c = st.columns([3, 2], gap="large")
    with col_d:
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
            height=480,
        )

    with col_c:
        st.subheader("Konstrukteurswertung")
        df_c = (
            pd.DataFrame(
                list(constructor_points.items()), columns=["Team", "Punkte"]
            )
            .sort_values(by="Punkte", ascending=False)
            .reset_index(drop=True)
        )
        df_c.index += 1
        st.dataframe(df_c, use_container_width=True, height=480)

# --- TAB 2: TEAM-DUELL ---
with tab_duel:
    st.subheader("Head-to-Head: Lucas vs. Tim")
    l_pts = driver_stats["Lucas"]["Punkte"]
    t_pts = driver_stats["Tim"]["Punkte"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Punkte",
        f"{l_pts} : {t_pts}",
        delta=f"{l_pts - t_pts} Diff (Lucas)",
    )
    m2.metric(
        "Siege", f"{driver_stats['Lucas']['Siege']} : {driver_stats['Tim']['Siege']}"
    )
    m3.metric(
        "Podien",
        f"{driver_stats['Lucas']['Podien']} : {driver_stats['Tim']['Podien']}",
    )
    m4.metric(
        "Fastest Laps",
        f"{driver_stats['Lucas']['Fastest Laps']} : {driver_stats['Tim']['Fastest Laps']}",
    )

    st.write(
        f"**Aktuelle Autos:** Lucas fährt für **{data['lucas']['current_team']}** | Tim fährt für **{data['tim']['current_team']}**"
    )

# --- TAB 3: RENNEN EINTRAGEN ---
with tab_input:
    st.subheader("Rennergebnis eintragen")
    completed = [r["track"] for r in data["races"]]
    next_tracks = [t for t in TRACKS if t not in completed]
    selected_track = st.selectbox(
        "Strecke auswählen", next_tracks if next_tracks else TRACKS
    )

    with st.form("race_result_form"):
        all_d = sorted(list(active_drivers.keys()))
        c1, c2 = st.columns(2)
        picks = []

        for i in range(1, 11):
            with c1 if i <= 5 else c2:
                default_val = (
                    "Lucas"
                    if i == 1
                    else ("Tim" if i == 2 else all_d[i])
                )
                idx = all_d.index(default_val) if default_val in all_d else 0
                choice = st.selectbox(
                    f"Platz {i}", all_d, index=idx, key=f"pos_{i}"
                )
                picks.append(choice)

        fl = st.selectbox("🟣 Schnellste Runde", ["Keine / Außerhalb Top 10"] + picks)
        submit_race = st.form_submit_button(
            "💾 Ergebnis werten", type="primary", use_container_width=True
        )

        if submit_race:
            if len(set(picks)) != 10:
                st.error("Fehler: Ein Fahrer darf nicht doppelt in den Top 10 sein!")
            else:
                data["races"].append(
                    {
                        "track": selected_track,
                        "results": picks,
                        "fastest_lap": (
                            fl if fl != "Keine / Außerhalb Top 10" else None
                        ),
                        "driver_teams": dict(active_drivers),
                    }
                )
                save_data(data)
                st.success(f"{selected_track} erfolgreich eingetragen!")
                st.rerun()

# --- TAB 4: FAHRERMARKT (EINMALIGER WECHSEL) ---
with tab_market:
    st.subheader("Fahrermarkt & Teamwechsel")
    st.info("Regel: Jeder Fahrer darf maximal **einmal pro Saison** das Team wechseln!")

    col_tl, col_tt = st.columns(2)

    # Transfer Lucas
    with col_tl:
        st.markdown(
            f"### Lucas (Aktuell: **{data['lucas']['current_team']}**)"
        )
        if data["lucas"]["transfers_used"] >= 1:
            st.warning("🔒 Wechsel-Joker für diese Saison bereits verbraucht.")
        else:
            with st.form("transfer_lucas"):
                new_t_l = st.selectbox(
                    "Neues Team für Lucas",
                    [
                        t
                        for t in OFFICIAL_GRID.keys()
                        if t != data["lucas"]["current_team"]
                    ],
                )
                rep_l = st.selectbox(
                    "Welchen Fahrer ersetzt du dort?", OFFICIAL_GRID[new_t_l]
                )
                btn_tl = st.form_submit_button("Teamwechsel vollziehen")
                if btn_tl:
                    data["lucas"]["current_team"] = new_t_l
                    data["lucas"]["replaces"] = rep_l
                    data["lucas"]["transfers_used"] += 1
                    save_data(data)
                    st.success(f"Wechsel zu {new_t_l} vollzogen!")
                    st.rerun()

    # Transfer Tim
    with col_tt:
        st.markdown(f"### Tim (Aktuell: **{data['tim']['current_team']}**)")
        if data["tim"]["transfers_used"] >= 1:
            st.warning("🔒 Wechsel-Joker für diese Saison bereits verbraucht.")
        else:
            with st.form("transfer_tim"):
                new_t_t = st.selectbox(
                    "Neues Team für Tim",
                    [
                        t
                        for t in OFFICIAL_GRID.keys()
                        if t != data["tim"]["current_team"]
                    ],
                )
                rep_t = st.selectbox(
                    "Welchen Fahrer ersetzt du dort?", OFFICIAL_GRID[new_t_t]
                )
                btn_tt = st.form_submit_button("Teamwechsel vollziehen")
                if btn_tt:
                    data["tim"]["current_team"] = new_t_t
                    data["tim"]["replaces"] = rep_t
                    data["tim"]["transfers_used"] += 1
                    save_data(data)
                    st.success(f"Wechsel zu {new_t_t} vollzogen!")
                    st.rerun()

    st.markdown("---")
    if st.button("⚠️ Neue Saison starten (Setzt Wechsel-Joker zurück)"):
        data["lucas"]["transfers_used"] = 0
        data["tim"]["transfers_used"] = 0
        save_data(data)
        st.success("Neue Saison aktiv – Wechsel-Joker wieder verfügbar!")
        st.rerun()

# --- TAB 5: HISTORIE ---
with tab_history:
    st.subheader("Bisherige Rennen")
    if not data["races"]:
        st.info("Noch keine Rennen gefahren.")
    else:
        for idx, r in enumerate(reversed(data["races"])):
            real_idx = len(data["races"]) - 1 - idx
            with st.expander(
                f"Rennen #{real_idx + 1}: {r['track']} — Sieger: 🏆 {r['results'][0]}"
            ):
                st.write(
                    f"**Schnellste Rennrunde:** {r.get('fastest_lap') or 'N/A'}"
                )
                team_mapping = r.get("driver_teams", active_drivers)
                res_df = pd.DataFrame(
                    {
                        "Pos": [f"P{n}" for n in range(1, 11)],
                        "Fahrer": r["results"],
                        "Team": [
                            team_mapping.get(d, "N/A") for d in r["results"]
                        ],
                    }
                )
                st.table(res_df)
                if st.button(
                    f"Rennen löschen ({r['track']})", key=f"del_{real_idx}"
                ):
                    data["races"].pop(real_idx)
                    save_data(data)
                    st.rerun()
