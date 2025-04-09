import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.express as px

# ==== CONFIGURATION ====
GEMINI_API_KEY = "AIzaSyDL2k9_deJ-3Cs0AVB57PqjHZjtHoEvvZo"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# ==== LOAD NAYAPAY CSV ====
def load_nayapay_csv(uploaded_file):
    lines = uploaded_file.getvalue().decode("utf-8").splitlines()
    start_line = None
    for i, line in enumerate(lines):
        if "TIMESTAMP" in line and "DESCRIPTION" in line:
            start_line = i
            break

    if start_line is None:
        raise ValueError("Could not find transaction data.")

    df = pd.read_csv(uploaded_file, skiprows=start_line)
    return df

# ==== GEMINI SUBSCRIPTION DETECTOR ====
def detect_subscriptions_using_gemini(df):
    csv_data = df.to_csv(index=False)

    prompt = f"""
    Analyze the following CSV data from a NayaPay bank statement and identify recurring subscriptions.
    For each recurring subscription, return the following in JSON format:
    - description
    - amount
    - last_paid (most recent transaction date)
    - next_estimated_payment (assume monthly recurrence)

    Respond ONLY with a JSON array like:
    [
        {{
            "description": "Netflix",
            "amount": "1500",
            "last_paid": "2025-03-10",
            "next_estimated_payment": "2025-04-10"
        }},
        ...
    ]

    CSV Data:
    {csv_data}
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        subscription_data = json.loads(text)
        return subscription_data
    except Exception as e:
        raise Exception(f"Could not parse Gemini response:\n{text}\n\nError: {str(e)}")

# ==== SUGGESTIONS ====
def generate_saving_suggestions(subscription_data):
    return [
        f"\U0001F4B8 You are paying {item['amount']} for: {item['description']}."
        for item in subscription_data
    ]

def suggest_alternatives_with_gemini(subscription_data):
    prompt = f"""
You are a smart assistant suggesting cheaper or free alternatives to paid subscription services.

For each subscription below, suggest a cheaper or free alternative with a short explanation.
Respond in the following JSON format:
[
  {{
    "description": "Spotify",
    "amount": "1500",
    "suggestion": "Use YouTube Music Free with ads."
  }},
  ...
]

Subscriptions:
{json.dumps(subscription_data, indent=2)}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        suggestions_json = json.loads(text)
        return [f"\U0001F4A1 You pay PKR {item['amount']} for **{item['description']}**. {item['suggestion']}" for item in suggestions_json]
    except Exception as e:
        raise Exception(f"Could not parse Gemini response:\n{text}\n\nError: {str(e)}")

# ==== REMINDER MESSAGE ====
def generate_reminder_messages_with_alternatives(subscription_data):
    prompt = f"""
You are a financial assistant. Given the user's subscriptions, generate reminder messages with expected payment dates and include a suggestion for a cheaper or free alternative if applicable.

Output a JSON list in the format:
[
  {{
    "description": "Spotify",
    "amount": "1500",
    "next_estimated_payment": "2025-04-07",
    "reminder": "\U0001F514 Reminder: Your Spotify subscription (PKR 1500) is expected around 2025-04-07.",
  }},
  ...
]

Data:
{json.dumps(subscription_data, indent=2)}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        reminder_data = json.loads(text)
        return [item["reminder"] + "\n" + item.get("suggestion", "") for item in reminder_data]
    except Exception as e:
        raise Exception(f"Could not parse Gemini response:\n{text}\n\nError: {str(e)}")

# ==== CHATBOT: AI Q&A ====
def chat_with_gemini_about_data(subscription_data, user_question):
    prompt = f"""
You are a smart financial assistant helping users analyze their subscription payments from a NayaPay statement.

Below is a list of subscriptions, each with:
- description
- amount
- last_paid (most recent payment date)
- next_estimated_payment (automatically assumed to recur monthly)

When the user asks about future payment dates (like "when is Spotify due in May 2025"), calculate it based on the last_paid date by adding 1 month for each cycle.

Respond conversationally and provide helpful answers.

Subscription data:
{json.dumps(subscription_data, indent=2)}

User question:
{user_question}

Answer:
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

# ==== VISUALIZATION ====
def plot_monthly_subscription_costs(subscription_data):
    df = pd.DataFrame(subscription_data)
    df['last_paid'] = pd.to_datetime(df['last_paid'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    monthly_costs = df.groupby(df['last_paid'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly_costs['last_paid'] = monthly_costs['last_paid'].astype(str)
    st.subheader("\U0001F4CA Monthly Subscription Costs")
    st.bar_chart(monthly_costs.set_index('last_paid'))

def plot_subscription_pie_chart(subscription_data):
    df = pd.DataFrame(subscription_data)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    st.subheader("\U0001F967 Spending by Subscription")
    fig, ax = plt.subplots()
    ax.pie(df['amount'], labels=df['description'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

def plot_subscription_timeline(subscription_data):
    df = pd.DataFrame(subscription_data)
    df['last_paid'] = pd.to_datetime(df['last_paid'])
    df['next_estimated_payment'] = pd.to_datetime(df['next_estimated_payment'], errors='coerce')
    st.subheader("\U0001F4C5 Subscription Timeline")
    fig = px.timeline(df, x_start="last_paid", x_end="next_estimated_payment", y="description", title="Subscription Periods")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig)

# ==== STREAMLIT UI ====
st.set_page_config(page_title="Subscription Detector", layout="centered")
st.title("\U0001F4B3 Subscription Detector")
st.markdown("Upload your **Bank CSV statement** to detect subscriptions using AI and get saving + reminder tips \U0001F4A1")

uploaded_file = st.file_uploader("\U0001F4C1 Upload your bank monthly statement (CSV)", type="csv")

if uploaded_file is not None:
    try:
        df = load_nayapay_csv(uploaded_file)
        st.success("\u2705 File uploaded and parsed successfully.")

        with st.spinner("\U0001F50D Detecting subscriptions using Gemini..."):
            subscription_data = detect_subscriptions_using_gemini(df)

        if not subscription_data:
            st.success("\U0001F389 No subscriptions found.")
        else:
            st.subheader("\U0001F50D Subscriptions Detected:")
            subscriptions_df = pd.DataFrame(subscription_data)
            st.table(subscriptions_df)

            st.subheader("\U0001F4C9 Suggestions to Save Money:")
            for suggestion in generate_saving_suggestions(subscription_data):
                st.write("- " + suggestion)

            st.subheader("\U0001F4C5 Upcoming Subscription Reminders:")
            for msg in generate_reminder_messages_with_alternatives(subscription_data):
                st.markdown("- " + msg)

            with st.expander("\U0001F4A1 Cheaper Alternatives"):
                for alt in suggest_alternatives_with_gemini(subscription_data):
                    st.write("- " + alt)

            with st.expander("\U0001F4E7 Simulate Email Reminder"):
                recipient = st.text_input("Enter your email address")
                if st.button("Send Reminder Email"):
                    if recipient:
                        reminder_text = "\n".join(generate_reminder_messages_with_alternatives(subscription_data))
                        st.info(f"\U0001F4E8 Email would be sent to: {recipient}")
                        st.code(reminder_text, language='text')
                    else:
                        st.warning("\u26A0\uFE0F Please enter an email address.")

            with st.expander("\U0001F4CA View Data Visualizations"):
                plot_monthly_subscription_costs(subscription_data)
                plot_subscription_pie_chart(subscription_data)
                plot_subscription_timeline(subscription_data)

            with st.expander("\U0001F916 Ask the AI Assistant"):
                user_question = st.text_input("Ask about your subscriptions (e.g., 'How much in January?')")
                if user_question:
                    answer = chat_with_gemini_about_data(subscription_data, user_question)
                    st.markdown(f"**\U0001F9E0 Answer:** {answer}")

    except Exception as e:
        st.error(f"\u274C An error occurred: {str(e)}")
