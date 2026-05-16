import os
import math
from collections import defaultdict

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Label, Static
from textual.message import Message
from textual.worker import get_current_worker

from rich.text import Text

# --- Logic ---
def load_words():
    paths = ["five_letter_words.txt", "valid-wordle-words.txt", "NWL2020.txt"]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r") as f:
                words = [w.strip().upper() for w in f]
                # ensure strict 5-letter
                words = [w for w in words if len(w) == 5]
            if words:
                return words
    return ["APPLE", "BERRY", "CHERRY", "DELTA", "EAGLE"]

def compute_pattern(guess: str, target: str) -> tuple[int, ...]:
    pattern = [0, 0, 0, 0, 0]
    if guess == target:
        return (2, 2, 2, 2, 2)
        
    t_list = list(target)
    for i in range(5):
        if guess[i] == target[i]:
            pattern[i] = 2
            t_list[i] = None
            
    for i in range(5):
        if pattern[i] == 0:
            c = guess[i]
            if c in t_list:
                pattern[i] = 1
                t_list[t_list.index(c)] = None
                
    return tuple(pattern)

def filter_words(words: list[str], guess: str, pattern: tuple[int, ...]) -> list[str]:
    return [w for w in words if compute_pattern(guess, w) == pattern]

def create_word_text(word: str, colors: list[int]) -> Text:
    text = Text()
    for char, color in zip(word, colors):
        color_bg = {0: "#666666", 1: "#b59f3b", 2: "#538d4e"}[color]
        text.append(f" {char} ", style=f"bold white on {color_bg}")
        text.append(" ")
    return text

# --- Messages ---
class GuessSubmitted(Message):
    def __init__(self, guess: str, colors: list[int], control: Static):
        self.guess = guess
        self.colors = colors
        self.control = control
        super().__init__()

class EliminationResults(Message):
    def __init__(self, results: list[tuple[float, str]]):
        self.results = results
        super().__init__()

# --- Custom Widgets ---
class GuessEditor(Static, can_focus=True):
    BINDINGS = [
        ("left", "move_left", "Left"),
        ("right", "move_right", "Right"),
        ("enter", "cycle_color", "Color"),
        ("space", "submit", "Submit"),
    ]

    def __init__(self, word: str):
        super().__init__()
        self.word = word.upper()
        self.colors = [0, 0, 0, 0, 0]
        self.cursor_idx = 0

    def render(self) -> Text:
        text = Text()
        for i, char in enumerate(self.word):
            color_bg = {0: "#666666", 1: "#b59f3b", 2: "#538d4e"}[self.colors[i]]
            style = f"bold white on {color_bg}"
            if i == self.cursor_idx:
                style += " underline"
            text.append(f" {char} ", style=style)
            text.append(" ")
        
        text.append("\n\n")
        text.append(" ←/→ : Move Cursor\n", style="dim")
        text.append(" Enter : Cycle Color\n", style="dim")
        text.append(" Space : Confirm Guess", style="bold green")
        return text

    def action_move_left(self):
        if self.cursor_idx > 0:
            self.cursor_idx -= 1
            self.refresh()

    def action_move_right(self):
        if self.cursor_idx < 4:
            self.cursor_idx += 1
            self.refresh()

    def action_cycle_color(self):
        self.colors[self.cursor_idx] = (self.colors[self.cursor_idx] + 1) % 3
        self.refresh()

    def action_submit(self):
        self.post_message(GuessSubmitted(self.word, self.colors, self))

# --- Main App ---
class WordleSolverApp(App):
    TITLE = "Wordle Solver"
    CSS = """
    Screen {
        layout: horizontal;
    }
    .column {
        width: 1fr;
        height: 100%;
        border: solid #555555;
        padding: 1;
        margin: 0 1;
    }
    .column-title {
        text-style: bold;
        text-align: center;
        padding-bottom: 1;
        width: 100%;
        border-bottom: solid #555555;
        margin-bottom: 1;
    }
    #possible-list, #elimination-list {
        height: 1fr;
        overflow-y: auto;
    }
    #guesses-list {
        height: 1fr;
        overflow-y: auto;
        border-bottom: solid #555555;
        margin-bottom: 1;
        padding-bottom: 1;
    }
    #elim-status {
        text-style: italic;
        color: yellow;
        margin-bottom: 1;
    }
    #word-input {
        width: 100%;
        margin-bottom: 1;
    }
    #editor-container {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(classes="column"):
                yield Label("Possible Words", id="col1-title", classes="column-title")
                yield VerticalScroll(id="possible-list")
                
            with Vertical(classes="column"):
                yield Label("Elimination Words", id="col2-title", classes="column-title")
                yield Label("Loading dictionary...", id="elim-status")
                yield VerticalScroll(id="elimination-list")
                
            with Vertical(classes="column"):
                yield Label("Your Guesses", id="col3-title", classes="column-title")
                yield VerticalScroll(id="guesses-list")
                yield Input(placeholder="Type 5-letter word + Enter", id="word-input", max_length=5)
                yield Vertical(id="editor-container")
        yield Footer()

    async def on_mount(self):
        self.all_words = load_words()
        self.possible_words = self.all_words.copy()
        
        self.query_one("#word-input").focus()
        
        await self.update_possible_words()
        self.compute_eliminations(self.possible_words, self.all_words)

    async def update_possible_words(self):
        vs = self.query_one("#possible-list")
        await vs.remove_children()
        
        labels = [Label(w) for w in self.possible_words[:200]]
        if len(self.possible_words) > 200:
            labels.append(Label(Text(f"... and {len(self.possible_words)-200} more", style="dim")))
            
        if labels:
            await vs.mount(*labels)
            
        self.query_one("#col1-title").update(f"Possible Words ({len(self.possible_words)})")

    @on(Input.Submitted, "#word-input")
    def handle_input_submitted(self, event: Input.Submitted):
        word = event.value.strip().upper()
        if len(word) != 5:
            self.notify("Word must be exactly 5 letters long", severity="error")
            return
            
        if word not in self.all_words:
            self.notify("Word not in dictionary (Proceeding anyway)", severity="warning")
            
        event.input.value = ""
        event.input.display = False
        
        editor = GuessEditor(word)
        container = self.query_one("#editor-container")
        container.mount(editor)
        editor.focus()

    @on(GuessSubmitted)
    async def handle_guess_submitted(self, event: GuessSubmitted):
        await event.control.remove()
        
        inp = self.query_one("#word-input")
        inp.display = True
        inp.focus()
        
        guess_text = create_word_text(event.guess, event.colors)
        await self.query_one("#guesses-list").mount(Label(guess_text))
        
        self.possible_words = filter_words(self.possible_words, event.guess, tuple(event.colors))
        await self.update_possible_words()
        
        self.query_one("#elim-status").update("Calculating expected info...")
        await self.query_one("#elimination-list").remove_children()
        
        self.compute_eliminations(self.possible_words, self.all_words)

    @work(thread=True, exclusive=True)
    def compute_eliminations(self, possible: list[str], all_words: list[str]):
        worker = get_current_worker()
        
        if len(possible) <= 1:
            self.post_message(EliminationResults([]))
            return
            
        results = []
        tot = len(possible)
        
        # Process all words. Runs in a thread so it doesn't block the UI.
        for w in all_words:
            if worker.is_cancelled:
                return
                
            pattern_counts = {}
            for t in possible:
                pat = compute_pattern(w, t)
                pattern_counts[pat] = pattern_counts.get(pat, 0) + 1
                
            e = 0.0
            for count in pattern_counts.values():
                p = count / tot
                e -= p * math.log2(p)
                
            results.append((e, w))
            
        results.sort(reverse=True)
        self.post_message(EliminationResults(results[:100]))

    @on(EliminationResults)
    async def handle_elimination_results(self, event: EliminationResults):
        if len(self.possible_words) <= 1:
            self.query_one("#elim-status").update("Target found or no words left.")
        else:
            self.query_one("#elim-status").update(f"Top 100 choices (Bits):")
            
        vs = self.query_one("#elimination-list")
        await vs.remove_children()
        
        labels = []
        for score, w in event.results:
            labels.append(Label(f"{w}  |  {score:.2f} bits"))
            
        if labels:
            await vs.mount(*labels)

if __name__ == "__main__":
    app = WordleSolverApp()
    app.run()
