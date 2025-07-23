import requests
import re

GOOGLE_API_KEY = "AIzaSyAV90i7OZlTxyRyTkIZO4fISYCN-9F_nuQ"
MODEL_NAME = "gemini-2.5-pro"

SQL_PROMPT_TEMPLATE = """
You are a helpful assistant that generates SQL queries based on natural language questions.
The database has the following tables and columns:
- product_level_adsales (date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
- product_level_eligibility (eligibility_datetime_utc, item_id, eligibility, message)
- product_level_totalsales (date, item_id, total_sales, total_units_ordered)

Question: {question}

SQL:
"""

def call_google_llm(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, params={"key": GOOGLE_API_KEY}, json=payload)

    print("[DEBUG] LLM API status:", response.status_code)
    print("[DEBUG] LLM API response text:", response.text)

    if response.status_code != 200:
        try:
            print("\nLLM API error:", response.json())
        except Exception:
            print("Failed to decode error JSON")
        return ""

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Error parsing LLM response:", e)
        return ""

def generate_sql_from_question(question: str) -> str:
    prompt = SQL_PROMPT_TEMPLATE.format(question=question)
    response = call_google_llm(prompt)
    print("[DEBUG] LLM raw response:", repr(response))
    return response.strip()

def extract_sql_from_llm_output(llm_output: str) -> str:
    """
    Extracts the first SQL statement from the LLM output, removing code block markers and extra text.
    """
    # Remove code block markers
    llm_output = re.sub(r"sql|", "", llm_output, flags=re.IGNORECASE).strip()
    # Remove any leading 'sql' or explanations
    llm_output = re.sub(r"^sql\s*", "", llm_output, flags=re.IGNORECASE)
    # Find the first SQL statement (ends with ;)
    match = re.search(r"(SELECT[\s\S]+?;)", llm_output, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: return the cleaned output
    return llm_output.strip()