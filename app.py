"""
DecodeLabs AI Chatbot — Project 1
Rule-Based O(1) Lookup + Groq LLM Fallback
Finance & Healthcare Focused
"""

from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, re, json, uuid

app = Flask(__name__, static_folder=".")
CORS(app)

# ─────────────────────────────────────────────
#  O(1) RULE BASE  (hashmap / dictionary)
# ─────────────────────────────────────────────
RULES: dict[str, str] = {

    # ── Greetings ──────────────────────────────
    "hello":      "Hello! I'm your DecodeLabs AI assistant. Ask me anything about Finance or Healthcare!",
    "hi":         "Hi there! How can I help you today with Finance or Healthcare?",
    "hey":        "Hey! Ready to help with Finance or Healthcare questions.",
    "good morning":"Good morning! Let's tackle your Finance or Healthcare questions.",
    "good evening":"Good evening! How can I assist you today?",
    "how are you": "I'm running at 100% efficiency! What Finance or Healthcare topic can I help with?",

    # ── Exit commands ──────────────────────────
    "bye":        "Goodbye! Stay healthy and financially savvy!",
    "exit":       "Session ended. Thank you for using DecodeLabs AI!",
    "quit":       "Quitting session. See you next time!",
    "goodbye":    "Take care! Come back anytime for Finance or Healthcare help.",

    # ── FINANCE ───────────────────────────────
    "stock portfolio":
        "📈 To analyse your stock portfolio: diversify across sectors, monitor P/E ratios, "
        "rebalance quarterly, and use index funds as a stable base. Tools: Yahoo Finance, Bloomberg.",

    "analyze my stock portfolio":
        "📊 Portfolio analysis involves: (1) Asset allocation review, (2) Risk vs return ratio, "
        "(3) Sector diversification, (4) Comparing against benchmark indices like S&P 500.",

    "budgeting tips":
        "💰 Top budgeting tips: Follow the 50/30/20 rule (needs/wants/savings), "
        "track every expense, build a 3–6 month emergency fund, and automate savings.",

    "budgeting tips for savings":
        "💳 Savings-focused budgeting: (1) Pay yourself first, (2) Cut subscriptions you don't use, "
        "(3) Use high-yield savings accounts, (4) Set specific savings goals with deadlines.",

    "investment":
        "📉 Investment basics: Start early for compound interest benefits, diversify assets "
        "(stocks, bonds, real estate), understand risk tolerance, and avoid emotional trading.",

    "mutual funds":
        "🏦 Mutual funds pool investor money to buy diversified assets. Key metrics: expense ratio "
        "(keep <1%), NAV, fund manager track record, and exit load policies.",

    "tax":
        "🧾 Tax planning tips: Maximise deductions, contribute to tax-advantaged accounts (401k/IRA), "
        "keep records of expenses, and consult a CPA for complex situations.",

    "cryptocurrency":
        "₿ Crypto is highly volatile. Only invest what you can afford to lose. "
        "Research the project's whitepaper, use cold wallets for storage, and diversify.",

    "insurance":
        "🛡️ Insurance essentials: Term life > whole life for most people. "
        "Ensure health, auto, home, and disability coverage. Compare premiums vs deductibles.",

    "health insurance":
        "🏥 Health insurance plans: HMO (lower cost, in-network only), PPO (flexible, higher cost), "
        "HDHP (high deductible + HSA eligible). Check copay, deductible, and out-of-pocket max.",

    "explain health insurance plans":
        "📋 Health Insurance types:\n• HMO – requires referrals, lower premiums\n"
        "• PPO – no referrals, broader network, higher cost\n"
        "• EPO – in-network only, no referrals\n"
        "• HDHP – high deductible, pairs with an HSA for tax savings.",

    "loan":
        "🏛️ Loan advice: Compare APR (not just interest rate), check prepayment penalties, "
        "maintain a credit score >750 for best rates, and avoid payday loans.",

    "credit score":
        "💳 Improve your credit score: Pay bills on time (35% of score), keep utilisation <30%, "
        "don't close old accounts, and limit hard inquiries.",

    "retirement":
        "🌅 Retirement planning: Start at 25 not 45! Contribute max to 401(k) to get employer match, "
        "open a Roth IRA, target 25× your annual expenses as your retirement corpus.",

    # ── HEALTHCARE ─────────────────────────────
    "symptoms of seasonal allergies":
        "🌿 Seasonal allergy symptoms: sneezing, runny/stuffy nose, itchy/watery eyes, "
        "postnasal drip, and fatigue. Triggers: pollen, mold, dust. Treatment: antihistamines, nasal sprays.",

    "allergy":
        "🤧 Allergies occur when the immune system overreacts to a substance. "
        "Common triggers: pollen, pet dander, food, insect stings. See an allergist for testing.",

    "diabetes":
        "🩺 Diabetes management: Monitor blood glucose regularly, follow a low-GI diet, "
        "exercise 150 min/week, take medications as prescribed, and get A1C checked every 3 months.",

    "blood pressure":
        "❤️ Healthy BP is <120/80 mmHg. To lower BP: reduce sodium, exercise regularly, "
        "limit alcohol, manage stress, and take prescribed medications consistently.",

    "mental health":
        "🧠 Mental health matters! Practice: daily mindfulness (10 min), regular sleep schedule, "
        "social connection, and seek professional help if feelings persist >2 weeks.",

    "depression":
        "💙 Depression signs: persistent sadness, loss of interest, sleep changes, fatigue. "
        "Treatment: therapy (CBT), medication (SSRIs), lifestyle changes. Please seek professional help.",

    "anxiety":
        "🫁 Managing anxiety: deep breathing (4-7-8 technique), grounding exercises, "
        "limit caffeine, regular exercise, and cognitive behavioural therapy (CBT).",

    "nutrition":
        "🥦 Nutrition basics: 50% vegetables/fruits, 25% lean protein, 25% whole grains. "
        "Limit processed foods, sugar, and trans fats. Stay hydrated — 8 glasses/day.",

    "exercise":
        "🏃 WHO recommends: 150 min moderate or 75 min vigorous cardio/week + strength training 2×/week. "
        "Even a 30-min daily walk significantly improves cardiovascular health.",

    "sleep":
        "😴 Sleep hygiene: 7–9 hours for adults. Stick to a consistent schedule, "
        "avoid screens 1 hr before bed, keep room cool & dark, limit caffeine after 2 PM.",

    "covid":
        "🦠 COVID-19: Stay up-to-date on vaccinations, wear masks in crowded indoor spaces if at risk, "
        "isolate if symptomatic, and follow local health authority guidelines.",

    "fever":
        "🌡️ Fever >38°C (100.4°F): Rest, hydrate well, take paracetamol/ibuprofen for comfort. "
        "Seek medical care if >39.5°C, lasts >3 days, or accompanied by severe symptoms.",

    "headache":
        "💊 Headache relief: Stay hydrated, rest in a quiet dark room, apply cold/warm compress. "
        "Frequent migraines may need prescription treatment — consult a neurologist.",

    "first aid":
        "🚑 Basic first aid: RICE for sprains (Rest, Ice, Compression, Elevation). "
        "For cuts: clean, apply pressure, bandage. For burns: cool water 10 min, do NOT use ice.",

    "bmi":
        "⚖️ BMI = weight(kg) / height(m)². Ranges: Underweight <18.5, Normal 18.5–24.9, "
        "Overweight 25–29.9, Obese ≥30. BMI is a screening tool, not a diagnostic measure.",
}


# ─────────────────────────────────────────────
#  HISTORY — persistent JSON storage
# ─────────────────────────────────────────────
HISTORY_FILE = "chat_history.json"

current_session: dict = {"id": None, "title": None, "messages": []}


def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_session() -> None:
    if not current_session["messages"]:
        return
    all_chats = load_history()
    all_chats[current_session["id"]] = {
        "title":    current_session["title"],
        "messages": current_session["messages"],
    }
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_chats, f, indent=2)


def generate_title(first_message: str) -> str:
    """Ask Groq to produce a clean 3-5 word topic title."""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a short 3-5 word title that captures the topic of this message. "
                        "Return ONLY the title — no quotes, no punctuation, no explanation."
                    ),
                },
                {"role": "user", "content": first_message},
            ],
            max_tokens=15,
        )
        return resp.choices[0].message.content.strip().strip('"').strip("'")
    except Exception:
        words = first_message.strip().split()
        return " ".join(words[:4]).capitalize()


# ─────────────────────────────────────────────
#  NORMALISER
# ─────────────────────────────────────────────
def normalise(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


# ─────────────────────────────────────────────
#  O(1) LOOKUP
# ─────────────────────────────────────────────
def rule_lookup(query: str):
    q = normalise(query)
    if q in RULES:
        return RULES[q]
    for key, response in RULES.items():
        if key in q or q in key:
            return response
    return None


# ─────────────────────────────────────────────
#  Groq FALLBACK
# ─────────────────────────────────────────────
def llm_fallback(query: str, history: list = []) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Build messages: system prompt + last 6 messages for context + current query
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant specialised in Finance and Healthcare. "
                    "Answer concisely in 2-3 sentences. "
                    "Use the conversation history to understand pronouns like 'it', 'that', or 'this' "
                    "and resolve them to the topic being discussed. "
                    "If the question is unrelated to Finance or Healthcare, "
                    "politely say you only cover those topics."
                )
            }
        ]

        # Inject last 6 messages as context (3 exchanges)
        for msg in history[-6:]:
            messages.append({"role": "user",      "content": msg["user"]})
            messages.append({"role": "assistant",  "content": msg["bot"]})

        # Add the current query
        messages.append({"role": "user", "content": query})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=300,
        )

        return "🤖 (AI) " + response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Groq fallback error: {str(e)}"


# ─────────────────────────────────────────────
#  API ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global current_session
    data  = request.get_json(force=True)
    query = data.get("message", "").strip()

    if not query:
        return jsonify({"response": "Please type a message!", "source": "rule"})

    if current_session["id"] is None:
        current_session["id"] = str(uuid.uuid4())

    rule_response = rule_lookup(query)
    if rule_response:
        response = rule_response
        source   = "rule"
    else:
        # Pass session history so Groq understands "it", "that", "this"
        response = llm_fallback(query, history=current_session["messages"])
        source   = "llm"

    if current_session["title"] is None:
        current_session["title"] = generate_title(query)

    current_session["messages"].append({"user": query, "bot": response})
    save_session()

    return jsonify({"response": response, "source": source})


@app.route("/new_chat", methods=["POST"])
def new_chat():
    global current_session
    save_session()
    current_session = {"id": str(uuid.uuid4()), "title": None, "messages": []}
    return jsonify({"status": "ok"})


@app.route("/history", methods=["GET"])
def get_history():
    all_chats = load_history()
    result = [{"id": cid, "title": data["title"]} for cid, data in all_chats.items()]
    return jsonify(result)


@app.route("/history/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    all_chats = load_history()
    if chat_id in all_chats:
        return jsonify(all_chats[chat_id])
    return jsonify({"error": "Chat not found"}), 404


@app.route("/suggestions", methods=["GET"])
def suggestions():
    return jsonify([
        {"icon": "chart-line",  "text": "Analyze my stock portfolio"},
        {"icon": "heart-pulse", "text": "Explain health insurance plans"},
        {"icon": "piggy-bank",  "text": "Budgeting tips for savings"},
        {"icon": "leaf",        "text": "Symptoms of seasonal allergies"},
    ])


if __name__ == "__main__":
    print("🚀 DecodeLabs Chatbot running on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
