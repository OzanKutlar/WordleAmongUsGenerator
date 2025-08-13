# Read words from NWL2020.txt and filter only 5-letter words

input_file = "NWL2020.txt"
output_file = "five_letter_words.txt"

five_letter_words = []

with open(input_file, "r") as file:
    for line in file:
        # Remove leading/trailing whitespace
        line = line.strip()
        if not line:
            continue  # skip empty lines
        
        # Split the line and take the first part (the word)
        word = line.split()[0]
        
        # Keep only 5-letter words
        if len(word) == 5:
            five_letter_words.append(word)

# Optionally, save the filtered words to a new file
with open(output_file, "w") as out_file:
    for word in five_letter_words:
        out_file.write(word + "\n")

print(f"Found {len(five_letter_words)} five-letter words. Saved to {output_file}.")
