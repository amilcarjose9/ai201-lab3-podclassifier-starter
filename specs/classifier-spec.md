# Classifier Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 2.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `build_few_shot_prompt()` and
`classify_episode()` in `classifier.py`.

---

## build_few_shot_prompt(labeled_examples, description)

### What it does
Constructs a prompt string for the LLM that includes the task instructions,
all labeled training examples, and the new episode description to classify.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `labeled_examples` | `list[dict]` | Each dict has `"title"`, `"description"`, `"label"` (and others). These are the examples you labeled in Milestone 1. |
| `description` | `str` | The episode description to classify. |

### Output

| Return value | Type | Description |
|---|---|---|
| prompt | `str` | A complete prompt string ready to send to the LLM. |

---

### Spec fields — fill these in before writing code

**Task instruction (what should the LLM know about the task?):**

```
You are classifying podcast episodes by their format. Classify the episode
into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion — no guests,
  no assembled external sources
- panel: multiple guests with roughly equal speaking time, often debating or
  discussing a topic together
- narrative: a story assembled from external sources — interviews, archival
  audio, reporting — with a clear narrative arc

Return only the label and your reasoning. Do not explain the taxonomy.
```

---

**How should labeled examples be formatted in the prompt?**

```
Each example should include the episode title, a brief excerpt or the full
description, and the correct label. Separate examples with a blank line or
a delimiter like "---". Include all fields that help the model see why the
label was applied — title and description are both useful; other fields
(like episode ID) are not needed.
```

---

**Example block sketch (write one concrete example):**

```
Title: {title}
Description: {description}
Label: {label}
```

---

**How should the new episode (to be classified) be presented?**

```
Present it in the same format as the labeled examples, but omit the Label
line and replace it with an instruction to classify. For example:

Title: {title}
Description: {description}
Label: ?

Then add a line like: "Classify the episode above. Return your answer in
the format below:" followed by the output format you chose.
```

---

**What output format should you request from the LLM?**

Request the label on the first line by itself, and the reasoning on the subsequent lines.
Example instruction:
"Return your answer exactly in this format:
Line 1: Only the exact label (interview, solo, panel, or narrative)
Line 2+: Your brief reasoning."

---

**Edge cases to handle in the prompt:**

If `labeled_examples` is empty, the prompt should gracefully fall back to a zero-shot prompt (just the instructions and the new description). The loop building the examples should just be skipped.

---

## classify_episode(description, labeled_examples)

### What it does
Classifies a single podcast episode description using the few-shot LLM classifier.
Returns a dict with a label and reasoning.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `description` | `str` | The episode description to classify. |
| `labeled_examples` | `list[dict]` | Labeled training examples from `load_labeled_examples()`. |

### Output

| Return value | Type | Description |
|---|---|---|
| result | `dict` | Must have keys `"label"` and `"reasoning"`. `"label"` must be one of `VALID_LABELS` or `"unknown"`. |

---

### Spec fields — fill these in before writing code

**Step 1 — Build the prompt:**

```
Call build_few_shot_prompt(labeled_examples, description) and store the
returned string in a variable (e.g., prompt). Pass through both arguments
exactly as received — no modification needed before calling.
```

---

**Step 2 — Send to the LLM:**

```
Call _client.chat.completions.create() with:
  - model: the model name from config (LLM_MODEL)
  - messages: a list with one dict — {"role": "user", "content": prompt}
    (system-design.md shows an optional system message too — either shape works)
  - max_tokens: a reasonable limit (e.g., 200–300) to keep responses concise

Extract the response text from:
  response.choices[0].message.content
```

---

**Step 3 — Parse the response:**

1. Split the raw text by newlines: `lines = response_text.strip().split('\n')`.
2. Extract the raw label from the first line: `raw_label = lines[0]`.
3. Extract the reasoning from the rest: `reasoning = '\n'.join(lines[1:]).strip()`.
4. Normalize the label: lowercase it, and strip out common markdown/punctuation like asterisks, colons, or the word "label".

---

**Step 4 — Validate the label:**

Check if the normalized label exists in the VALID_LABELS list. If it does not, set the label variable to the exact string `"unknown"`.

---

**Step 5 — Handle errors gracefully:**

Wrap the API call and parsing logic in a `try...except Exception as e:` block. If anything fails (network timeout, index out of bounds on parsing), catch the exception and return `{"label": "unknown", "reasoning": f"Error during classification: {str(e)}"}`.

---

### Return value structure

```python
{
    "label": str,      # one of VALID_LABELS, or "unknown" if invalid/error
    "reasoning": str,  # brief explanation from the LLM
}
```

---

## Notes on label quality

The classifier is only as good as your labels. If your training examples have
inconsistent or ambiguous labels, the LLM will learn the wrong pattern.

Before implementing the classifier, re-read `data/taxonomy.md` and double-check
any labels you're unsure about. Annotation quality is part of the lab.

---

## Implementation Notes

*Fill this in after implementing and testing both functions.*

**Test: what does the raw LLM response look like for one episode?**

Episode tested: The Orchard That Vanished (t016)
Raw response text: 
**narrative**

Reasoning: The description indicates that the episode follows a reporter (Dani Kim) tracing the chain of ownership of an orchard through various corporate entities. This is an investigative story assembled from external reporting, documents, and a clear narrative arc, which directly matches the criteria for the "narrative" format.

**How did you parse the label out of the response?**

First, I split the response by newline (`\n`). The first line `lines[0]` was `**narrative**`. To parse this reliably, I used regex `re.sub(r'[^a-zA-Z]', '', raw_label).lower().replace("label", "")`. This successfully stripped the asterisks and left only the pure alphabetical string "narrative", which correctly matches our VALID_LABELS list. The reasoning was captured by joining the remaining lines.


**Did any episodes return `"unknown"`? If so, why?**

No. Because of the aggressive regex normalization, there were no `"unknown"` results during standard runs. Before adding the regex step, it sometimes returned `"unknown"` because the model included formatting like `Label: solo` or `**interview**`, which failed a strict `==` equality check against VALID_LABELS.


**One thing about the output format that surprised you:**

Even when explicitly told in the prompt "Line 1: Only the exact label", the LLM still occasionally tries to be helpful by wrapping the label in markdown bold (`**label**`) or prefixing it (`Label: label`). It reinforces the idea that you cannot prompt your way out of formatting quirks—you must build robust string parsing to handle the variations an LLM will inevitably introduce.

