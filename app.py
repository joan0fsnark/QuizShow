import os
import json
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- CONSTANTS & COLOR LIBRARY ---
COLOR_LIBRARY = {
    "Red": "#e74c3c",
    "Orange": "#e67e22",
    "Yellow": "#f1c40f",
    "Green": "#2ecc71",
    "Blue": "#3498db",
    "Purple": "#9b59b6"
}

BG_DARK = "#2c3e50"
CARD_BG = "#34495e"
OPTION_BG = "#1e272e"
TEXT_LIGHT = "#ecf0f1"
ACCENT_GREEN = "#2ecc71"
ACCENT_YELLOW = "#f1c40f"
ACCENT_BLUE = "#3498db"
ACCENT_PURPLE = "#9b59b6"
ACCENT_ORANGE = "#e67e22"


class STEAMQuizShowApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("STEAM Quiz Show Dashboard")
        self.geometry("950x780")
        self.configure(bg=BG_DARK)

        # --- GAME STATE ---
        self.current_filename = "None Loaded"
        self.questions = []
        self.current_idx = 0
        self.scores = {}
        self.team_colors = {}
        self.shuffled_options = []
        self.question_revealed = False
        self.game_history = []  # State history for undo operations

        # --- MAIN CONTAINER ---
        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        # Attempt to load default file if present
        default_file = "q-animals.json"
        if os.path.exists(default_file):
            self.load_questions_from_file(os.path.abspath(default_file))

        self.show_setup_screen()

    # ---------------------------------------------------------
    # DATA LOADING & FILE SELECTION LOGIC
    # ---------------------------------------------------------
    def load_questions_from_file(self, filepath):
        """Reads, cleans, and standardizes question data from any JSON dataset."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

            cleaned_data = []

            # Handle top-level wrappers like {"questions": [...]}
            if isinstance(data, dict):
                for key in ["questions", "data", "items"]:
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break

            if not isinstance(data, list):
                messagebox.showerror("Error", "JSON file root must be a list of question objects.")
                return False

            for item in data:
                if isinstance(item, list) and len(item) > 0:
                    item = item[0]

                if not isinstance(item, dict):
                    continue

                q_text = item.get("question")
                opts = item.get("options")
                ans = item.get("answer")

                if q_text and opts and ans and isinstance(opts, list):
                    cleaned_data.append({
                        "question": str(q_text),
                        "options": list(opts),
                        "answer": str(ans),
                        "subject": item.get("subject", "GENERAL"),
                        "info": item.get("info", "")
                    })

            if not cleaned_data:
                messagebox.showwarning("Warning", f"No valid questions found in:\n{os.path.basename(filepath)}")
                return False

            random.shuffle(cleaned_data)
            self.questions = cleaned_data
            self.current_filename = os.path.basename(filepath)
            self.current_idx = 0
            return True

        except Exception as e:
            messagebox.showerror("File Error", f"Could not read JSON file:\n{e}")
            return False

    def select_file_action(self):
        """Launches the system file selection dialog."""
        selected_path = filedialog.askopenfilename(
            title="Choose a Question JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if selected_path:
            if self.load_questions_from_file(selected_path):
                messagebox.showinfo("Success", f"Loaded {len(self.questions)} questions from:\n{self.current_filename}")
                self.show_setup_screen()

    def clear_container(self):
        """Clears container widgets prior to screen rendering."""
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------------------------------------------------------
    # SCREEN 1: GAME SETUP
    # ---------------------------------------------------------
    def show_setup_screen(self):
        self.clear_container()

        tk.Label(
            self.container, text="GAME SHOW SETUP", font=("Arial", 22, "bold"),
            bg=BG_DARK, fg=ACCENT_YELLOW
        ).pack(side="top", fill="x", pady=(0, 15))

        # --- STEP 1: JSON FILE SELECTOR TOOLBAR ---
        file_frame = tk.LabelFrame(
            self.container, text=" STEP 1: SELECT QUESTION FILE ", font=("Arial", 10, "bold"),
            bg=CARD_BG, fg=ACCENT_YELLOW, bd=2, relief="groove", padx=15, pady=15
        )
        file_frame.pack(side="top", fill="x", pady=(0, 15))

        # Vibrant Blue File Selection Button
        load_btn = tk.Label(
            file_frame,
            text="📂 LOAD NEW QUESTION FILE",
            font=("Arial", 11, "bold"),
            bg=ACCENT_BLUE,
            fg="white",
            bd=2,
            relief="raised",
            cursor="hand2",
            padx=15,
            pady=8
        )
        load_btn.pack(side="left", padx=(0, 15))
        load_btn.bind("<Button-1>", lambda e: self.select_file_action())
        load_btn.bind("<Enter>", lambda e: load_btn.config(bg="#2980b9"))
        load_btn.bind("<Leave>", lambda e: load_btn.config(bg=ACCENT_BLUE))

        status_msg = (
            f"Active Dataset: {self.current_filename}\nQuestions Ready: {len(self.questions)}"
            if self.questions else "No question file loaded. Please click 'LOAD NEW QUESTION FILE'."
        )
        status_color = ACCENT_GREEN if self.questions else "#e74c3c"

        tk.Label(
            file_frame, text=status_msg, font=("Arial", 10, "bold"),
            bg=CARD_BG, fg=status_color, justify="left", anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # --- STEP 2: TEAM SETUP ---
        team_frame = tk.LabelFrame(
            self.container, text=" STEP 2: CONFIGURE TEAMS ", font=("Arial", 10, "bold"),
            bg=CARD_BG, fg=ACCENT_YELLOW, bd=2, relief="groove", padx=15, pady=15
        )
        team_frame.pack(side="top", fill="x", pady=(0, 15))

        spin_row = tk.Frame(team_frame, bg=CARD_BG)
        spin_row.pack(anchor="w", pady=(0, 10))

        tk.Label(
            spin_row, text="How many teams? (2-6):", font=("Arial", 11, "bold"),
            bg=CARD_BG, fg=TEXT_LIGHT
        ).pack(side="left", padx=(0, 10))

        self.num_teams_var = tk.IntVar(value=3)
        num_teams_spin = tk.Spinbox(
            spin_row, from_=2, to=6, textvariable=self.num_teams_var,
            font=("Arial", 11), width=5, command=self.render_team_color_selectors
        )
        num_teams_spin.pack(side="left")

        self.colors_frame = tk.Frame(team_frame, bg=CARD_BG)
        self.colors_frame.pack(fill="x")

        self.team_color_vars = []
        self.render_team_color_selectors()

        # Vibrant Green Start Game Button
        start_btn = tk.Label(
            self.container, text="🚀 START GAME", font=("Arial", 14, "bold"),
            bg=ACCENT_GREEN, fg="black", bd=2, relief="raised", cursor="hand2", pady=12
        )
        start_btn.pack(side="bottom", fill="x", pady=10)
        start_btn.bind("<Button-1>", lambda e: self.start_game())
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#27ae60"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=ACCENT_GREEN))

    def render_team_color_selectors(self):
        """Renders color selection dropdowns for each team."""
        for widget in self.colors_frame.winfo_children():
            widget.destroy()

        self.team_color_vars = []
        num_teams = self.num_teams_var.get()
        color_options = list(COLOR_LIBRARY.keys())

        for i in range(num_teams):
            row = tk.Frame(self.colors_frame, bg=CARD_BG)
            row.pack(fill="x", pady=3)

            tk.Label(
                row, text=f"Team {i + 1} Color:", font=("Arial", 10, "bold"),
                bg=CARD_BG, fg=TEXT_LIGHT, width=15, anchor="w"
            ).pack(side="left")

            default_color = color_options[i % len(color_options)]
            var = tk.StringVar(value=default_color)
            self.team_color_vars.append(var)

            dropdown = ttk.Combobox(
                row, textvariable=var, values=color_options, state="readonly", width=12
            )
            dropdown.pack(side="left", padx=10)

    def start_game(self):
        if not self.questions:
            messagebox.showwarning("No Questions", "Please load a question file before starting!")
            return

        selected_colors = [var.get() for var in self.team_color_vars]
        if len(set(selected_colors)) < len(selected_colors):
            messagebox.showerror("Duplicate Colors", "Each team must have a unique color!")
            return

        self.scores = {f"Team {color}": 0 for color in selected_colors}
        self.team_colors = {f"Team {color}": COLOR_LIBRARY[color] for color in selected_colors}
        self.game_history = []
        self.current_idx = 0

        self.build_game_ui()
        self.prepare_next_turn()

    # ---------------------------------------------------------
    # MAIN GAME UI LAYOUT & TURN MANAGEMENT
    # ---------------------------------------------------------
    def build_game_ui(self):
        self.clear_container()

        # Subject Header Frame
        self.meta_frame = tk.Frame(self.container, bg=BG_DARK)
        self.meta_frame.pack(fill="x", pady=(0, 10))

        self.subject_label = tk.Label(
            self.meta_frame, text="SUBJECT: INITIALIZING", font=("Arial", 13, "bold"),
            bg=BG_DARK, fg="#3498db"
        )
        self.subject_label.pack()

        # Question Card Display Area
        self.q_frame = tk.Frame(self.container, bg=CARD_BG, bd=2, relief="solid", highlightbackground="#415b76")
        self.q_frame.pack(fill="both", expand=True, pady=5)

        self.q_text = tk.Label(
            self.q_frame, text="", font=("Arial", 22, "bold"), bg=CARD_BG, fg=TEXT_LIGHT,
            wraplength=850, justify="center"
        )
        self.q_text.pack(expand=True, fill="both", padx=20, pady=20)

        # Options Grid
        self.opts_frame = tk.Frame(self.container, bg=BG_DARK)
        self.opts_frame.pack(fill="x", pady=10)
        self.opts_frame.grid_columnconfigure((0, 1), weight=1)

        self.opt_labels = []
        for r in range(2):
            for c in range(2):
                lbl = tk.Label(
                    self.opts_frame, text="", font=("Arial", 12, "bold"), bg=OPTION_BG, fg=TEXT_LIGHT,
                    bd=1, relief="solid", padx=15, pady=10, anchor="w", wraplength=380, justify="left"
                )
                lbl.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
                self.opt_labels.append(lbl)

        # Vibrant Yellow "Reveal Correct Answer" Button
        self.reveal_btn = tk.Label(
            self.container, text="💡 REVEAL CORRECT ANSWER", font=("Arial", 11, "bold"),
            bg=ACCENT_YELLOW, fg="black", cursor="hand2", padx=20, pady=8, bd=2, relief="raised"
        )
        self.reveal_btn.pack(fill="x", pady=5)
        self.reveal_btn.bind("<Button-1>", lambda e: self.reveal_answer())

        self.ans_label = tk.Label(self.container, text="", font=("Arial", 13, "bold"), bg=BG_DARK, fg=ACCENT_GREEN)
        self.ans_label.pack(pady=2)

        # Host Control Panel Frame
        self.host_frame = tk.Frame(self.container, bg=BG_DARK)
        self.host_frame.pack(fill="x", pady=5)

        self.sep_lbl = tk.Label(
            self.host_frame, text="HOST PANEL", font=("Arial", 10, "bold"),
            bg=BG_DARK, fg="#bdc3c7"
        )
        self.sep_lbl.pack(anchor="w", pady=(0, 5))

        self.btn_container = tk.Frame(self.host_frame, bg=BG_DARK)
        self.btn_container.pack(fill="x")

        # Leaderboard Scoreboard Frame
        self.score_frame = tk.Frame(self.container, bg=BG_DARK)
        self.score_frame.pack(fill="x", pady=(5, 0))

        score_title = tk.Label(
            self.score_frame, text="CURRENT SCOREBOARD & ADJUSTMENTS", font=("Arial", 10, "bold"),
            bg=BG_DARK, fg="#bdc3c7"
        )
        score_title.pack(anchor="w", pady=(0, 5))

        self.score_bars = tk.Frame(self.score_frame, bg=BG_DARK)
        self.score_bars.pack(fill="x")

    def save_state_to_history(self):
        """Saves a clean state snapshot before making score or question changes."""
        snapshot = {
            "current_idx": self.current_idx,
            "scores": self.scores.copy(),
            "question_revealed": self.question_revealed,
            "shuffled_options": self.shuffled_options.copy()
        }
        self.game_history.append(snapshot)

    def prepare_next_turn(self):
        """Intermission/Pause Screen between questions."""
        self.question_revealed = False
        self.ans_label.config(text="")

        if self.current_idx < len(self.questions):
            next_subject = self.questions[self.current_idx].get('subject', 'GENERAL').upper()
            self.subject_label.config(text=f"UPCOMING CATEGORY: {next_subject}")
            self.flash_category_header(0, True)
        else:
            self.subject_label.config(text="GAME STATUS: COMPLETING MATCH", fg="#3498db")

        if self.current_idx == 0:
            cinematic_text = (
                "WELCOME TO THE SHOW\n"
                "• • •\n"
                "Teams are locked and ready.\n"
                "Host, click 'NEXT QUESTION' to start Round 1!"
            )
        else:
            cinematic_text = (
                "ROUND OVER\n"
                "• • •\n"
                "Host is resetting buzzers.\n"
                "Eyes on the screen!"
            )

        self.q_text.config(text=cinematic_text, font=("Arial", 18, "bold"), fg="#95a5a6", wraplength=800)

        for lbl in self.opt_labels:
            lbl.config(text="", bg=BG_DARK, relief="flat")

        self.reveal_btn.config(bg=CARD_BG, fg="#7f8c8d", cursor="arrow")
        self.refresh_host_panel()
        self.refresh_score_display()

    def flash_category_header(self, count, color_state):
        """Flashes the subject header to draw attention to the upcoming topic."""
        if self.question_revealed:
            return
        if count < 8:
            color = ACCENT_YELLOW if color_state else BG_DARK
            self.subject_label.config(fg=color)
            self.after(500, lambda: self.flash_category_header(count + 1, not color_state))
        else:
            self.subject_label.config(fg=ACCENT_YELLOW)

    def display_current_question(self, from_undo=False):
        """Displays the active question card and shuffled choices."""
        if self.current_idx >= len(self.questions):
            self.trigger_game_over()
            return

        if not from_undo:
            self.save_state_to_history()

        current_q = self.questions[self.current_idx]
        self.question_revealed = True

        self.reveal_btn.config(bg=ACCENT_YELLOW, fg="black", cursor="hand2")
        self.subject_label.config(text=f"SUBJECT: {current_q.get('subject', 'GENERAL').upper()}", fg="#3498db")
        self.q_text.config(text=f"Question {self.current_idx + 1}:\n{current_q.get('question', '')}", font=("Arial", 18, "bold"), fg=TEXT_LIGHT)

        # Shuffle options dynamically
        if not from_undo:
            raw_opts = []
            for opt in current_q["options"]:
                clean_opt = str(opt).strip()
                if len(clean_opt) > 2 and (clean_opt[1] in [")", "."] or clean_opt[2] in [")", "."]):
                    clean_opt = clean_opt.split(")", 1)[-1].split(".", 1)[-1].strip()
                raw_opts.append(clean_opt)
            random.shuffle(raw_opts)

            alphabet = ["A)", "B)", "C)", "D)", "E)", "F)"]
            self.shuffled_options = [f"{alphabet[i]}  {raw_opts[i]}" for i in range(len(raw_opts))]

        for i, lbl in enumerate(self.opt_labels):
            if i < len(self.shuffled_options):
                lbl.config(text=self.shuffled_options[i], bg=OPTION_BG, relief="solid")
            else:
                lbl.config(text="", bg=BG_DARK, relief="flat")

        self.refresh_host_panel()

    def refresh_host_panel(self):
        """Renders host panel controls dynamically using custom-rendered colored Labels."""
        for widget in self.btn_container.winfo_children():
            widget.destroy()

        if not self.question_revealed:
            self.sep_lbl.config(text="HOST PANEL: ADVANCE WHEN READY")

            # Vibrant Green Next Question Button
            next_btn = tk.Label(
                self.btn_container, text="▶️ NEXT QUESTION", font=("Arial", 12, "bold"),
                bg=ACCENT_GREEN, fg="black", cursor="hand2", bd=2, relief="raised", pady=10
            )
            next_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
            next_btn.bind("<Button-1>", lambda e: self.display_current_question())
            next_btn.bind("<Enter>", lambda e: next_btn.config(bg="#27ae60"))
            next_btn.bind("<Leave>", lambda e: next_btn.config(bg=ACCENT_GREEN))

            # Vibrant Purple Undo Button
            undo_bg = ACCENT_PURPLE if self.game_history else OPTION_BG
            undo_fg = "white" if self.game_history else "#57606f"
            undo_cursor = "hand2" if self.game_history else "arrow"

            undo_btn = tk.Label(
                self.btn_container, text="⏪ UNDO", font=("Arial", 12, "bold"),
                bg=undo_bg, fg=undo_fg, cursor=undo_cursor, bd=2, relief="raised", pady=10
            )
            undo_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))
            if self.game_history:
                undo_btn.bind("<Button-1>", lambda e: self.trigger_undo_rewind())
                undo_btn.bind("<Enter>", lambda e: undo_btn.config(bg="#8e44ad"))
                undo_btn.bind("<Leave>", lambda e: undo_btn.config(bg=ACCENT_PURPLE))

        else:
            self.sep_lbl.config(text="HOST PANEL: CLICK WHO BUZZED IN FIRST")

            # Vibrant Team Colors for Buzzers
            for team, color_hex in self.team_colors.items():
                text_color = "#000000" if color_hex in ["#f1c40f", "#2ecc71"] else "#ffffff"

                btn = tk.Label(
                    self.btn_container,
                    text=f"🚨 {team}",
                    font=("Arial", 11, "bold"),
                    bg=color_hex,
                    fg=text_color,
                    bd=2,
                    relief="raised",
                    cursor="hand2",
                    pady=10
                )
                btn.pack(side="left", expand=True, fill="x", padx=3)
                btn.bind("<Button-1>", lambda e, t=team: self.award_points(t))

            # Vibrant Orange Skip Button
            skip_btn = tk.Label(
                self.btn_container, text="❌ Skip Q", font=("Arial", 11, "bold"),
                bg=ACCENT_ORANGE, fg="white", bd=2, relief="raised", cursor="hand2", pady=10
            )
            skip_btn.pack(side="left", expand=True, fill="x", padx=3)
            skip_btn.bind("<Button-1>", lambda e: self.skip_question())
            skip_btn.bind("<Enter>", lambda e: skip_btn.config(bg="#d35400"))
            skip_btn.bind("<Leave>", lambda e: skip_btn.config(bg=ACCENT_ORANGE))

            # Vibrant Purple Undo Button
            undo_btn = tk.Label(
                self.btn_container, text="⏪ Undo", font=("Arial", 11, "bold"),
                bg=ACCENT_PURPLE, fg="white", bd=2, relief="raised", cursor="hand2", pady=10
            )
            undo_btn.pack(side="left", expand=True, fill="x", padx=3)
            undo_btn.bind("<Button-1>", lambda e: self.trigger_undo_rewind())
            undo_btn.bind("<Enter>", lambda e: undo_btn.config(bg="#8e44ad"))
            undo_btn.bind("<Leave>", lambda e: undo_btn.config(bg=ACCENT_PURPLE))

    def award_points(self, team):
        self.save_state_to_history()
        self.scores[team] += 1
        self.current_idx += 1
        self.prepare_next_turn()

    def skip_question(self):
        self.save_state_to_history()
        self.current_idx += 1
        self.prepare_next_turn()

    def trigger_undo_rewind(self):
        """Restores the previous game state from the history stack."""
        if not self.game_history:
            return

        previous_state = self.game_history.pop()
        self.current_idx = previous_state["current_idx"]
        self.scores = previous_state["scores"]
        self.shuffled_options = previous_state["shuffled_options"]
        target_revelation = previous_state["question_revealed"]

        if target_revelation:
            self.display_current_question(from_undo=True)
        else:
            self.prepare_next_turn()

    def change_score_manually(self, team, amount):
        self.scores[team] = max(0, self.scores[team] + amount)
        self.refresh_score_display()

    def reveal_answer(self):
        if self.question_revealed and self.current_idx < len(self.questions):
            current_q = self.questions[self.current_idx]
            target_ans = current_q.get("answer", "")
            info_text = f"\nℹ️ {current_q['info']}" if current_q.get("info") else ""
            self.ans_label.config(text=f"🎯 Correct Answer: {target_ans}{info_text}")

    def refresh_score_display(self):
        """Renders live scoreboard cards with manual adjustment controls."""
        for widget in self.score_bars.winfo_children():
            widget.destroy()

        self.score_bars.grid_columnconfigure(list(range(len(self.scores))), weight=1)
        for i, (team, score) in enumerate(self.scores.items()):
            team_color = self.team_colors[team]

            card_container = tk.Frame(self.score_bars, bg=BG_DARK)
            card_container.grid(row=0, column=i, padx=6, sticky="ew")
            card_container.grid_columnconfigure((0, 1), weight=1)

            card_border = tk.Frame(card_container, bg=team_color, bd=2, relief="solid")
            card_border.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

            card = tk.Label(
                card_border, text=f"{team}\n{score} pts", font=("Arial", 11, "bold"),
                bg=CARD_BG, fg=team_color, pady=6
            )
            card.pack(fill="both", expand=True)

            minus_btn = tk.Label(
                card_container, text="−", font=("Arial", 9, "bold"), bg=CARD_BG, fg="#95a5a6",
                cursor="hand2", bd=1, relief="flat", width=4
            )
            minus_btn.grid(row=1, column=0, padx=(0, 2), sticky="e")
            minus_btn.bind("<Button-1>", lambda e, t=team: self.change_score_manually(t, -1))
            minus_btn.bind("<Enter>", lambda e, w=minus_btn: w.config(bg="#e74c3c", fg="white"))
            minus_btn.bind("<Leave>", lambda e, w=minus_btn: w.config(bg=CARD_BG, fg="#95a5a6"))

            plus_btn = tk.Label(
                card_container, text="+", font=("Arial", 9, "bold"), bg=CARD_BG, fg="#95a5a6",
                cursor="hand2", bd=1, relief="flat", width=4
            )
            plus_btn.grid(row=1, column=1, padx=(2, 0), sticky="w")
            plus_btn.bind("<Button-1>", lambda e, t=team: self.change_score_manually(t, 1))
            plus_btn.bind("<Enter>", lambda e, w=plus_btn: w.config(bg=ACCENT_GREEN, fg="black"))
            plus_btn.bind("<Leave>", lambda e, w=plus_btn: w.config(bg=CARD_BG, fg="#95a5a6"))

    # ---------------------------------------------------------
    # SCREEN 3: GAME OVER
    # ---------------------------------------------------------
    def trigger_game_over(self):
        self.clear_container()

        tk.Label(
            self.container, text="🏁 GAME OVER!", font=("Arial", 28, "bold"),
            bg=BG_DARK, fg=ACCENT_YELLOW
        ).pack(pady=20)

        max_score = max(self.scores.values()) if self.scores else 0
        winners = [t for t, s in self.scores.items() if s == max_score]

        if len(winners) == 1:
            win_text = f"🏆 Champion: {winners[0]}\nScore: {max_score} points"
            lbl_color = self.team_colors[winners[0]]
        else:
            win_text = f"🤝 Tied Match Between:\n{', '.join(winners)}\nScore: {max_score} points"
            lbl_color = TEXT_LIGHT

        tk.Label(
            self.container, text=win_text, font=("Arial", 18, "bold"),
            bg=BG_DARK, fg=lbl_color, justify="center"
        ).pack(pady=15)

        restart_btn = tk.Label(
            self.container, text="🔄 Restart Application", font=("Arial", 12, "bold"),
            bg=ACCENT_BLUE, fg="white", cursor="hand2", pady=10, padx=20, bd=2, relief="raised"
        )
        restart_btn.pack(pady=20)
        restart_btn.bind("<Button-1>", lambda e: self.show_setup_screen())


if __name__ == "__main__":
    app = STEAMQuizShowApp()
    app.mainloop()