# ==========================================================
# CAIGS ULTRA AI - WORKSHEET EMOJI ENGINE (UPGRADED)
# CHILD WORKSHEET MODE • EMOJI-ONLY MODE • PRINT OPTIMIZED
# ==========================================================

import os
import re
import spacy
from collections import Counter
from nltk.corpus import wordnet

# ----------------------------------------------------------
# LOAD NLP MODEL
# ----------------------------------------------------------

nlp = spacy.load("en_core_web_sm")

# ----------------------------------------------------------
# PATH CONFIGURATION
# ----------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOJI_FOLDER = os.path.join(BASE_DIR, "emoji_images")

# ----------------------------------------------------------
# EXTENDED WORD → EMOJI MAP
# ----------------------------------------------------------

WORD_TO_EMOJI = {

# PEOPLE
"boy":"👦","girl":"👧","child":"🧒","children":"🧒","baby":"👶",
"man":"👨","woman":"👩","mother":"👩","father":"👨",
"teacher":"👩‍🏫","student":"🧑‍🎓","doctor":"👩‍⚕️",
"nurse":"👩‍⚕️","police":"👮","king":"🤴","queen":"👸",
"family":"👨‍👩‍👧‍👦","friend":"🤝",

# BODY
"brain":"🧠","heart":"❤️","eye":"👁","eyes":"👀",
"hand":"✋","hands":"🤲","leg":"🦵","legs":"🦵",
"arm":"💪","blood":"🩸","bone":"🦴","ear":"👂",
"nose":"👃","mouth":"👄","head":"🧑",

# EMOTIONS
"happy":"😊","sad":"😢","angry":"😠","cry":"😭",
"laugh":"😂","smile":"😊","love":"❤️",
"fear":"😨","surprise":"😲","excited":"🤩",

# NATURE
"sun":"☀️","moon":"🌙","star":"⭐","cloud":"☁️",
"rain":"🌧","rainbow":"🌈","fire":"🔥",
"water":"💧","river":"🌊","tree":"🌳",
"flower":"🌸","leaf":"🍃","forest":"🌲",
"mountain":"⛰","earth":"🌍","planet":"🪐",

# FOOD
"apple":"🍎","banana":"🍌","mango":"🥭","orange":"🍊",
"grapes":"🍇","bread":"🍞","rice":"🍚",
"milk":"🥛","egg":"🥚","cake":"🎂",
"icecream":"🍦","chocolate":"🍫","pizza":"🍕",
"burger":"🍔","tea":"🍵","coffee":"☕",

# SCHOOL
"book":"📘","notebook":"📓","pen":"🖊️",
"pencil":"✏️","school":"🏫","class":"🏫",
"exam":"📝","homework":"📘","lesson":"📖",
"question":"❓","answer":"✅","number":"🔢",

# SCIENCE
"atom":"⚛️","science":"🔬","microscope":"🔬",
"experiment":"🧪","energy":"⚡","electricity":"⚡",
"robot":"🤖","computer":"💻",

# ACTIONS
"run":"🏃","walk":"🚶","jump":"🤾",
"dance":"💃","sing":"🎤","write":"✍️",
"read":"📖","draw":"🎨","play":"🎮",
"clap":"👏","tap":"👆","eat":"🍽",

# ANIMALS
"dog":"🐶","cat":"🐱","lion":"🦁","tiger":"🐯",
"elephant":"🐘","monkey":"🐒","cow":"🐄",
"goat":"🐐","horse":"🐎","pig":"🐷",
"hen":"🐔","duck":"🦆","bird":"🐦",
"parrot":"🦜","fish":"🐟","frog":"🐸",
"snake":"🐍","bear":"🐻","rabbit":"🐰",
"wolf":"🐺","fox":"🦊","panda":"🐼",

# TRANSPORT
"car":"🚗","bus":"🚌","train":"🚆",
"cycle":"🚲","bike":"🚲","plane":"✈️",
"boat":"🚤","ship":"🚢","rocket":"🚀",

# OBJECTS
"light":"💡","clock":"⏰","phone":"📱",
"camera":"📷","gift":"🎁","key":"🔑",
"box":"📦","ball":"⚽","umbrella":"☂️",
# GENERIC MCQ DISTRACTORS
"thing":"📦",
"object":"📦",
"item":"📦",
"part":"🧩",
"piece":"🧩",
"word":"🔤",
"term":"🔤",
"option":"🔘"
}

# ----------------------------------------------------------
# AUTO EXPAND PLURALS
# ----------------------------------------------------------

expanded = {}
for word, emoji in WORD_TO_EMOJI.items():
    expanded[word] = emoji
    expanded[word + "s"] = emoji
    expanded[word + "es"] = emoji

WORD_TO_EMOJI = expanded

# ----------------------------------------------------------
# UTILITIES
# ----------------------------------------------------------

def emoji_to_filename(emoji_char):
    cleaned = emoji_char.replace("\ufe0f", "")
    return "-".join(f"{ord(c):x}" for c in cleaned) + ".png"

def get_emoji_for_word(word):
    return WORD_TO_EMOJI.get(word.lower().strip())

def get_emoji_image_path(emoji_char):
    # Try hex format first (e.g., 1f338.png)
    hex_filename = emoji_to_filename(emoji_char)
    hex_path = os.path.join(EMOJI_FOLDER, hex_filename)
    if os.path.exists(hex_path):
        return hex_path
    
    # Try direct emoji filename (e.g., 🌸.png)
    direct_filename = emoji_char + ".png"
    direct_path = os.path.join(EMOJI_FOLDER, direct_filename)
    if os.path.exists(direct_path):
        return direct_path
    
    # Try with common variations
    cleaned = emoji_char.replace("\ufe0f", "")
    for ext in ["png", "gif", "jpg", "jpeg"]:
        direct_path = os.path.join(EMOJI_FOLDER, cleaned + "." + ext)
        if os.path.exists(direct_path):
            return direct_path
    
    return None

# ==========================================================
# MODE 1 – HEAVY INLINE EMOJI MODE
# (emoji + word together)
# ==========================================================

def parse_text_heavy_emoji(text):

    if not text:
        return []

    doc = nlp(text)
    output = []

    for token in doc:
        word = token.text
        lemma = re.sub(r"[^\w]", "", token.lemma_.lower())

        emoji_char = get_emoji_for_word(lemma)

        if emoji_char:
            image_path = get_emoji_image_path(emoji_char)
            if image_path:
                output.append(("IMAGE", image_path))
            else:
                output.append(("TEXT", emoji_char + " "))

        output.append(("TEXT", word + " "))

    return output

# ==========================================================
# MODE 2 – EMOJI ONLY REPLACEMENT MODE
# (NOUNS replaced completely by emoji)
# ==========================================================

def parse_text_emoji_only(text):

    if not text:
        return []

    doc = nlp(text)
    output = []

    for token in doc:

        word = token.text
        lemma = re.sub(r"[^\w]", "", token.lemma_.lower())

        if token.pos_ == "NOUN":

            emoji_char = get_emoji_for_word(lemma)

            if emoji_char:
                image_path = get_emoji_image_path(emoji_char)
                if image_path:
                    output.append(("IMAGE", image_path))
                else:
                    output.append(("TEXT", emoji_char + " "))
                continue

        output.append(("TEXT", word + " "))

    return output

# ==========================================================
# EXTRACT NEW WORDS (TOP FREQUENT NOUNS)
# ==========================================================

def extract_new_words(text, top_n=6):

    doc = nlp(text)
    nouns = [token.text.lower() for token in doc if token.pos_ == "NOUN"]

    counter = Counter(nouns)
    return [word for word, _ in counter.most_common(top_n)]

# ==========================================================
# EXTRACT DIFFICULT WORDS
# (longer words with simple meaning)
# ==========================================================

def extract_difficult_words(text, max_words=5):

    doc = nlp(text)
    difficult = []

    for token in doc:
        word = token.text.strip()

        if len(word) > 6 and token.pos_ in ["NOUN", "VERB", "ADJ"]:
            meaning = get_simple_meaning(word)
            if meaning:
                difficult.append((word, meaning))

        if len(difficult) >= max_words:
            break

    return difficult

# ----------------------------------------------------------
# SIMPLE WORD MEANING USING WORDNET
# ----------------------------------------------------------

def get_simple_meaning(word):

    synsets = wordnet.synsets(word)

    if not synsets:
        return None

    definition = synsets[0].definition()

    # shorten definition
    short_def = definition.split(";")[0]
    short_def = short_def.split(",")[0]

    return short_def.capitalize()

# ==========================================================
# HEADER PARSER (NO LIMITS)
# ==========================================================

def parse_header_with_emoji(text):

    if not text:
        return []

    doc = nlp(text)
    output = []

    for token in doc:
        word = token.text
        lemma = re.sub(r"[^\w]", "", token.lemma_.lower())

        emoji_char = get_emoji_for_word(lemma)

        if emoji_char:
            image_path = get_emoji_image_path(emoji_char)
            if image_path:
                output.append(("IMAGE", image_path))
            else:
                output.append(("TEXT", emoji_char + " "))

        output.append(("TEXT", word + " "))

    return output