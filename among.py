import sys
import time
import threading

# Emoji mapping
EMOJIS = {
    "blank": "⬛",
    "yellow": "🟨",
    "green": "🟩"
}

# Fixed crewmate pattern
CREWMATE_PATTERN = [
    ["blank", "yellow", "yellow", "yellow", "blank"],
    ["yellow", "yellow", "green",  "green",  "blank"],
    ["yellow", "yellow", "yellow", "yellow", "blank"],
    ["green",  "yellow", "blank",  "yellow", "green"],
    ["green",  "green",  "green",  "green",  "green"]
]

CREWMATE_PATTERN_TWO = [
    ["blank", "yellow", "yellow", "yellow", "yellow"],
    ["yellow", "yellow", "green",  "green",  "green"],
    ["yellow", "yellow", "green",  "green",  "green"],
    ["yellow", "yellow", "yellow", "yellow", "yellow"],
    ["blank",  "yellow", "yellow",  "yellow", "yellow"],
    ["blank",  "yellow",  "blank",  "blank",  "yellow"]
]

CREWMATE_PATTERN_THREE = [
    ["blank", "blank", "blank", "blank", "blank"],
    ["blank", "yellow", "yellow",  "yellow",  "blank"],
    ["yellow", "yellow", "green",  "green",  "blank"],
    ["yellow", "yellow", "yellow", "yellow", "blank"],
    ["blank",  "yellow", "blank",  "yellow", "blank"],
    ["green",  "green",  "green",  "green",  "green"]
]

CREWMATE_PATTERN_FOUR = [
    ["blank", "blank", "green", "green",  "green"],
    ["blank", "green", "green", "yellow",  "yellow"],
    ["blank", "green", "green", "green", "green"],
    ["blank", "blank",  "green", "blank",  "green"],
    ["green",  "green",  "green",  "green",  "green"]
]

CREWMATE_PATTERN_FIVE = [
    ["blank", "blank", "green", "green",  "green"],
    ["blank", "green", "green", "blank",  "blank"],
    ["blank", "green", "green", "green", "green"],
    ["blank", "blank",  "green", "blank",  "green"],
    ["green",  "green",  "green",  "green",  "green"]
]

def load_words(filename):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]


def matches_pattern(word, guess, flat_pattern):
    """
    Check if a word matches the pattern produced by a guess in Wordle.
    
    Args:
        word: The target word to check
        guess: The guessed word
        flat_pattern: List of colors ["green", "yellow", "blank"] for each position
    
    Returns:
        bool: True if the word could produce this pattern with this guess
    """
    guess = guess.lower()
    word = word.lower()
    
    if len(guess) != len(word) or len(guess) != len(flat_pattern):
        return False
    
    # First pass: handle greens and count remaining letters
    word_remaining = list(word)  # Letters not yet accounted for by greens
    
    for i in range(len(guess)):
        if flat_pattern[i] == "green":
            if word[i] != guess[i]:
                return False
            # Remove this letter from remaining count
            word_remaining[i] = None
    
    # Second pass: handle yellows and blanks
    for i in range(len(guess)):
        g_letter = guess[i]
        
        if flat_pattern[i] == "yellow":
            # Yellow means: letter exists in word but not at this position
            if word[i] == g_letter:
                return False  # Can't be yellow if it's in the right position
            
            # Check if this letter exists elsewhere in the remaining letters
            if g_letter not in word_remaining:
                return False
            
            # Remove one instance of this letter from remaining count
            try:
                word_remaining[word_remaining.index(g_letter)] = None
            except ValueError:
                return False
        
        elif flat_pattern[i] == "blank":
            # Blank means this letter shouldn't exist in any remaining positions
            # (it might exist but already be accounted for by greens/previous yellows)
            if g_letter in word_remaining:
                return False
    
    return True
    
    
def reverse_row(row):
    reversed_row = []
    for i in range(len(row)):
        p = row[i]
        
        if p == "green":
            reversed_row.append("yellow")
        
        if p == "yellow":
            reversed_row.append("green")
        
        if p == "blank":
            reversed_row.append("blank")
    
    return reversed_row

    
def among_us_generator(actual_word, crewmate_pattern, words):
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    amongi_possible = True
    
    # Shared variables for threading
    searching = threading.Event()
    spinner_stop = threading.Event()
    
    def spinner_thread():
        idx = 0
        while not spinner_stop.is_set():
            if searching.is_set():
                sys.stdout.write(f"\rSearching... {spinner[idx % len(spinner)]}   ")
                sys.stdout.flush()
                idx += 1
            time.sleep(0.025)
    
    # Start spinner thread
    spinner_thread_obj = threading.Thread(target=spinner_thread, daemon=True)
    spinner_thread_obj.start()
    
    for row_index, row in enumerate(crewmate_pattern):
        # Start searching for this row
        searching.set()
        
        found_word = False
        for guessed_word in words:
            if matches_pattern(actual_word, guessed_word, row):
                # Stop searching and clear the spinner
                searching.clear()
                sys.stdout.write("\r" + " " * 20 + "\r")
                sys.stdout.flush()
                
                # Print the match with the current row pattern
                sys.stdout.write(f"{''.join(EMOJIS[c] for c in row)} : {guessed_word}\n")
                sys.stdout.flush()
                
                found_word = True
                break
        
        # If no word found for this row, continue to next row
        if not found_word:
            searching.clear()
            sys.stdout.write("\r" + " " * 20 + "\r")
            sys.stdout.write(f"{''.join(EMOJIS[c] for c in row)} : (no match found)\n")
            amongi_possible = False
            
    if(not amongi_possible):
        sys.stdout.write("Trying reversed crewmate\n")
        amongi_possible = True
        for row_index, row in enumerate(crewmate_pattern):
            row = reverse_row(row)
            
            # Start searching for this row
            searching.set()
            
            found_word = False
            for guessed_word in words:
                if matches_pattern(actual_word, guessed_word, row):
                    # Stop searching and clear the spinner
                    searching.clear()
                    sys.stdout.write("\r" + " " * 20 + "\r")
                    sys.stdout.flush()
                    
                    # Print the match with the current row pattern
                    sys.stdout.write(f"{''.join(EMOJIS[c] for c in row)} : {guessed_word}\n")
                    sys.stdout.flush()
                    
                    found_word = True
                    break
            
            # If no word found for this row, continue to next row
            if not found_word:
                searching.clear()
                sys.stdout.write("\r" + " " * 20 + "\r")
                sys.stdout.write(f"{''.join(EMOJIS[c] for c in row)} : (no match found)\n")
                amongi_possible = False
    
    # Stop the spinner thread
    searching.clear()
    spinner_stop.set()
    
    sys.stdout.write("\n\nSearch complete.\n\n")
    
    return amongi_possible

if __name__ == "__main__":
    # Check if command-line argument was provided
    if len(sys.argv) > 1:
        guess_word = sys.argv[1].strip()
    else:
        guess_word = input("Enter a guess word: ").strip()
    
    # Load valid words and process the guess
    words = load_words("valid-wordle-words.txt")
    # words = load_words("five_letter_words.txt")
    if not among_us_generator(guess_word, CREWMATE_PATTERN, words):
        if not among_us_generator(guess_word, CREWMATE_PATTERN_TWO, words):
            if not among_us_generator(guess_word, CREWMATE_PATTERN_THREE, words):
                if not among_us_generator(guess_word, CREWMATE_PATTERN_FOUR, words):
                    among_us_generator(guess_word, CREWMATE_PATTERN_FIVE, words)