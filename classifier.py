import json
import os
import re
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_LABELS, DATA_PATH, TRAIN_FILE, LABELS_FILE

_client = Groq(api_key=GROQ_API_KEY)


def load_labeled_examples() -> list[dict]:
    """
    Load the training episodes and merge them with the student's labels.
    """
    train_path = os.path.join(DATA_PATH, TRAIN_FILE)
    labels_path = os.path.join(DATA_PATH, LABELS_FILE)

    with open(train_path, encoding="utf-8") as f:
        episodes = {ep["id"]: ep for ep in json.load(f)}

    with open(labels_path, encoding="utf-8") as f:
        labels = {entry["id"]: entry["label"] for entry in json.load(f)}

    labeled = []
    for ep_id, ep in episodes.items():
        label = labels.get(ep_id)
        if label in VALID_LABELS:
            labeled.append({**ep, "label": label})

    return labeled


def build_few_shot_prompt(labeled_examples: list[dict], description: str) -> str:
    """
    Build a few-shot classification prompt using the student's labeled training examples.
    """
    prompt_parts = [
        "You are classifying podcast episodes by their format. Classify the episode into exactly one of these four labels:",
        "",
        "- interview: a conversation between a host and one or more guests",
        "- solo: a single host speaking from memory, experience, or opinion — no guests, no assembled external sources",
        "- panel: multiple guests with roughly equal speaking time, often debating or discussing a topic together",
        "- narrative: a story assembled from external sources — interviews, archival audio, reporting — with a clear narrative arc",
        "",
        "Here are some examples of correctly labeled episodes:",
        "---"
    ]

    # 1. Add the few-shot examples
    for ex in labeled_examples:
        prompt_parts.extend([
            f"Title: {ex['title']}",
            f"Description: {ex['description']}",
            f"Label: {ex['label']}",
            "---"
        ])

    # 2. Add the target description
    prompt_parts.extend([
        "Now, classify this new episode:",
        f"Description: {description}",
        "---",
        "Return your answer exactly in this format:",
        "Line 1: Only the exact label (interview, solo, panel, or narrative)",
        "Line 2+: Your brief reasoning."
    ])

    return "\n".join(prompt_parts)


def classify_episode(description: str, labeled_examples: list[dict]) -> dict:
    """
    Classify a single podcast episode description using the few-shot LLM classifier.
    """
    prompt = build_few_shot_prompt(labeled_examples, description)

    try:
        # 1. Send to the LLM
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise podcast classification assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.1 # Low temperature for more consistent formatting
        )
        
        response_text = response.choices[0].message.content
        
        # Tip: Uncomment the line below during testing if you get high 'unknown' rates
        # print(f"RAW RESPONSE:\n{response_text}\n---")

        # 2. Parse the response
        lines = response_text.strip().split('\n')
        if not lines:
            raise ValueError("Empty response from LLM")
            
        raw_label = lines[0]
        reasoning = '\n'.join(lines[1:]).strip() if len(lines) > 1 else "No reasoning provided."

        # 3. Normalize the label (strip formatting, punctuation, and lowercase it)
        # Removes markdown asterisks, "Label:", spaces, etc.
        clean_label = re.sub(r'[^a-zA-Z]', '', raw_label).lower()
        clean_label = clean_label.replace("label", "") # In case it returned "Label: interview"

        # 4. Validate
        if clean_label not in VALID_LABELS:
            clean_label = "unknown"

        return {
            "label": clean_label,
            "reasoning": reasoning
        }

    except Exception as e:
        # 5. Handle errors gracefully
        return {
            "label": "unknown",
            "reasoning": f"Error during classification: {str(e)}"
        }
