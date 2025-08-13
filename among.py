import sys
import time

# Emoji mapping
EMOJIS = {
    "blank": "⬛",
    "yellow": "🟨",
    "green": "🟩"
}

# Fixed crewmate pattern
CREWMATE_PATTERN = [
    ["blank", "yellow", "yellow", "yellow", "blank"],
    ["yellow", "yellow", "blank",  "blank",  "blank"],
    ["yellow", "yellow", "yellow", "yellow", "blank"],
    ["green",  "yellow", "blank",  "yellow", "green"],
    ["green",  "green",  "green",  "green",  "green"]
]

def load_words(filename):
    with open(filename, "r") as f:
        return [line.strip().lower() for line in f if line.strip()]


def matches_pattern(word, guess, flat_pattern):
    guess = guess.lower()
    word = word.lower()
    for i in range(len(guess)):
        g_letter = guess[i]
        p = flat_pattern[i]
        
        # ✅ GREEN: Correct letter in correct position
        if p == "green" and word[i] != g_letter:
            return False
        
        # ✅ YELLOW: Letter exists in word but NOT in current position
        if p == "yellow" and (word[i] == g_letter or g_letter not in word or (word.count(g_letter) < guess[:(i+1)].count(g_letter))):
            return False
        
        # ✅ BLANK: Letter does NOT exist in word at all
        if p == "blank" and g_letter in word:
            return False
    
    return True
    
    
    
def among_us_generator(actual_word, crewmate_pattern, words):
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    idx = 0
    
    # Process each row of the pattern
    for row_index, row in enumerate(crewmate_pattern):
        # Try both original and swapped patterns for this row
        
        # Start searching for this row
        sys.stdout.write("Searching...   ")
        sys.stdout.flush()
        
        found_word = False
        for guessed_word in words:
            # Update spinner
            sys.stdout.write(f"\rSearching... {spinner[idx % len(spinner)]}   ")
            sys.stdout.flush()
            idx += 1
            # time.sleep(0.01)
            
            if matches_pattern(actual_word, guessed_word, row):
                # Clear the spinner line
                sys.stdout.write("\r" + " " * 20 + "\r")
                sys.stdout.flush()
                
                # Print the match with the current row pattern
                sys.stdout.write(f"{''.join(EMOJIS[c] for c in row)} : {guessed_word}\n")
                sys.stdout.flush()
                
                found_word = True
                break
        
        # If no word found for this row, continue to next row
        if not found_word:
            sys.stdout.write("\r" + " " * 20 + "\r")
            sys.stdout.write(f"{''.join(EMOJIS[c] for c in row)} : (no match found)\n")
    
    sys.stdout.write("Search complete.\n")

if __name__ == "__main__":
    # Check if command-line argument was provided
    if len(sys.argv) > 1:
        guess_word = sys.argv[1].strip()
    else:
        guess_word = input("Enter a guess word: ").strip()
    
    # Load valid words and process the guess
    # words = load_words("valid-wordle-words.txt")
    words = load_words("five_letter_words.txt")
    among_us_generator(guess_word, CREWMATE_PATTERN, words)