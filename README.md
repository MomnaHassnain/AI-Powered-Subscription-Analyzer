# AI-Powered-Subscription-Analyzer

This is a Streamlit app that helps users analyze their **bank statements** (e.g., from NayaPay) to automatically detect recurring **subscriptions** using **Gemini AI**
(Google Generative AI). It provides **money-saving suggestions**, **cheaper alternatives**, **reminder messages**, and **beautiful visualizations** of your spending.

---

## ✨ Features

- 🔍 **Subscription Detection**: Automatically identify recurring payments from uploaded CSV.
- 💡 **Suggestions to Save**: Understand what subscriptions you’re paying for and get helpful tips to reduce costs.
- 🧠 **AI-Powered Alternatives**: Gemini AI suggests free or cheaper alternatives to your current services.
- 🔔 **Reminder Messages**: Get personalized messages for upcoming payments with expected dates.
- 📊 **Data Visualizations**:
  - Monthly subscription cost trends
  - Spending by service (pie chart)
  - Timeline of payments
- 🤖 **Chat with AI Assistant**: Ask natural language questions like “How much did I spend in January?” or “When is Netflix due next?”
- 📧 **Simulated Email Reminder**: Preview email messages for future payments.

---

## 📁 File Upload Requirements

- Upload your **CSV bank statement**.
- The file must include at least the following columns:
  - `TIMESTAMP`
  - `DESCRIPTION`
  - `AMOUNT`

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/subscription-detector.git
cd subscription-detector


. Run the app

streamlit run app.py
