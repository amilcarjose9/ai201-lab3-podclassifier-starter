# Evaluation Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 3.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `compute_accuracy()` and
`compute_per_class_accuracy()` in `evaluate.py`.

---

## Background: What is evaluation?

After building a classifier, we need to know how well it works. Evaluation answers:
- **Overall:** What fraction of episodes did we classify correctly?
- **Per-class:** Are we better at some labels than others?

Both functions take the same inputs: a list of predicted labels and a list of
ground-truth labels, in the same order.

---

## compute_accuracy(predictions, ground_truth)

### What it does
Returns the fraction of predictions that exactly match the ground truth.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`, one per episode. |
| `ground_truth` | `list[str]` | The correct labels, in the same order as `predictions`. |

### Output

| Return value | Type | Description |
|---|---|---|
| accuracy | `float` | A value between 0.0 and 1.0. |

---

### Spec fields — fill these in before writing code

**Formula:**

Accuracy is the total number of correct predictions divided by the total number of predictions made. A prediction is considered correct if the predicted string exactly matches the ground truth string for that specific episode.

---

**Step-by-step logic:**

1. Check if the `ground_truth` list is empty. If it is, return 0.0.
2. Initialize a counter for correct predictions to 0.
3. Loop through both lists simultaneously (e.g., using `zip(predictions, ground_truth)`).
4. For each pair, check if predicted == truth. If so, increment the correct counter by 1.
5. Return the correct counter divided by the length of the ground_truth list.

---

**Edge case — what if both lists are empty?**

The function should return 0.0. If the lists are empty, dividing by the length of ground_truth (0) will cause a ZeroDivisionError. Returning 0.0 gracefully handles the case where there is no test data.

---

**Worked example:**

predictions  = ["interview", "solo", "panel", "interview"]
ground_truth = ["interview", "solo", "solo",  "narrative"]

- Index 0: "interview" == "interview" (Correct)
- Index 1: "solo" == "solo" (Correct)
- Index 2: "panel" != "solo" (Incorrect)
- Index 3: "interview" != "narrative" (Incorrect)

Total correct: 2
Total episodes: 4
Accuracy: 2 / 4 = 0.5 (50% accuracy)

---

## compute_per_class_accuracy(predictions, ground_truth)

### What it does
Returns accuracy broken down by each label. For each label in `VALID_LABELS`,
reports how many episodes with that ground-truth label were classified correctly.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`. |
| `ground_truth` | `list[str]` | Correct labels, in the same order. |

### Output

A `dict` keyed by label. Each value is a dict with three keys:

```python
{
    "interview": {"correct": int, "total": int, "accuracy": float},
    "solo":      {"correct": int, "total": int, "accuracy": float},
    "panel":     {"correct": int, "total": int, "accuracy": float},
    "narrative": {"correct": int, "total": int, "accuracy": float},
}
```

---

### Spec fields — fill these in before writing code

**What does "correct" mean for a given class?**

An episode counts as correctly classified for a class (e.g., "interview") if its label in ground_truth is "interview", AND its label in predictions is also exactly "interview".

---

**What does "total" mean for a given class?**

"Total" means the total number of episodes in the *ground_truth* list that actually belong to that class. It represents the true volume of that class in the test set, regardless of what the classifier predicted.

---

**Step-by-step logic:**

1. Initialize a dictionary with a key for each label in VALID_LABELS, setting "correct": 0, "total": 0, and "accuracy": 0.0 for each.
2. Loop over the predictions and ground_truth lists simultaneously using `zip`.
3. For each pair (predicted, truth), increment the "total" count for the `truth` label by 1.
4. If predicted == truth, also increment the "correct" count for the `truth` label by 1.
5. After the loop finishes, iterate through the dictionary values. If "total" > 0, calculate "accuracy" = "correct" / "total".
6. Return the dictionary.

---

**Edge case — what if a class has no examples in ground_truth (total == 0)?**

Accuracy should be set to 0.0. Attempting to divide "correct" by 0 "total" examples will cause a ZeroDivisionError. Defaulting to 0.0 is safe and accurate, as you cannot successfully predict any instances of a class that does not exist in the test set.

---

**Worked example:**

predictions  = ["interview", "interview", "solo", "panel", "panel"]
ground_truth = ["interview", "solo",      "solo", "panel", "narrative"]

label       correct  total  accuracy
----------  -------  -----  --------
interview   1        1      1.0
solo        1        2      0.5
panel       1        1      1.0
narrative   0        1      0.0


---

## Reflection questions (discuss at the checkpoint)

1. Your overall accuracy might be decent even if one class has very low accuracy.
   Why is per-class accuracy a more informative metric than overall accuracy alone?

2. If `panel` episodes consistently get misclassified as `interview`, what does
   that tell you about your training labels or your prompt?

3. You labeled 20 training episodes and evaluated on 20 test episodes (5 per class).
   How might the evaluation results change if you had labeled 100 training episodes?
   What if you had 200 test episodes?
