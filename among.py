import time
import sys

# Emoji mappings
EMOJIS = {
    "blank": "⬛",   # Gray square
    "yellow": "🟨", # Yellow square
    "green": "🟩"   # Green square
}

def load_words(filename):
    with open(filename, "r") as f:
        return [line.strip().lower() for line in f if line.strip()]

def swap_yellow_green(pattern):
    return [
        "green" if p == "yellow" else
        "yellow" if p == "green" else
        p
        for p in pattern
    ]

def matches_pattern(word, guess, pattern):
    for i, (g_letter, p) in enumerate(zip(guess, pattern)):
        if p == "green" and word[i] != g_letter:
            return False
        if p == "yellow":
            if word[i] == g_letter or g_letter not in word:
                return False
        if p == "blank" and g_letter not in [guess[j] for j, status in enumerate(pattern) if status in ("green", "yellow")]:
            if g_letter in word:
                return False
    return True

def among_us_generator(guess, pattern, words):
    print("Searching for amongus word...")
    time.sleep(0.8)

    # Animation for searching
    dots = [".  ", ".. ", "...", ".. ", ".  "]
    for d in dots:
        sys.stdout.write(f"\rSearching for amongus word{d}")
        sys.stdout.flush()
        time.sleep(0.4)

    matches = []
    for word in words:
        if matches_pattern(word, guess, pattern):
            matches.append(word)
            break

    if not matches:
        swapped = swap_yellow_green(pattern)
        for word in words:
            if matches_pattern(word, guess, swapped):
                matches.append(word)
                break

    # Show result
    if matches:
        chosen = matches[0]
        pattern_to_show = pattern if matches_pattern(chosen, guess, pattern) else swap_yellow_green(pattern)
        emoji_line = "".join(EMOJIS[p] for p in pattern_to_show)
        sys.stdout.write(f"\r{emoji_line} : {chosen}\n")
    else:
        sys.stdout.write("\rNo matches found.\n")

if __name__ == "__main__":
    word_list = load_words("valid-wordle-words.txt")
    guess_word = "cigar"
    pattern = ["blank", "yellow", "yellow", "yellow", "blank"]
    among_us_generator(guess_word, pattern, word_list)
