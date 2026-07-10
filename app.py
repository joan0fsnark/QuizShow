import streamlit as st
import random
import json

# Set up page styling and force dark theme elements
st.set_page_config(page_title="STEAM Quiz Show", layout="centered")

# --- CUSTOM CSS INJECTION FOR THE TKINTER LOOK ---
st.markdown(
    """
    <style>
        /* Global Background and Text Color Alignment */
        .stApp {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
            color: #ecf0f1 !important;
            font-family: 'Arial', sans-serif !important;
        }
        .stCaption {
            color: #3498db !important;
            font-size: 16px !important;
            font-weight: bold !important;
        }

        /* Direct HTML Button Styling overrides for Classroom Buzzers */
        .buzzer-link {
            display: block;
            text-align: center;
            padding: 12px 6px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 15px;
            text-decoration: none !important;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            transition: transform 0.1s ease;
        }
        .buzzer-link:hover {
            transform: scale(1.03);
            color: inherit;
        }
        .buzzer-link:active {
            transform: scale(0.98);
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# STEP 1: LOAD QUESTIONS DATA
# ---------------------------------------------------------
@st.cache_data
def load_all_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            cleaned_data = []
            for item in data:
                if isinstance(item, list) and len(item) > 0:
                    item = item[0]
                if isinstance(item, dict) and "options" in item and "answer" in item:
                    cleaned_data.append(item)
            random.shuffle(cleaned_data)
            return cleaned_data
    except Exception as e:
        st.error(f"Error loading questions.json: {e}")
        return []


# ---------------------------------------------------------
# STEP 2: INITIALIZE SESSION STATE (GAME MEMORY)
# ---------------------------------------------------------
if "questions" not in st.session_state:
    st.session_state.questions = load_all_questions()
    st.session_state.current_idx = 0
    st.session_state.scores = {}
    st.session_state.setup_complete = False
    st.session_state.reveal_pressed = False
    st.session_state.shuffled_options = []

COLOR_LIBRARY = {
    "Red": "#e74c3c",
    "Orange": "#e67e22",
    "Yellow": "#f1c40f",
    "Green": "#2ecc71",
    "Blue": "#3498db",
    "Purple": "#9b59b6"
}

# ---------------------------------------------------------
# STEP 3: INTERCEPT WEB BUZZER CLICKS
# ---------------------------------------------------------
# We capture custom link actions via URL parameters to respond instantly on click
query_params = st.query_params
if "action" in query_params:
    action_target = query_params["action"]
    # Clear parameter so it doesn't trigger repeatedly on refresh
    st.query_params.clear()

    if action_target == "skip":
        st.session_state.current_idx += 1
        st.session_state.reveal_pressed = False
        st.session_state.shuffled_options = []
        st.rerun()
    elif action_target.startswith("award_"):
        clicked_team = action_target.replace("award_", "").replace("_", " ")
        if clicked_team in st.session_state.scores:
            st.session_state.scores[clicked_team] += 1
        st.session_state.current_idx += 1
        st.session_state.reveal_pressed = False
        st.session_state.shuffled_options = []
        st.rerun()

# ---------------------------------------------------------
# STEP 4: SCREEN 1 - SETUP SCREEN
# ---------------------------------------------------------
if not st.session_state.setup_complete:
    st.markdown("<h1 style='text-align: center; color: #f1c40f !important;'>GAME SHOW SETUP</h1>",
                unsafe_allow_html=True)

    num_teams = st.slider("How many teams? (2-6):", min_value=2, max_value=6, value=3)

    color_options = list(COLOR_LIBRARY.keys())
    team_configs = {}

    st.write("### Assign Colors")
    for i in range(num_teams):
        default_color = color_options[i % len(color_options)]
        chosen_color = st.selectbox(f"Team {i + 1}:", color_options, index=color_options.index(default_color),
                                    key=f"setup_team_{i}")
        team_configs[f"Team {chosen_color}"] = COLOR_LIBRARY[chosen_color]

    st.write("")
    if st.button("🚀 START GAME", type="primary", use_container_width=True):
        selected_colors = list(team_configs.values())
        if len(set(selected_colors)) < len(selected_colors):
            st.error("Each team must have a unique color!")
        else:
            st.session_state.scores = {team: 0 for team in team_configs.keys()}
            st.session_state.team_colors = team_configs
            st.session_state.setup_complete = True
            st.rerun()

# ---------------------------------------------------------
# STEP 5: SCREEN 2 - GAMEPLAY DASHBOARD
# ---------------------------------------------------------
else:
    questions = st.session_state.questions
    idx = st.session_state.current_idx

    if idx >= len(questions) or not questions:
        st.markdown("<h1 style='text-align: center;'>🏆 Quiz Finished!</h1>", unsafe_allow_html=True)
        st.balloons()

        if st.session_state.scores:
            max_score = max(st.session_state.scores.values())
            winners = [team for team, score in st.session_state.scores.items() if score == max_score]

            if len(winners) == 1:
                st.success(f"### The winner is {winners[0]} with {max_score} points!")
            else:
                st.info(f"### It's a tie between: {', '.join(winners)} with {max_score} points!")

        if st.button("🔄 Play Again", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    else:
        current_q = questions[idx]

        if not st.session_state.shuffled_options:
            raw_opts = []
            for opt in current_q["options"]:
                clean_opt = str(opt).strip()
                if len(clean_opt) > 2 and (clean_opt[1] in [")", "."] or clean_opt[2] in [")", "."]):
                    clean_opt = clean_opt.split(")", 1)[-1].split(".", 1)[-1].strip()
                raw_opts.append(clean_opt)
            random.shuffle(raw_opts)

            letters = ["A)", "B)", "C)", "D)"]
            st.session_state.shuffled_options = [f"{letters[i]}  {raw_opts[i]}" for i in range(len(raw_opts))]

        st.caption(f"SUBJECT: {current_q.get('subject', 'GENERAL')}")

        # Locked-Size HTML Question Display Box
        st.markdown(
            f"""
            <div style="background-color: #34495e; padding: 20px; border-radius: 6px; border: 2px solid #415b76; min-height: 120px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                <h2 style="color: white !important; text-align: center; margin: 0; font-family: 'Arial', sans-serif; font-size: 22px; font-weight: bold; line-height: 1.4;">
                    Question {idx + 1}:<br>{current_q.get('question', '')}
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # High-Visibility Options Grid
        opts = st.session_state.shuffled_options
        col1, col2 = st.columns(2)

        option_style = """
        <div style="background-color: #1e272e; padding: 15px 20px; border-radius: 4px; border: 1px solid #34495e; margin: 8px 0;">
            <p style="color: #ecf0f1 !important; margin: 0; font-family: 'Arial', sans-serif; font-size: 16px; font-weight: bold;">
                {text}
            </p>
        </div>
        """

        with col1:
            st.markdown(option_style.format(text=opts[0]), unsafe_allow_html=True)
            if len(opts) > 2:
                st.markdown(option_style.format(text=opts[2]), unsafe_allow_html=True)
        with col2:
            if len(opts) > 1:
                st.markdown(option_style.format(text=opts[1]), unsafe_allow_html=True)
            if len(opts) > 3:
                st.markdown(option_style.format(text=opts[3]), unsafe_allow_html=True)

        st.write("")

        # Reveal Answer Section
        if st.button("👀 REVEAL CORRECT ANSWER", use_container_width=True):
            st.session_state.reveal_pressed = True

        if st.session_state.reveal_pressed:
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
                    <h3 style="color: #2ecc71 !important; font-family: 'Arial', sans-serif; font-weight: bold;">
                        🎯 Correct Answer: {current_q.get('answer', '')}
                    </h3>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Host Control Panel Frame Header
        st.markdown(
            """
            <div style="border-bottom: 1px solid #bdc3c7; margin-top: 20px; margin-bottom: 15px;">
                <p style="margin: 0; font-size: 14px; font-weight: bold; color: #bdc3c7 !important; letter-spacing: 1px;">
                    HOST PANEL: CLICK WHO BUZZED IN FIRST
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        host_cols = st.columns(len(st.session_state.scores) + 1)

        for i, team in enumerate(st.session_state.scores.keys()):
            team_color_hex = st.session_state.team_colors[team]
            # UPDATED: Force all button text to be highly visible black for readability
            text_color = "#000000"
            url_safe_team = team.replace(" ", "_")

            with host_cols[i]:
                st.markdown(
                    f"""
                            <a href="?action=award_{url_safe_team}" target="_self" class="buzzer-link" 
                               style="background-color: {team_color_hex}; color: {text_color} !important;">
                               🚨 {team}
                            </a>
                            """,
                    unsafe_allow_html=True
                )

        with host_cols[-1]:
            st.markdown(
                """
                <a href="?action=skip" target="_self" class="buzzer-link" 
                   style="background-color: #95a5a6; color: #000000 !important;">
                   ❌ Skip Q
                </a>
                """,
                unsafe_allow_html=True
            )

        # Leaderboard Section
        st.markdown(
            """
            <div style="border-bottom: 1px solid #bdc3c7; margin-top: 35px; margin-bottom: 15px;">
                <p style="margin: 0; font-size: 14px; font-weight: bold; color: #bdc3c7 !important; letter-spacing: 1px;">
                    CURRENT SCORES (1 POINT PER CORRECT ANSWER)
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        score_cols = st.columns(len(st.session_state.scores))
        for i, (team, score) in enumerate(st.session_state.scores.items()):
            team_color_hex = st.session_state.team_colors[team]
            with score_cols[i]:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 10px; border-radius: 4px; background-color: #34495e;">
                        <span style="color: {team_color_hex} !important; font-size: 18px; font-weight: bold;">
                            {team}: {score}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )