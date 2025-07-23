# CommerceMind-Autonomous-Analytics-Agent-for-Retail-Data
# CommerceMind: Autonomous Analytics Agent for Retail Data

> An AI-powered agent that answers natural language questions about e-commerce data using local LLMs, SQL querying, and visualizations.

---

## 🧠 Project Overview

CommerceMind is a smart AI agent that allows users to query structured e-commerce datasets using plain English questions. It translates the queries into SQL, executes them on local databases, and returns results in both tabular and visual forms.

---

## 📁 Datasets Used

1. **Product-Level Total Sales and Metrics**
2. **Product-Level Ad Sales and Metrics**
3. **Product-Level Eligibility Table**

All datasets are mapped and converted into SQL tables before querying.

---

## 🎯 Objective

- Accept user questions via a web/API interface.
- Translate natural language to SQL queries using a local LLM or LLM API.
- Execute the query on the respective database.
- Return answers in human-readable and optionally visualized formats.
- Bonus: Show results with live-streaming text effect for an interactive feel.

---

## 🛠️ Steps Implemented

### 1. **Data Preparation**
- CSV files loaded into SQLite database.
- Preprocessing handled using Pandas.

### 2. **Local LLM Integration**
- Option 1: Use lightweight local LLMs like `Phi-2`, `Mistral`, or `LLaMA.cpp`.
- Option 2: Use external APIs like [Gemini 2.5](https://aistudio.google.com/apikey) (with key).

### 3. **Query Engine**
- User question ➝ LLM ➝ SQL ➝ Execution ➝ Answer ➝ Display.

### 4. **Frontend**
- Built using **Streamlit** to support:
  - Query input box
  - Answer display
  - SQL query preview
  - Optional graph output using Matplotlib/Seaborn

### 5. **Bonus Features**
- 📊 Visualizations (bar/pie/line charts)
- 📡 Real-time streaming responses (typing effect)

---

## 🚀 Example Questions

> Try asking these:
- What is my total sales?
- Calculate the RoAS (Return on Ad Spend).
- Which product had the highest CPC?

---

## 📦 Tech Stack

| Layer          | Tools / Libraries                     |
|----------------|----------------------------------------|
| Backend        | Python, SQLite, Pandas                |
| AI Model       | Local LLM (Phi-2 / Mistral) OR Gemini |
| Frontend       | Streamlit                             |
| Visualization  | Matplotlib, Seaborn                   |
| API Layer      | FastAPI or Streamlit Endpoints        |

---

## 📁 Project Structure

