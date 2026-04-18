# ==========================================================
# AI WORKSHEET ENGINE (PATENT-GRADE VERSION)
# ==========================================================

import re
import json
import ollama
import spacy
from collections import Counter

from emoji_engine import parse_text_heavy_emoji

# ----------------------------------------------------------
# LOAD NLP MODEL
# ----------------------------------------------------------

nlp = spacy.load("en_core_web_sm")

# ----------------------------------------------------------
# CLEAN TEXT
# ----------------------------------------------------------

def clean_text(text):

    lines = text.split("\n")

    blacklist = [
        "true or false","fill in the blanks","multiple choice",
        "match the following","iq fun zone","challenge arena",
        "draw and write","worksheet","page","xp progress",
        "achievement badges"
    ]

    cleaned = []

    for line in lines:

        line = line.strip()

        if len(line) < 6:
            continue

        lower = line.lower()

        if any(b in lower for b in blacklist):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)

# ----------------------------------------------------------
# SENTENCE EXTRACTION
# ----------------------------------------------------------

def extract_lesson_sentences(text):

    sentences = re.split(r"[.!?]", text)

    lesson = []

    for s in sentences:

        s = s.strip()

        if len(s) < 25:
            continue

        if re.match(r"^\d+\.", s):
            continue

        lesson.append(s)

    return lesson[:20]

# ----------------------------------------------------------
# KEYWORDS
# ----------------------------------------------------------

def extract_keywords(sentences):

    text = " ".join(sentences)

    doc = nlp(text)

    nouns = []

    for token in doc:
        if token.pos_ in ["NOUN","PROPN"]:
            word = token.text.lower()

            if len(word) > 2:
                nouns.append(word)

    counter = Counter(nouns)

    return [w for w,_ in counter.most_common(15)]

# ----------------------------------------------------------
# JSON PARSER
# ----------------------------------------------------------

def parse_json(text):

    try:
        return json.loads(text)

    except:

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise ValueError("No JSON found")

        json_text = match.group(0)

        json_text = re.sub(r",\s*}", "}", json_text)
        json_text = re.sub(r",\s*]", "]", json_text)

        return json.loads(json_text)

# ----------------------------------------------------------
# 🔴 SELF-CORRECTING VALIDATION ENGINE
# ----------------------------------------------------------

def validate_output(data):

    if len(data.get("true_false", [])) < 5:
        return False

    if len(data.get("fill_blanks", [])) < 5:
        return False

    if len(data.get("mcqs", [])) < 5:
        return False

    if len(data.get("match_general", [])) < 5:
        return False

    if len(data.get("iq_section", [])) < 5:
        return False

    return True


def self_correct_llm(prompt, max_attempts=3):

    last_data = None

    for _ in range(max_attempts):

        response = ollama.chat(
            model="llama3",
            messages=[{"role":"user","content":prompt}],
            format="json",
            options={"temperature":0.2}
        )

        content = response["message"]["content"]

        try:
            data = parse_json(content)
            last_data = data
        except:
            prompt += "\nFix JSON format."
            continue

        if validate_output(data):
            return data

        # try to fix
        prompt += "\nFix all constraints exactly."

    # 🔴 FALLBACK INSTEAD OF CRASH
    print("⚠️ LLM validation failed, using fallback")

    if last_data:
        return repair_data(last_data)

    # final safe empty structure
    return {
        "true_false": [],
        "fill_blanks": [],
        "mcqs": [],
        "match_general": [],
        "iq_section": []
    }
# ----------------------------------------------------------
# 🎯 DIFFICULTY ENGINE
# ----------------------------------------------------------
def generate_dummy_options(answer):

    base = answer if answer else "Answer"

    return [
        base,
        base + " 1",
        base + " 2",
        base + " 3"
    ]


import random

# ----------------------------------------------------------
# SMART OPTION GENERATOR
# ----------------------------------------------------------

def generate_smart_options(answer):

    pool = [
        "run","jump","eat","sleep","walk",
        "look","write","read","play","talk"
    ]

    options = [answer]

    for word in pool:
        if word.lower() != answer.lower():
            options.append(word)
        if len(options) == 4:
            break

    return options


# ----------------------------------------------------------
# REPAIR DATA (FINAL VERSION)
# ----------------------------------------------------------

def repair_data(data):

    data.setdefault("true_false", [])
    data.setdefault("fill_blanks", [])
    data.setdefault("mcqs", [])
    data.setdefault("match_general", [])
    data.setdefault("iq_section", [])

    # 🔴 FIX MCQ OPTIONS PROPERLY
    for mcq in data["mcqs"]:

        answer = mcq.get("a", "answer")

        opts = mcq.get("options", [])

        # 🔴 FIX: detect bad options
        if (
            len(opts) < 4 or
            any(o.lower() == "option" for o in opts)
        ):
            opts = generate_smart_options(answer)

        # ensure correct answer exists
        if answer not in opts:
            opts[0] = answer

        random.shuffle(opts)

        mcq["options"] = opts[:4]
def classify_difficulty(sentence):

    l = len(sentence.split())

    if l < 8:
        return "easy"
    elif l < 15:
        return "medium"
    else:
        return "hard"


def tag_difficulty(sentences):

    return [(s, classify_difficulty(s)) for s in sentences]

# ----------------------------------------------------------
# 🧠 CONCEPT GRAPH ENGINE
# ----------------------------------------------------------

def build_concept_graph(sentences):

    graph = {}

    for s in sentences:

        words = s.lower().split()

        for i in range(len(words)-1):

            w1 = words[i]
            w2 = words[i+1]

            if w1 not in graph:
                graph[w1] = []

            graph[w1].append(w2)

    return graph

# ----------------------------------------------------------
# 🎨 MULTI-MODAL ENGINE
# ----------------------------------------------------------

def multimodal_transform(text):

    return {
        "text": text,
        "emoji": parse_text_heavy_emoji(text),
        "length": len(text.split())
    }

# ----------------------------------------------------------
# 🤖 LLM GENERATOR (UPDATED)
# ----------------------------------------------------------

def generate_questions_with_llm(sentences):

    lesson_text = "\n".join(sentences)
    keywords = extract_keywords(sentences)

    prompt = f"""
    STRICT JSON ONLY.

    DO NOT FAIL.

    Generate EXACTLY:

    true_false → 8 items
    fill_blanks → 8 items
    mcqs → 8 items (each must have 4 options)
    match_general → 10 items
    iq_section → 8 items

    FORMAT:

    {{
    "true_false":[{{"q":"question","a":"answer"}}],
    "fill_blanks":[{{"q":"question","a":"answer"}}],
    "mcqs":[{{"q":"question","options":["a","b","c","d"],"a":"correct"}}],
    "match_general":[{{"left":"item","right":"item"}}],
    "iq_section":[{{"type":"logic","question":"question"}}]
    }}

    RULES:
    - Do not return empty lists
    - Do not skip any section
    - Always fill all counts
    - Use very simple English (class 1 level)

    LESSON:
    {lesson_text}

    KEYWORDS:
    {",".join(keywords)}

    RETURN ONLY JSON.
    """

    return self_correct_llm(prompt)

# ----------------------------------------------------------
# 🎮 CHALLENGE ARENA (UNCHANGED)
# ----------------------------------------------------------

def generate_challenge_arena(sentences, keywords):

    treasure = [f"Find meaning of '{k}'" for k in keywords[:3]]

    boss = sentences[0] if sentences else "Explain lesson"

    return {
        "treasure_hunt": treasure,
        "boss_battle": boss,
        "emoji_cipher": [("❓", k) for k in keywords[:3]],
        "word_builder": [(k[:3], k) for k in keywords if len(k)>5][:3],
        "rapid_fire": [f"What is {k}?" for k in keywords[:3]],
        "role_play": "Teach your friend"
    }

# ----------------------------------------------------------
# 🚀 MAIN PIPELINE (UPGRADED)
# ----------------------------------------------------------

def generate_worksheet(text, chapter):

    cleaned = clean_text(text)

    lesson_sentences = extract_lesson_sentences(cleaned)

    if not lesson_sentences:
        raise ValueError("No lesson content")

    keywords = extract_keywords(lesson_sentences)

    # 🔴 NEW COMPONENTS
    difficulty_map = tag_difficulty(lesson_sentences)
    concept_graph = build_concept_graph(lesson_sentences)

    multi_output = [
        multimodal_transform(s)
        for s in lesson_sentences[:5]
    ]

    challenge = generate_challenge_arena(lesson_sentences, keywords)

    data = generate_questions_with_llm(lesson_sentences)

    worksheet = {

        "chapter": chapter,

        "summary_section":{
            "chapter_title": chapter,
            "summary_lines": lesson_sentences[:5],
            "new_words": keywords[:5],
            "difficult_words": difficulty_map[:5]
        },

        "true_false": data.get("true_false",[]),
        "fill_blanks": data.get("fill_blanks",[]),
        "mcqs": data.get("mcqs",[]),
        "match_general": data.get("match_general",[]),
        "iq_section": data.get("iq_section",[]),
        "vocabulary": data.get("vocabulary",[]),

        "concept_graph": concept_graph,          # 🔴 NEW
        "multi_modal": multi_output,             # 🔴 NEW

        "illustration":{
            "drawing":"Draw concept diagram",
            "writing":"Write summary"
        },

        "challenge_arena": challenge,
        "extracted_images":[]
    }

    return worksheet