from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import re

app = FastAPI()

class AIQueryRequest(BaseModel):
    sql_query: str

# checking query safty
def is_safe_select_query(query: str) -> bool:
    clean_query = query.strip().upper()
    
    if not clean_query.startswith("SELECT"):
        return False
    
    if ";" in clean_query[:-1]:
        return False

    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "EXEC"]
    for word in forbidden_keywords:
        if re.search(rf"\b{word}\b", clean_query):
            return False
            
    return True

@app.post("/execute-ai-query")
def execute_ai_query(request: AIQueryRequest):
    sql = request.sql_query
    
    if not is_safe_select_query(sql):
        raise HTTPException(status_code=403, detail= "error! you can just use SELECT query requests")
    
    try:

        conn = sqlite3.connect("file:sales_db.db?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        cursor.execute(sql)
        rows = cursor.fetchall()
        
        result = [dict(row) for row in rows]
        
        return {
            "status": "success",
            "executed_query": sql,
            "row_count": len(result),
            "data": result
        }
        
    except sqlite3.Error as db_error:
        
        raise HTTPException(
            status_code=400, 
            detail=f"خطا در اجرای کوئری SQL: {str(db_error)}"
        )
    finally:
        if 'conn' in locals():
            conn.close()