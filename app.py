import streamlit as st
import random
import json

# Set up the web page title and layout
st.set_page_config(page_title="STEAM Quiz Show", layout="centered")


# ---------------------------------------------------------
# STEP 1: LOAD QUESTIONS DATA
# ---------------------------------------------------------
@st.cache_data
def load_all_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            # Handle list-wrapped data safely
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

# ---------------------------------------------------------
# STEP 3: SCREEN 1 - SETUP SCREEN
# ---------------------------------------------------------
if not st.session_state.setup_complete:
    st.title("🏆 STEAM Quiz Show Setup")
    st.subheader("Configure your classroom teams")

    num_teams = st.slider("How many teams?", min_value=2, max_value=6, value=3)

    color_options = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple"]
    team_configs = {}

    st.write("### Assign Team Colors")
    for i in range(num_teams):
        # Pick default colors down the line to avoid immediate duplicates
        default_color = color_options[i % len(color_options)]
        chosen_color = st.selectbox(f"Team {i + 1} Color:", color_options, index=color_options.index(default_color),
                                    key=f"setup_team_{i}")
        team_configs[f"Team {chosen_color}"] = chosen_color

    if st.button("🚀 START GAME", type="primary", use_container_width=True):
        # Unique color check
        selected_colors = list(team_configs.keys())
        if len(set(selected_colors)) < len(selected_colors):
            st.error("Each team must have a unique color selection!")
        else:
            st.session_state.scores = {team: 0 for team in team_configs.keys()}
            st.session_state.setup_complete = True
            st.rerun()

# ---------------------------------------------------------
# STEP 4: SCREEN 2 - GAMEPLAY DASHBOARD
# ---------------------------------------------------------
else:
    questions = st.session_state.questions
    idx = st.session_state.current_idx

    # Check if the game is finished
    if idx >= len(questions) or not questions:
        st.title("🏁 Game Over!")
        st.balloons()

        # Determine winners
        if st.session_state.scores:
            max_score = max(st.session_state.scores.values())
            winners = [team for team, score in st.session_state.scores.items() if score == max_score]

            if len(winners) == 1:
                st.success(f"### 🏆 The winner is {winners[0]} with {max_score} points!")
            else:
                st.info(f"### 🤝 It's a tie between: {', '.join(winners)} with {max_score} points!")

        if st.button("🔄 Play Again", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    else:
        current_q = questions[idx]

        # Clean background formatting strings if options have A) or 1.
        if not st.session_state.shuffled_options:
            raw_opts = []
            for opt in current_q["options"]:
                clean_opt = str(opt).strip()
                if len(clean_opt) > 2 and (clean_opt[1] in [")", "."] or clean_opt[2] in [")", "."]):
                    clean_opt = clean_opt.split(")", 1)[-1].split(".", 1)[-1].strip()
                raw_opts.append(clean_opt)
            random.shuffle(raw_opts)

            letters = ["A)", "B)", "C)", "D)"]
            st.session_state.shuffled_options = [f"{letters[i]} {raw_opts[i]}" for i in range(len(raw_opts))]

        # Header Subject Banner
        st.caption(f"🎨 SUBJECT: {current_q.get('subject', 'GENERAL')}")
        st.title(f"Question {idx + 1}")

        # Fixed, styled Question Box using markdown card elements
        st.markdown(
            f"""
            <div style="background-color: #34495e; padding: 25px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #465d75;">
                <h3 style="color: white; text-align: center; margin: 0; font-family: sans-serif; line-height: 1.5;">
                    {current_q.get('question', '')}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Options Layout Grid
        col1, col2 = st.columns(2)
        opts = st.session_state.shuffled_options

        with col1:
            st.info(opts[0])
            if len(opts) > 2: st.info(opts[2])
        with col2:
            if len(opts) > 1: st.info(opts[1])
            if len(opts) > 3: st.info(opts[3])

        st.markdown("---")

        # Answer Section
        c_left, c_right = st.columns([1, 2])
        with c_left:
            if st.button("👀 Reveal Answer", use_container_width=True):
                st.session_state.reveal_pressed = True
        with c_right:
            if st.session_state.reveal_pressed:
                st.success(f"🎯 Correct Answer Target: {current_q.get('answer', '')}")

        st.markdown("### 🚨 Host Control Panel")
        st.write("Click the team that successfully buzzed in first to award 1 point:")

        # Map nice display colors for web context buttons
        color_map = {"Red": "red", "Orange": "orange", "Yellow": "secondary", "Green": "green", "Blue": "blue",
                     "Purple": "primary"}

        host_cols = st.columns(len(st.session_state.scores) + 1)

        for i, team in enumerate(st.session_state.scores.keys()):
            team_color = team.split(" ")[-1]
            btn_type = color_map.get(team_color, "secondary")

            with host_cols[i]:
                if st.button(f"🚨 {team}", type="primary" if btn_type == "primary" else "secondary",
                             use_container_width=True):
                    st.session_state.scores[team] += 1
                    st.session_state.current_idx += 1
                    st.session_state.reveal_pressed = False
                    st.session_state.shuffled_options = []
                    st.rerun()

        with host_cols[-1]:
            if st.button("❌ Skip Q", use_container_width=True):
                st.session_state.current_idx += 1
                st.session_state.reveal_pressed = False
                st.session_state.shuffled_options = []
                st.rerun()

        # Score Leaderboard Section at Bottom
        st.markdown("---")
        st.write("### 📊 Live Leaderboard")
        score_cols = st.columns(len(st.session_state.scores))
        for i, (team, score) in enumerate(st.session_state.scores.items()):
            with score_cols[i]:
                st.metric(label=team, value=f"{score} pts")