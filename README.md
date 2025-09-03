# 🟩 Wordle Among Us Generator ⬛🟨

This project is a fun **Wordle pattern visualizer** that tries to generate **Among Us crewmates** out of Wordle boards.
It searches through valid Wordle words and attempts to fill out a sequence of guesses that, when combined, resemble a crewmate sprite using 🟩🟨⬛ emojis.

---

## 🚀 Features

* Generates Wordle-like grids that resemble **Among Us crewmates**.
* Uses real **Wordle word lists** for guesses.
* Includes multiple crewmate patterns (`CREWMATE_PATTERN_ONE` through `CREWMATE_PATTERN_FIVE`).
* Attempts reversed patterns if the original pattern cannot be matched.
* Fun animated **spinner** while searching for matches.

---

## 📦 Installation

Clone this repository and navigate into it:

```bash
git clone https://github.com/OzanKutlar/WordleAmongUsGenerator.git
cd WordleAmongUsGenerator
```

Make sure you have **Python 3.7+** installed.

---

## ▶️ Usage

Run the script and pass a target word (the "actual Wordle solution") as a command-line argument:

```bash
python among.py CRANE
```

Or just run it and enter a word interactively:

```bash
python among.py
Enter a guess word: CRANE
```

The program will attempt to generate crewmate patterns using valid Wordle guesses from the included word list (`valid-wordle-words.txt`).

---

## 🎨 Examples

Here are some generated crewmates from real Wordle games:

**Wordle 1535 X/6**

```
⬛⬛⬛⬛⬛
⬛🟩🟩🟩⬛
🟩🟩🟨🟨⬛
🟩🟩🟩🟩⬛
⬛🟩⬛🟩⬛
🟨🟨🟨🟨🟨
```

**Wordle 1533 5/6**

```
⬛🟨🟨🟨⬛
🟨🟨🟩🟩⬛
🟨🟨🟨🟨⬛
🟩🟨⬛🟨🟩
🟩🟩🟩🟩🟩
```

**Wordle 1527 X/6**

```
⬛🟨🟨🟨🟨
🟨🟨🟩🟩🟩
🟨🟨🟩🟩🟩
🟨🟨🟨🟨🟨
⬛🟨🟨🟨🟨
⬛🟨⬛⬛🟨
```

**Wordle 1522 5/6**

```
⬛⬛🟨🟨🟨
⬛🟨🟨🟩🟩
⬛🟨🟨🟨🟨
⬛⬛🟨⬛🟨
🟩🟩🟩🟩🟩
```

---

## 🛠️ How It Works

1. The script defines multiple **crewmate patterns** made of `green`, `yellow`, and `blank` tiles.
2. For each row in the pattern, it searches through the word list for a valid Wordle guess that would produce the same row result if compared to the target word.
3. If no valid set of words is found, it tries the **reversed pattern** (swapping 🟩 and 🟨).
4. The result is a Wordle-like output that looks like an **Among Us crewmate**.

---

## 🧑‍💻 Contributing

Contributions are welcome! Feel free to open an **issue** or submit a **pull request** if you’d like to add:

* New crewmate patterns
* Optimizations for word searching
* Extra fun shapes beyond crewmates 👀

---
