import sys
import time
from typing import List, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    from rich import box
    from rich.spinner import Spinner
except ImportError:
    sys.exit("Please install the 'rich' library: pip install rich")

# --- Configuration & Constants ---

EMOJI_MAP = {
    "blank": "⬛",
    "yellow": "🟨",
    "green": "🟩"
}

COLOR_MAP = {
    "blank": "grey30",
    "yellow": "gold1",
    "green": "green3"
}

PATTERNS = {
    "Standard": [
        ["blank", "yellow", "yellow", "yellow", "blank"],
        ["yellow", "yellow", "green",  "green",  "blank"],
        ["yellow", "yellow", "yellow", "yellow", "blank"],
        ["green",  "yellow", "blank",  "yellow", "green"],
        ["green",  "green",  "green",  "green",  "green"]
    ],
    "Walking": [
        ["blank", "yellow", "yellow", "yellow", "yellow"],
        ["yellow", "yellow", "green",  "green",  "green"],
        ["yellow", "yellow", "green",  "green",  "green"],
        ["yellow", "yellow", "yellow", "yellow", "yellow"],
        ["blank",  "yellow", "yellow",  "yellow", "yellow"],
        ["blank",  "yellow",  "blank",  "blank",  "yellow"]
    ],
    "Backpack": [
        ["blank", "blank", "blank", "blank", "blank"],
        ["blank", "yellow", "yellow",  "yellow",  "blank"],
        ["yellow", "yellow", "green",  "green",  "blank"],
        ["yellow", "yellow", "yellow", "yellow", "blank"],
        ["blank",  "yellow", "blank",  "yellow", "blank"],
        ["green",  "green",  "green",  "green",  "green"]
    ],
    "Amogus Short": [
        ["blank", "blank", "green", "green",  "green"],
        ["blank", "green", "green", "yellow",  "yellow"],
        ["blank", "green", "green", "green", "green"],
        ["blank", "blank",  "green", "blank",  "green"],
        ["green",  "green",  "green",  "green",  "green"]
    ],
    "Amogus Tall": [
        ["blank", "blank", "green", "green",  "green"],
        ["blank", "green", "green", "blank",  "blank"],
        ["blank", "green", "green", "green", "green"],
        ["blank", "blank",  "green", "blank",  "green"],
        ["green",  "green",  "green",  "green",  "green"]
    ]
}

console = Console()

# --- Logic ---

def load_words(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File '{filename}' not found.")
        sys.exit(1)

def matches_pattern(word, guess, flat_pattern):
    guess = guess.lower()
    word = word.lower()
    
    if len(guess) != len(word) or len(guess) != len(flat_pattern):
        return False
    
    word_remaining = list(word)
    
    # First pass: handle greens
    for i in range(len(guess)):
        if flat_pattern[i] == "green":
            if word[i] != guess[i]:
                return False
            word_remaining[i] = None
    
    # Second pass: handle yellows and blanks
    for i in range(len(guess)):
        g_letter = guess[i]
        
        if flat_pattern[i] == "yellow":
            if word[i] == g_letter:
                return False
            if g_letter not in word_remaining:
                return False
            try:
                word_remaining[word_remaining.index(g_letter)] = None
            except ValueError:
                return False
        
        elif flat_pattern[i] == "blank":
            if g_letter in word_remaining:
                return False
    
    return True

def reverse_row(row):
    reversed_row = []
    for p in row:
        if p == "green": reversed_row.append("yellow")
        elif p == "yellow": reversed_row.append("green")
        else: reversed_row.append("blank")
    return reversed_row

# --- UI Generation ---

def create_styled_word(word: str, pattern_row: List[str]) -> Text:
    text = Text()
    for char, p_type in zip(word, pattern_row):
        text.append(f" {char} ", style=f"bold white on {COLOR_MAP[p_type]}")
        text.append(" ") 
    return text

def generate_table(title: str, results: List[Tuple], status="searching") -> Table:
    """
    Status can be: searching, failed, success
    """
    color = "cyan"
    if status == "failed": color = "red"
    if status == "success": color = "green"
    
    table = Table(
        box=box.ROUNDED, 
        title=f"[bold {color}]Attempt: {title}", 
        border_style=color,
        expand=True
    )
    table.add_column("Pattern", justify="center", width=20)
    table.add_column("Word", justify="center")

    for pattern_row, word_found in results:
        emoji_str = "".join(EMOJI_MAP[c] for c in pattern_row)
        
        if word_found == "...":
            # Spinner placeholder
            word_display = Spinner("dots", text="Searching...", style="cyan")
        elif word_found is None:
            # Failed row
            word_display = Text("NO MATCH FOUND", style="bold red")
        else:
            # Success row
            word_display = create_styled_word(word_found, pattern_row)
            
        table.add_row(emoji_str, word_display)
        
    return table

def attempt_pattern(target_word: str, pattern_grid: List[List[str]], words: List[str], pattern_name: str) -> bool:
    results = [] 
    
    # We use transient=False so the table stays on screen after the loop ends
    with Live(console=console, refresh_per_second=12, transient=False) as live:
        
        for row in pattern_grid:
            # 1. Show Spinner for current row
            results.append((row, "..."))
            live.update(generate_table(pattern_name, results, status="searching"))
            
            # Artificial tiny delay to let the eye catch the "scanning" vibe
            time.sleep(0.1)
            
            # 2. Search
            found_word = None
            for guess in words:
                if matches_pattern(target_word, guess, row):
                    found_word = guess
                    break
            
            # 3. Update Result
            results.pop() # Remove spinner
            
            if found_word:
                results.append((row, found_word))
                live.update(generate_table(pattern_name, results, status="searching"))
            else:
                # Row failed
                results.append((row, None))
                live.update(generate_table(pattern_name, results, status="failed"))
                time.sleep(0.5) # Pause to let user see the failure
                return False
    
    # If loop completes without returning False, we succeeded
    # One final update to paint the border green
    console.print(generate_table(pattern_name, results, status="success"))
    return True

# --- Main Execution ---

if __name__ == "__main__":
    WORD_FILE = "valid-wordle-words.txt"
    
    try:
        words = load_words(WORD_FILE)
    except SystemExit:
        words = [] # Handled in load_words

    if not words:
        sys.exit()

    if len(sys.argv) > 1:
        target = sys.argv[1].strip().upper()
    else:
        target = console.input("[bold yellow]Enter target word: [/bold yellow]").strip().upper()

    if len(target) != 5:
        console.print("[bold red]Word must be 5 letters.[/bold red]")
        sys.exit()

    console.print(f"\nGenerations for: [bold magenta]{target}[/bold magenta]\n")

    # Define the order of attempts
    attempts = [
        ("Standard Crewmate", PATTERNS["Standard"]),
        ("Standard (Reversed)", [reverse_row(r) for r in PATTERNS["Standard"]]),
        ("Walking Crewmate", PATTERNS["Walking"]),
        ("Walking (Reversed)", [reverse_row(r) for r in PATTERNS["Walking"]]),
        ("Backpack", PATTERNS["Backpack"]),
        ("Amogus Short", PATTERNS["Amogus Short"]),
        ("Amogus Tall", PATTERNS["Amogus Tall"]),
    ]

    success = False
    
    for name, grid in attempts:
        # Try to generate
        if attempt_pattern(target, grid, words, name):
            console.print(Panel(f"[bold green]SUCCESS![/bold green] Generated {name}.", border_style="green"))
            success = True
            break
        else:
            # Add a little spacer between failed attempts
            console.print("")

    if not success:
        console.print(Panel("[bold red]FAILURE[/bold red]\nCould not generate any crewmate.", border_style="red"))