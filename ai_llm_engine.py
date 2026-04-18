# ==========================================================
# AI LLM ENGINE (SELF-CORRECTING + VALIDATED)
# ==========================================================

import ollama
import json
import re

MODEL = "llama3"

# ----------------------------------------------------------
# 🔴 VALIDATION ENGINE
# ----------------------------------------------------------

def validate_structure(data):

    required_keys = [
        "chapter",
        "true_false",
        "fill_blanks",
        "mcqs",
        "match",
        "iq"
    ]

    for key in required_keys:
        if key not in data:
            return False

    # minimum checks
    if len(data["true_false"]) == 0:
        return False

    if len(data["fill_blanks"]) == 0:
        return False

    if len(data["mcqs"]) == 0:
        return False

    if len(data["iq"]) == 0:
        return False

    # MCQ strict check
    for mcq in data["mcqs"]:
        if len(mcq.get("options", [])) != 4:
            return False

    return True


# ----------------------------------------------------------
# 🔁 AUTO REPAIR ENGINE
# ----------------------------------------------------------

def repair_data(data):

    data.setdefault("true_false", [])
    data.setdefault("fill_blanks", [])
    data.setdefault("mcqs", [])
    data.setdefault("match", [])
    data.setdefault("iq", [])

    # fix MCQ options
    for mcq in data["mcqs"]:
        opts = mcq.get("options", [])

        while len(opts) < 4:
            opts.append("Option")

        mcq["options"] = opts[:4]

    return data


# ----------------------------------------------------------
# 🧠 SELF-CORRECTING LLM CALL
# ----------------------------------------------------------

def self_correct_generation(prompt, max_attempts=3):

    for attempt in range(max_attempts):

        response = ollama.chat(
            model=MODEL,
            format="json",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )

        content = response["message"]["content"]

        # Extract JSON
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            prompt += "\nReturn ONLY valid JSON. Fix formatting."
            continue

        json_str = match.group()

        try:
            data = json.loads(json_str)
        except:
            prompt += "\nFix invalid JSON structure."
            continue

        # repair first
        data = repair_data(data)

        # validate
        if validate_structure(data):
            return data

        # 🔴 SELF-CORRECTION LOOP
        prompt += "\nYour previous output failed validation. Fix all constraints exactly."

    raise ValueError("LLM failed after multiple attempts")


# ----------------------------------------------------------
# 🚀 MAIN FUNCTION
# ----------------------------------------------------------

def generate_ai_learning_kit(text, chapter):

    prompt = f"""
STRICT JSON ONLY.

Return ONLY valid JSON.

FORMAT:

{{
"chapter":"{chapter}",
"true_false":[{{"q":"", "a":""}}],
"fill_blanks":[{{"q":"", "a":""}}],
"mcqs":[{{"q":"", "options":["","","",""], "a":""}}],
"match":[{{"left":"","right":""}}],
"iq":[{{"type":"","question":""}}]
}}

RULES:
- No extra text
- No explanation
- No markdown
- Only JSON
- MCQ must have exactly 4 options

LESSON:
{text}
"""

    data = self_correct_generation(prompt)

    return data