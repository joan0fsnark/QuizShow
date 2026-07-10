import tkinter as tk
from tkinter import messagebox, ttk
import random
import json

# ---------------------------------------------------------
# STEP 1: CONFIGURATION & GLOBAL GAME DATA (6 RAINBOW COLORS)
# ---------------------------------------------------------
COLOR_LIBRARY = {
    "Red": "#e74c3c",
    "Orange": "#e67e22",
    "Yellow": "#f1c40f",
    "Green": "#2ecc71",
    "Blue": "#3498db",
    "Purple": "#9b59b6"
}

# These will be populated dynamically from the setup window
TEAM_COLORS = {}
TEAMS = []
scores = {}

QUESTIONS_POOL = []
json_filename = "questions.json"

try:
    with open(json_filename, "r", encoding="utf-8") as file:
        QUESTIONS_POOL = json.load(file)
except FileNotFoundError:
    root_temp = tk.Tk()
    root_temp.withdraw()
    messagebox.showerror("Error", f"Could not find '{json_filename}'. Ensure it's in the same folder as this script!")
    exit()
except json.JSONDecodeError:
    root_temp = tk.Tk()
    root_temp.withdraw()
    messagebox.showerror("Error", f"'{json_filename}' has a formatting error. Check your commas/quotes!")
    exit()

random.shuffle(QUESTIONS_POOL)
current_question_index = 0

current_shuffled_options = []
current_correct_answer_text = ""

# Global widgets to be configured once setup is complete
score_labels = {}
option_labels = []
subject_label = None
question_label = None
answer_label = None
host_frame = None
root_game = None  # Clears the module-level undefined warning


# ---------------------------------------------------------
# STEP 2: GAMEPLAY LOGIC
# ---------------------------------------------------------
def load_question():
    global current_question_index, current_shuffled_options, current_correct_answer_text

    # SAFETY CHECK: Keeps IDE linter quiet and stops premature widget execution
    if subject_label is None or question_label is None or answer_label is None:
        return

    if current_question_index < len(QUESTIONS_POOL):
        q_data = QUESTIONS_POOL[current_question_index]

        # --- TYPE SAFETY CHECK ---
        if isinstance(q_data, list):
            if len(q_data) > 0:
                q_data = q_data[0]
            else:
                current_question_index += 1
                load_question()
                return

        if not isinstance(q_data, dict) or "options" not in q_data or "answer" not in q_data:
            current_question_index += 1
            load_question()
            return
        # -----------------------------

        raw_options = []
        for opt in q_data["options"]:
            clean_opt = str(opt)
            if len(clean_opt) > 2 and (clean_opt[1] in [")", "."] or clean_opt[2] in [")", "."]):
                clean_opt = clean_opt.split(")", 1)[-1].split(".", 1)[-1]
            raw_options.append(clean_opt.strip())

        answer_raw = str(q_data["answer"])
        if len(answer_raw) > 2 and (answer_raw[1] in [")", "."] or answer_raw[2] in [")", "."]):
            answer_raw = answer_raw.split(")", 1)[-1].split(".", 1)[-1]
        correct_clean_text = answer_raw.strip()

        random.shuffle(raw_options)

        letters = ["A)", "B)", "C)", "D)"]
        current_shuffled_options = [f"{letters[idx]}  {raw_options[idx]}" for idx in range(len(raw_options))]

        try:
            correct_index = raw_options.index(correct_clean_text)
        except ValueError:
            correct_index = 0
            for idx, ropt in enumerate(raw_options):
                if correct_clean_text in ropt or ropt in correct_clean_text:
                    correct_index = idx
                    break

        current_correct_answer_text = current_shuffled_options[correct_index]

        subject_label.config(text=f"SUBJECT: {q_data.get('subject', 'GENERAL')}")
        question_label.config(text=f"Question {current_question_index + 1}:\n{q_data.get('question', '')}")

        for idx, text in enumerate(current_shuffled_options):
            if idx < len(option_labels):
                option_labels[idx].config(text=text)

        answer_label.config(text="")
    else:
        max_score = max(scores.values()) if scores else 0
        winners = [team for team, score in scores.items() if score == max_score]

        if len(winners) == 1:
            winner_text = f"The winner is Team {winners[0]} with {max_score} points!"
        elif len(winners) > 1:
            winner_text = f"It's a tie between: {', '.join(winners)} with {max_score} points!"
        else:
            winner_text = "No scores recorded."

        messagebox.showinfo("Game Over!", f"🏆 Quiz Finished!\n\n{winner_text}")
        root_game.quit()


def reveal_answer():
    if current_question_index < len(QUESTIONS_POOL):
        answer_label.config(text=f"🎯 Correct Answer: {current_correct_answer_text}")


def award_points(team):
    global current_question_index
    scores[team] += 1
    score_labels[team].config(text=f"{team}: {scores[team]}")

    current_question_index += 1
    load_question()


def skip_question():
    global current_question_index
    current_question_index += 1
    load_question()


# ---------------------------------------------------------
# STEP 3: MAIN GAME WINDOW LAUNCHER
# ---------------------------------------------------------
def launch_game():
    global subject_label, question_label, answer_label, host_frame, score_labels, option_labels, root_game

    setup_root.withdraw()

    root_game = tk.Toplevel()
    root_game.title("STEAM Quiz Show Dashboard (Middle School Edition)")
    root_game.geometry("950x720")
    root_game.configure(bg="#2c3e50")

    root_game.protocol("WM_DELETE_WINDOW", exit)

    # Subject Banner Area
    subject_label = tk.Label(root_game, text="", font=("Arial", 16, "bold"), fg="#3498db", bg="#2c3e50")
    subject_label.pack(pady=(15, 0))

    # STABLE, LOCKED-SIZE QUESTION DISPLAY BOX
    question_frame = tk.Frame(root_game, bg="#34495e", bd=2, relief="groove")
    question_frame.pack(pady=15, padx=20)

    question_label = tk.Label(
        question_frame,
        text="",
        font=("Arial", 18, "bold"),
        fg="white",
        bg="#34495e",
        wraplength=750,
        width=65,
        height=4,
        justify="center"
    )
    question_label.pack(pady=15, padx=15)

    # High-Visibility Vertical Options Grid Frame
    options_frame = tk.Frame(root_game, bg="#2c3e50")
    options_frame.pack(pady=10, fill="x", padx=40)

    option_labels = []
    grid_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

    for row, col in grid_positions:
        lbl = tk.Label(
            options_frame,
            text="",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#1e272e",
            padx=20,
            pady=15,
            bd=1,
            relief="solid",
            anchor="w",
            justify="left"
        )
        lbl.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(col, weight=1)
        option_labels.append(lbl)

    # Reveal Answer Section
    answer_frame = tk.Frame(root_game, bg="#2c3e50")
    answer_frame.pack(pady=10)

    # Reveal Button Using Solid Label Strategy for macOS compatibility
    reveal_button = tk.Label(
        answer_frame,
        text="👀 REVEAL CORRECT ANSWER",
        font=("Arial", 12, "bold"),
        bg="#f1c40f",
        fg="black",
        padx=15,
        pady=8,
        bd=1,
        relief="raised",
        cursor="hand2"
    )
    reveal_button.pack(pady=5)
    reveal_button.bind("<Button-1>", lambda e: reveal_answer())

    answer_label = tk.Label(answer_frame, text="", font=("Arial", 16, "bold"), fg="#2ecc71", bg="#2c3e50")
    answer_label.pack()

    # Host Control Frame
    host_frame = tk.LabelFrame(root_game, text=" HOST PANEL: CLICK WHO BUZZED IN FIRST ", font=("Arial", 10, "bold"),
                               fg="#ecf0f1", bg="#2c3e50", padx=10, pady=10)
    host_frame.pack(pady=15, fill="x", padx=20)

    # Leaderboard Frame (Bottom)
    leaderboard_frame = tk.LabelFrame(root_game, text=" CURRENT SCORES (1 POINT PER CORRECT ANSWER) ",
                                      font=("Arial", 10, "bold"), fg="#ecf0f1", bg="#2c3e50", padx=10, pady=10)
    leaderboard_frame.pack(pady=15, fill="x", padx=20)

    score_labels = {}
    for team in TEAMS:
        lbl = tk.Label(leaderboard_frame, text=f"{team}: 0", font=("Arial", 14, "bold"), fg=TEAM_COLORS[team],
                       bg="#2c3e50")
        lbl.pack(side="left", expand=True)
        score_labels[team] = lbl

    # Generate Host Buzz-In Action Buttons (Using Solid Label Strategy for absolute color flooding)
    for team in TEAMS:
        team_color_hex = TEAM_COLORS[team]
        btn_mock = tk.Label(
            host_frame,
            text=f"🚨 {team}",
            font=("Arial", 11, "bold"),
            bg=team_color_hex,
            fg="white" if team != "Team Yellow" else "black",
            padx=12,
            pady=8,
            bd=2,
            relief="raised",
            cursor="hand2"
        )
        btn_mock.pack(side="left", expand=True, padx=6, pady=5, fill="x")
        btn_mock.bind("<Button-1>", lambda e, t=team: award_points(t))

    # Skip Button Mock
    skip_btn_mock = tk.Label(
        host_frame,
        text="❌ Skip Q",
        font=("Arial", 11, "bold"),
        bg="#95a5a6",
        fg="black",
        padx=12,
        pady=8,
        bd=2,
        relief="raised",
        cursor="hand2"
    )
    skip_btn_mock.pack(side="left", expand=True, padx=6, pady=5, fill="x")
    skip_btn_mock.bind("<Button-1>", lambda e: skip_question())

    # Initialize First Question Safely Now That Widgets Exist
    load_question()


# ---------------------------------------------------------
# STEP 4: SETUP WINDOW (DETERMINING TEAMS & COLORS)
# ---------------------------------------------------------
def process_setup():
    global TEAM_COLORS, TEAMS, scores
    num_teams = int(team_count_var.get())

    selected_colors = []
    temp_teams_dict = {}

    for idx in range(num_teams):
        chosen_color = dropdowns[idx].get().strip()

        if not chosen_color:
            messagebox.showerror("Missing Selection", f"Please select a valid color for Team {idx + 1}!")
            return

        if chosen_color in selected_colors:
            messagebox.showerror("Duplicate Colors", "Each team must have a unique color!")
            return

        selected_colors.append(chosen_color)
        team_name = f"Team {chosen_color}"
        temp_teams_dict[team_name] = COLOR_LIBRARY[chosen_color]

    TEAM_COLORS = temp_teams_dict
    TEAMS = list(TEAM_COLORS.keys())
    scores = {team: 0 for team in TEAMS}

    launch_game()


def update_setup_rows(*_):
    # Fixed: Changed *args to *_ to explicitly handle unused variable trace inputs
    num_teams = int(team_count_var.get())
    for idx in range(6):
        if idx < num_teams:
            rows_frames[idx].pack(pady=5, fill="x")
            if not dropdowns[idx].get():
                dropdowns[idx].set(default_selections[idx])
        else:
            rows_frames[idx].pack_forget()


# Create Setup GUI
setup_root = tk.Tk()
setup_root.title("Quiz Show Startup Config")
setup_root.geometry("450x450")
setup_root.configure(bg="#2c3e50")

title_lbl = tk.Label(setup_root, text="GAME SHOW SETUP", font=("Arial", 16, "bold"), fg="#f1c40f", bg="#2c3e50")
title_lbl.pack(pady=15)

count_frame = tk.Frame(setup_root, bg="#2c3e50")
count_frame.pack(pady=10)

count_lbl = tk.Label(count_frame, text="How many teams? (2-6): ", font=("Arial", 11, "bold"), fg="white", bg="#2c3e50")
count_lbl.pack(side="left", padx=5)

team_count_var = tk.StringVar(value="3")
team_count_var.trace_add("write", update_setup_rows)

count_dropdown = ttk.Combobox(count_frame, textvariable=team_count_var, values=[str(x) for x in range(2, 7)],
                              state="readonly", width=5)
count_dropdown.pack(side="left")

colors_container = tk.LabelFrame(setup_root, text=" Assign Colors ", font=("Arial", 10, "bold"), fg="#bdc3c7",
                                 bg="#2c3e50", padx=10, pady=10)
colors_container.pack(pady=15, fill="both", expand=True, padx=20)

dropdowns = []
rows_frames = []
default_selections = list(COLOR_LIBRARY.keys())

# Fixed: Using slot_idx isolates variable scope from function contexts
for slot_idx in range(6):
    row_frame = tk.Frame(colors_container, bg="#2c3e50")
    row_frame.pack(pady=5, fill="x")
    rows_frames.append(row_frame)

    # Fixed: Using unique name setup_lbl resolves outer scope collision
    setup_lbl = tk.Label(row_frame, text=f"Team {slot_idx + 1}:", font=("Arial", 11, "bold"), fg="white", bg="#2c3e50",
                         width=8,
                         anchor="w")
    setup_lbl.pack(side="left", padx=5)

    color_var = tk.StringVar(value=default_selections[slot_idx])
    dd = ttk.Combobox(colors_container, textvariable=color_var, values=list(COLOR_LIBRARY.keys()), state="readonly")
    dd.pack(side="left", fill="x", expand=True, padx=5)

    dd.pack_forget()
    dd.pack(in_=row_frame, side="left", fill="x", expand=True, padx=5)

    dropdowns.append(dd)

update_setup_rows()

# Setup Start Action Trigger via Click Label
start_btn = tk.Label(
    setup_root,
    text="🚀 START GAME",
    font=("Arial", 12, "bold"),
    bg="#2ecc71",
    fg="white",
    pady=10,
    bd=2,
    relief="raised",
    cursor="hand2"
)
start_btn.pack(pady=20, fill="x", padx=20)
start_btn.bind("<Button-1>", lambda e: process_setup())

setup_root.mainloop()