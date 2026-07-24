import tkinter as tk
from tkinter import ttk, messagebox
import json
import random


class QuizShowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STEAM Quiz Show Dashboard")
        self.root.geometry("1024x755")
        self.root.configure(bg="#2c3e50")

        # UI Styling Colors
        self.bg_dark = "#2c3e50"
        self.box_bg = "#34495e"
        self.text_light = "#ecf0f1"

        self.COLOR_LIBRARY = {
            "Red": "#e74c3c", "Orange": "#e67e22", "Yellow": "#f1c40f",
            "Green": "#2ecc71", "Blue": "#3498db", "Purple": "#9b59b6"
        }

        # State Variables
        self.questions = []
        self.current_idx = 0
        self.scores = {}
        self.team_colors = {}
        self.shuffled_options = []
        self.question_revealed = False

        # --- NEW STATE VARIABLE FOR HISTORY TRACKING ---
        self.game_history = []

        self.load_questions()
        self.show_setup_screen()

    def load_questions(self):
        try:
            with open("q-general.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.questions = []

                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, list):
                            for sub_item in item:
                                if isinstance(sub_item, dict) and "question" in sub_item:
                                    self.questions.append(sub_item)
                        elif isinstance(item, dict) and "question" in item:
                            self.questions.append(item)

                random.shuffle(self.questions)
                print(f"🎉 Successfully loaded {len(self.questions)} questions total.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not load q-general.json:\n{e}")
            self.root.destroy()

    def show_setup_screen(self):
        self.setup_win = tk.Toplevel(self.root)
        self.setup_win.title("Game Show Setup")
        self.setup_win.geometry("450x500")
        self.setup_win.configure(bg=self.bg_dark)
        self.setup_win.grab_set()

        tk.Label(self.setup_win, text="GAME SHOW SETUP", font=("Arial", 18, "bold"), bg=self.bg_dark,
                 fg="#f1c40f").pack(pady=15)

        frame = tk.Frame(self.setup_win, bg=self.bg_dark)
        frame.pack(pady=10)

        tk.Label(frame, text="How many teams? (2-6):", font=("Arial", 12), bg=self.bg_dark, fg=self.text_light).grid(
            row=0, column=0, padx=10, pady=10)
        self.team_count_var = tk.StringVar(value="3")
        team_combo = ttk.Combobox(frame, textvariable=self.team_count_var, values=["2", "3", "4", "5", "6"], width=5,
                                  state="readonly")
        team_combo.grid(row=0, column=1, padx=10, pady=10)
        team_combo.bind("<<ComboboxSelected>>", self.update_setup_rows)

        self.rows_frame = tk.Frame(self.setup_win, bg=self.bg_dark)
        self.rows_frame.pack(pady=10, fill="x", padx=40)

        self.update_setup_rows()

    def update_setup_rows(self, event=None):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        count = int(self.team_count_var.get())
        color_options = list(self.COLOR_LIBRARY.keys())
        self.setup_combos = []

        for i in range(count):
            row_f = tk.Frame(self.rows_frame, bg=self.bg_dark)
            row_f.pack(fill="x", pady=4)

            tk.Label(row_f, text=f"Team {i + 1}:", font=("Arial", 11, "bold"), bg=self.bg_dark, fg=self.text_light,
                     width=8, anchor="w").pack(side="left")

            combo = ttk.Combobox(row_f, values=color_options, state="readonly", width=15)
            combo.set(color_options[i % len(color_options)])
            combo.pack(side="left", padx=10)
            self.setup_combos.append(combo)

        start_btn = tk.Label(self.setup_win, text="🚀 START GAME", font=("Arial", 14, "bold"), bg="#2ecc71", fg="black",
                             cursor="hand2", bd=0, padx=20, pady=10)
        start_btn.pack(side="bottom", fill="x", pady=20, padx=40)
        start_btn.bind("<Button-1>", lambda e: self.finalize_setup())

    def finalize_setup(self):
        selected_colors = [c.get() for c in self.setup_combos]
        if len(set(selected_colors)) < len(selected_colors):
            messagebox.showwarning("Duplicate Colors", "Each team must be assigned a unique color configuration!")
            return

        for i, color_name in enumerate(selected_colors):
            team_label = f"Team {color_name}"
            self.scores[team_label] = 0
            self.team_colors[team_label] = self.COLOR_LIBRARY[color_name]

        self.setup_win.destroy()
        self.build_main_ui()
        self.prepare_next_turn()

    def build_main_ui(self):
        # Top Metadata Banner
        self.meta_frame = tk.Frame(self.root, bg=self.bg_dark)
        self.meta_frame.pack(fill="x", pady=(15, 5))
        self.subject_label = tk.Label(self.meta_frame, text="SUBJECT: INITIALIZING", font=("Arial", 13, "bold"),
                                      bg=self.bg_dark, fg="#3498db")
        self.subject_label.pack()

        # Center Structural Question Frame
        self.q_frame = tk.Frame(self.root, bg=self.box_bg, bd=2, relief="solid", highlightbackground="#415b76")
        self.q_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.q_frame.pack_propagate(False)

        self.q_text = tk.Label(self.q_frame, text="", font=("Arial", 22, "bold"), bg=self.box_bg, fg=self.text_light,
                               wraplength=850, justify="center")
        self.q_text.place(relx=0.5, rely=0.5, anchor="center")

        # Multi-choice Subgrid Frame
        self.opts_frame = tk.Frame(self.root, bg=self.bg_dark)
        self.opts_frame.pack(fill="x", padx=40, pady=10)
        self.opts_frame.grid_columnconfigure((0, 1), weight=1)

        self.opt_labels = []
        for r in range(2):
            for c in range(2):
                lbl = tk.Label(self.opts_frame, text="", font=("Arial", 15, "bold"), bg="#1e272e", fg=self.text_light,
                               bd=1, relief="solid", padx=20, pady=15, anchor="w")
                lbl.grid(row=r, column=c, padx=10, pady=8, sticky="ew")
                self.opt_labels.append(lbl)

        # Reveal Answer Mac-Safe Label
        self.reveal_btn = tk.Label(self.root, text="👀 REVEAL CORRECT ANSWER", font=("Arial", 12, "bold"), bg="#f1c40f",
                                   fg="black", cursor="hand2", padx=20, pady=8, bd=1, relief="raised")
        self.reveal_btn.pack(fill="x", padx=50, pady=5)
        self.reveal_btn.bind("<Button-1>", lambda e: self.reveal_answer())

        self.ans_label = tk.Label(self.root, text="", font=("Arial", 15, "bold"), bg=self.bg_dark, fg="#2ecc71")
        self.ans_label.pack(pady=5)

        # Host Control Panel Frame Footer
        self.host_frame = tk.Frame(self.root, bg=self.bg_dark)
        self.host_frame.pack(fill="x", padx=40, pady=5)

        self.sep_lbl = tk.Label(self.host_frame, text="HOST PANEL", font=("Arial", 10, "bold"), bg=self.bg_dark,
                                fg="#bdc3c7")
        self.sep_lbl.pack(anchor="w", pady=(0, 5))

        self.btn_container = tk.Frame(self.host_frame, bg=self.bg_dark)
        self.btn_container.pack(fill="x")

        # Live Score Leaderboard Layout
        self.score_frame = tk.Frame(self.root, bg=self.bg_dark)
        self.score_frame.pack(fill="x", padx=40, pady=(5, 20))

        score_title = tk.Label(self.score_frame, text="CURRENT SCOREBOARD & ADJUSTMENTS", font=("Arial", 10, "bold"),
                               bg=self.bg_dark, fg="#bdc3c7")
        score_title.pack(anchor="w", pady=(0, 5))

        self.score_bars = tk.Frame(self.score_frame, bg=self.bg_dark)
        self.score_bars.pack(fill="x")

    def save_state_to_history(self):
        """Saves a clean deep copy of current scores and status before any changes occur."""
        snapshot = {
            "current_idx": self.current_idx,
            "scores": self.scores.copy(),
            "question_revealed": self.question_revealed,
            "shuffled_options": self.shuffled_options.copy()
        }
        self.game_history.append(snapshot)

    def prepare_next_turn(self):
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
                "Host, advance to kick off Round 1!"
            )
        else:
            cinematic_text = (
                "ROUND OVER\n"
                "• • •\n"
                "Host is resetting buzzers.\n"
                "Eyes on the screen!"
            )

        self.q_text.config(text=cinematic_text, font=("Helvetica Neue", 20, "bold"), fg="#95a5a6", wraplength=800)

        for lbl in self.opt_labels:
            lbl.config(text="", bg="#2c3e50", relief="flat")

        self.reveal_btn.config(bg="#34495e", fg="#7f8c8d", cursor="arrow")
        self.refresh_host_panel()
        self.refresh_score_display()

    def flash_category_header(self, count, color_state):
        if self.question_revealed:
            return
        if count < 8:
            if color_state:
                self.subject_label.config(fg="#f1c40f")
            else:
                self.subject_label.config(fg="#2c3e50")
            self.root.after(500, lambda: self.flash_category_header(count + 1, not color_state))
        else:
            self.subject_label.config(fg="#f1c40f")

    def display_current_question(self, from_undo=False):
        if self.current_idx >= len(self.questions):
            self.trigger_game_over()
            return

        # Only log history if expanding forward, not rewinding back into it
        if not from_undo:
            self.save_state_to_history()

        current_q = self.questions[self.current_idx]
        self.question_revealed = True

        self.reveal_btn.config(bg="#f1c40f", fg="black", cursor="hand2")
        self.subject_label.config(text=f"SUBJECT: {current_q.get('subject', 'GENERAL').upper()}", fg="#3498db")
        self.q_text.config(text=current_q.get("question", ""), font=("Arial", 22, "bold"), fg=self.text_light)

        # If we didn't just rebuild this card from an undo state, generate a fresh option shuffle
        if not from_undo:
            raw_opts = []
            for opt in current_q["options"]:
                clean_opt = str(opt).strip()
                if len(clean_opt) > 2 and (clean_opt[1] in [")", "."] or clean_opt[2] in [")", "."]):
                    clean_opt = clean_opt.split(")", 1)[-1].split(".", 1)[-1].strip()
                raw_opts.append(clean_opt)
            random.shuffle(raw_opts)

            letters = ["A)", "B)", "C)", "D)"]
            self.shuffled_options = [f"{letters[i]} {raw_opts[i]}" for i in range(len(raw_opts))]

        for i, lbl in enumerate(self.opt_labels):
            if i < len(self.shuffled_options):
                lbl.config(text=self.shuffled_options[i], bg="#1e272e", relief="solid")
            else:
                lbl.config(text="")

        self.refresh_host_panel()

    def refresh_host_panel(self):
        for widget in self.btn_container.winfo_children():
            widget.destroy()

        # Create an extra grid column boundary to house the Undo option safely
        col_count = len(self.scores) + 2 if self.question_revealed else 2
        self.btn_container.grid_columnconfigure(list(range(col_count)), weight=1)

        if not self.question_revealed:
            self.sep_lbl.config(text="HOST PANEL: ADVANCE WHEN READY")

            # Left side: Next Question
            next_btn = tk.Label(self.btn_container, text="▶️ NEXT QUESTION", font=("Arial", 13, "bold"), bg="#2ecc71",
                                fg="black", cursor="hand2", bd=1, relief="raised", pady=10)
            next_btn.grid(row=0, column=0, padx=(0, 4), pady=5, sticky="ew")
            next_btn.bind("<Button-1>", lambda e: self.display_current_question())

            # Right side: Undo button (toggled dynamic visual appearance based on availability)
            undo_bg = "#34495e" if self.game_history else "#1e272e"
            undo_fg = "#95a5a6" if self.game_history else "#57606f"
            undo_cursor = "hand2" if self.game_history else "arrow"

            undo_btn = tk.Label(self.btn_container, text="⏪ UNDO", font=("Arial", 13, "bold"), bg=undo_bg, fg=undo_fg,
                                cursor=undo_cursor, bd=1, relief="raised", pady=10)
            undo_btn.grid(row=0, column=1, padx=(4, 0), pady=5, sticky="ew")
            if self.game_history:
                undo_btn.bind("<Button-1>", lambda e: self.trigger_undo_rewind())

        else:
            self.sep_lbl.config(text="HOST PANEL: CLICK WHO BUZZED IN FIRST")

            # Team buzzer click rows
            for i, team in enumerate(self.scores.keys()):
                bg_hex = self.team_colors[team]
                fg_color = "black" if "Yellow" in team else "white"

                btn = tk.Label(self.btn_container, text=f"🚨 {team}", font=("Arial", 11, "bold"), bg=bg_hex, fg=fg_color,
                               cursor="hand2", bd=1, relief="raised", pady=10)
                btn.grid(row=0, column=i, padx=4, pady=5, sticky="ew")
                btn.bind("<Button-1>", lambda e, t=team: self.award_points(t))

            # Skip Question Column Button
            skip_btn = tk.Label(self.btn_container, text="❌ Skip Q", font=("Arial", 11, "bold"), bg="#95a5a6",
                                fg="black", cursor="hand2", bd=1, relief="raised", pady=10)
            skip_btn.grid(row=0, column=len(self.scores), padx=4, pady=5, sticky="ew")
            skip_btn.bind("<Button-1>", lambda e: self.skip_question())

            # Undo active question back to intermission card
            undo_btn = tk.Label(self.btn_container, text="⏪ Undo", font=("Arial", 11, "bold"), bg="#34495e",
                                fg="#ecf0f1", cursor="hand2", bd=1, relief="raised", pady=10)
            undo_btn.grid(row=0, column=len(self.scores) + 1, padx=4, pady=5, sticky="ew")
            undo_btn.bind("<Button-1>", lambda e: self.trigger_undo_rewind())

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
        """Pops the last stored snapshot out of history and forces a full game state restore."""
        if not self.game_history:
            return

        previous_state = self.game_history.pop()

        self.current_idx = previous_state["current_idx"]
        self.scores = previous_state["scores"]
        self.shuffled_options = previous_state["shuffled_options"]
        target_revelation = previous_state["question_revealed"]

        # Route rendering loops elegantly depending on what type of screen we are restoring
        if target_revelation:
            self.display_current_question(from_undo=True)
        else:
            self.prepare_next_turn()

    def change_score_manually(self, team, amount):
        self.scores[team] = max(0, self.scores[team] + amount)
        self.refresh_score_display()

    def reveal_answer(self):
        if self.question_revealed and self.current_idx < len(self.questions):
            target_ans = self.questions[self.current_idx].get("answer", "")
            self.ans_label.config(text=f"🎯 Correct Answer Target: {target_ans}")

    def refresh_score_display(self):
        for widget in self.score_bars.winfo_children():
            widget.destroy()

        self.score_bars.grid_columnconfigure(list(range(len(self.scores))), weight=1)
        for i, (team, score) in enumerate(self.scores.items()):
            team_color = self.team_colors[team]

            card_container = tk.Frame(self.score_bars, bg=self.bg_dark)
            card_container.grid(row=0, column=i, padx=8, sticky="ew")
            card_container.grid_columnconfigure((0, 1), weight=1)

            card = tk.Label(card_container, text=f"{team}\n{score} pts", font=("Arial", 12, "bold"), bg="#34495e",
                            fg=team_color, bd=1, relief="solid", pady=8)
            card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

            minus_btn = tk.Label(card_container, text="−", font=("Arial", 9, "bold"), bg="#34495e", fg="#95a5a6",
                                 cursor="hand2", bd=1, relief="flat", width=4)
            minus_btn.grid(row=1, column=0, padx=(0, 2), sticky="e")
            minus_btn.bind("<Button-1>", lambda e, t=team: self.change_score_manually(t, -1))

            minus_btn.bind("<Enter>", lambda e, w=minus_btn: w.config(bg="#e74c3c", fg="white"))
            minus_btn.bind("<Leave>", lambda e, w=minus_btn: w.config(bg="#34495e", fg="#95a5a6"))

            plus_btn = tk.Label(card_container, text="+", font=("Arial", 9, "bold"), bg="#34495e", fg="#95a5a6",
                                cursor="hand2", bd=1, relief="flat", width=4)
            plus_btn.grid(row=1, column=1, padx=(2, 0), sticky="w")
            plus_btn.bind("<Button-1>", lambda e, t=team: self.change_score_manually(t, 1))

            plus_btn.bind("<Enter>", lambda e, w=plus_btn: w.config(bg="#2ecc71", fg="black"))
            plus_btn.bind("<Leave>", lambda e, w=plus_btn: w.config(bg="#34495e", fg="#95a5a6"))

    def trigger_game_over(self):
        self.meta_frame.destroy()
        self.q_frame.destroy()
        self.opts_frame.destroy()
        self.reveal_btn.destroy()
        self.ans_label.destroy()
        self.host_frame.destroy()
        self.score_frame.destroy()

        end_f = tk.Frame(self.root, bg=self.bg_dark)
        end_f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(end_f, text="🏁 GAME OVER!", font=("Arial", 28, "bold"), bg=self.bg_dark, fg="#f1c40f").pack(pady=10)

        max_score = max(self.scores.values())
        winners = [t for t, s in self.scores.items() if s == max_score]

        if len(winners) == 1:
            win_text = f"🏆 Champion: {winners[0]}\nScore: {max_score} points"
            lbl_color = self.team_colors[winners[0]]
        else:
            win_text = f"🤝 Tied Match Between:\n{', '.join(winners)}\nScore: {max_score} points"
            lbl_color = "#ecf0f1"

        tk.Label(end_f, text=win_text, font=("Arial", 18, "bold"), bg=self.bg_dark, fg=lbl_color,
                 justify="center").pack(pady=15)

        restart_btn = tk.Label(end_f, text="🔄 Restart Application", font=("Arial", 12, "bold"), bg="#3498db",
                               fg="white", cursor="hand2", bd=1, relief="raised", padx=20, pady=10)
        restart_btn.pack(pady=20)
        restart_btn.bind("<Button-1>", lambda e: self.reset_entire_app())

    def reset_entire_app(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizShowApp(root)
    root.mainloop()