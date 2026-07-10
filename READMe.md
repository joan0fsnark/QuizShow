# STEAM Quiz Show Dashboard

An interactive, high-visibility digital quiz show application built using **Python** and **Tkinter**. This project is specifically tailored for K-12/Middle School STEAM classrooms, offering a vibrant, smooth, and engaging multiplayer game show experience for students. Questions/answers can be easily modified

---

## 🚀 Features
* **Dynamic Team Customization:** Supports 2 to 6 teams with custom vibrant color selections (Red, Orange, Yellow, Green, Blue, Purple).
* **Cross-Platform macOS Compatibility:** Custom UI rendering avoids native macOS button limitations, ensuring solid, vibrant, full-color team buzz-in elements.
* **Persistent Layout Design:** Structural question boxes are fixed to eliminate annoying layout jumps or text-shifting when cycling through questions of varying lengths.
* **Type-Safe JSON Integration:** Questions, subjects, and multiple-choice options are loaded safely from a structured local `questions.json` database.
* **Host Control Panel:** Built-in dashboard allows the instructor to smoothly manage scores, reveal correct answers, or skip questions on the fly.

---

## 📁 Project Structure
* `quiz.py` — Core application logic and Tkinter UI rendering pipeline.
* `questions.json` — Pre-loaded database featuring multiple-choice items covering Science, Technology, Engineering, Arts, and Math.

---

## 🛠️ Requirements & Installation
Ensure you have Python 3.14+ installed via Homebrew (or your preferred manager).

1. Install the necessary Tkinter Tcl/Tk geometry bindings:
   ```bash
   brew install python-tk@3.14
   
2. Clone the repository and navigate into the folder:
    ```bash
    cd QuizShow
   
3. Launch the game:
    ```bash
    python3 quiz.py
   
---

## 🎮 Classroom User Guide
Follow these steps to smoothly launch, configure, and host the STEAM Quiz Show in your classroom.

1. Navigate into the folder:
    ```bash
    cd yourcomputer/user/QuizShow
   
2. Launch the game:
    ```bash
    python3 quiz.py
   
---
   
### Startup Configuration:
The Game Show Setup window will appear first.

**Choose Team Count:** Click the dropdown menu next to "How many teams?" and pick any number from 2 to 6.

**Assign Colors:** Unique configuration rows will slide into view. Assign each team a distinct, unique color from the dropdown selection (Red, Orange, Yellow, Green, Blue, or Purple) so no two teams are identical.

**Launch:** Click the bright green ```🚀 START GAME``` banner at the bottom. The setup dialog will close itself, and the primary interactive display will take over the screen.

### Hosting the Quiz Show (The Flow)
Project this dashboard onto your classroom smartboard or projector screen for maximum student visibility.

→ Present the Question: The blue header at the top specifies the active category (e.g., SCIENCE, TECHNOLOGY, MATH). Read the question and its corresponding four choices out loud to the room.

→ Student Buzz-In: Different game formats are possible. From physical desk buzzers, hands-up, or a team captain signal to claim the floor. You also can issue whiteboards to each team, give them 15-30 seconds to deliberate, and all correct answers score a point.

<u>The Host Panel Control:</u>

→ Correct Answer: If the team that buzzed in answers correctly, look at the HOST PANEL frame at the bottom and click their respective vibrant color button. The app automatically builds their leaderboard score by 1 point and pulls a fresh, random question onto the board.

→ Incorrect / Stalled: If they miss it, you can open the floor to another group, or click the gray ```❌ Skip Q``` button to wipe the question and move forward without shifting any scores.

→ Revealing Answers: If a question completely stumps the room, click the yellow ```👀 REVEAL CORRECT ANSWER``` label to instantly flash the precise solution right below it in green text.

**Crowning the Champion**
The background system automatically tracks your total question pool. Once the final question entry from your ```questions.json``` file is played, the game board freezes and pops open a dedicated Game Over! summary card. It tallies all results, breaks down potential ties, and announces your grand champion team for the day!

---

### 📝 Customizing the Questions Pool

You can easily modify the game content, update answers, or change subjects without touching any Python code.

**1. Editing Existing Questions**

To change a question, update an answer, or fix a typo, simply open the `questions.json` file in a text editor (like VS Code, Notepad, or TextEdit) and edit the text directly inside the matching dictionary keys (`subject`, `question`, `options`, `answer`).

### 2. Loading a Whole New Question Set
If you want to swap out your current trivia deck for a completely fresh topic (e.g., a "History Quiz" or a "Vocabulary Review"):
1. Create a new JSON file formatted exactly like `questions.json` (a single array containing structured question dictionaries)[cite: 3]. 
2. Save your new file inside the main project directory (e.g., `history_deck.json`).
3. Open `quiz.py` and locate **Line 24**:
   ```python
   json_filename = "questions.json"
4. Update "questions.json" to match your new file name:
   ```python
   json_filename = "history_deck.json"5. Save quiz.py and run your application normally!
5. Save ```quiz.py``` and run the application as instructed above.