# DecodeLabs AI Chatbot — Project 1

> Rule-Based O(1) Chatbot + Flan-T5 LLM Fallback | Finance & Healthcare

---

## Project Structure

```
decodelabs-chatbot/
├── app.py            ← Flask backend (rules + Flan-T5 fallback)
├── index.html        ← Frontend (dark/light theme, matches design)
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `torch` + `transformers` are large (~1 GB). If you only want the rule-based bot without the LLM fallback, just install:
> ```bash
> pip install flask flask-cors
> ```

### 2. Run the server
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## Architecture

### Rule Lookup — O(1) with Python dict

```
User query
    │
    ▼
normalise(query)          # lowercase + strip punctuation
    │
    ▼
RULES[query]  ──hit──▶   Return rule response
    │
   miss
    │
    ▼
Flan-T5 LLM fallback ──▶  Return AI response
```

The `RULES` dictionary is a Python `dict` — hash map under the hood.
- Exact match: **O(1)** average
- Partial key scan: O(k) where k = number of keys (small, fixed set)

### Topics Covered

| Category    | Topics |
|-------------|--------|
| Finance     | Stocks, budgeting, investment, mutual funds, tax, crypto, credit score, retirement, loans |
| Healthcare  | Allergies, diabetes, blood pressure, mental health, nutrition, sleep, COVID, first aid, BMI |

---

## Theme Toggle

Click the **moon/sun icon** at the bottom of the sidebar to switch between dark and light themes.

---

## Extending the Bot

Add new rules to the `RULES` dict in `app.py`:

```python
RULES["your trigger phrase"] = "Your response here."
```

Keys are auto-normalised (lowercase, no punctuation), so `"Blood Pressure"` and `"blood pressure"` both match.
