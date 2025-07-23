from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection
from llm import generate_sql_from_question, extract_sql_from_llm_output

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "E-commerce AI Agent is running."}

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"error": "No question provided."}
    # Step 1: Use LLM to generate SQL
    sql_query = generate_sql_from_question(question)
    if not sql_query:
        return {"error": "Failed to generate SQL from question."}
    # Clean the SQL query
    sql_query = extract_sql_from_llm_output(sql_query)
    # Step 2: Run SQL on DB
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed."}
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        return {"sql": sql_query, "results": results}
    except Exception as e:
        return {"error": str(e), "sql": sql_query}