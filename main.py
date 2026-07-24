import os
import sqlite3
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse
from init_db import init_db

app = FastAPI()

# יצירת הטבלאות והנתונים בעליית השרת
@app.on_event("startup")
def startup_event():
    init_db()

def get_db():
    try:
        conn = sqlite3.connect('clalit.db')
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# הגשת עמוד הבית
@app.get("/")
def read_root():
    return FileResponse("index.html")

# הגשת קובץ העיצוב (תמיכה בכל הנתיבים האפשריים)
@app.get("/style.css")
@app.get("/static/style.css")
def get_css():
    return FileResponse("style.css", media_type="text/css")

# הגשת קובץ ה-JS (תמיכה בכל הנתיבים האפשריים)
@app.get("/app.js")
@app.get("/static/app.js")
def get_js():
    return FileResponse("app.js", media_type="application/javascript")

# שליפת לקוחות עבור השדה הנגלל בטופס
@app.get("/api/customers")
def get_customers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_id, (first_name || ' ' || last_name) AS full_name, id_number FROM customers WHERE status = 'פעיל'"
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"customer_id": r[0], "full_name": r[1], "id_number": r[2]} for r in rows]

# שליפת תורים להצגה בטבלה
@app.get("/api/appointments")
def get_appointments():
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT a.appointment_id, a.customer_id, (c.first_name || ' ' || c.last_name) AS customer_name,
               a.doctor_name, a.specialization, a.clinic_name, 
               a.appointment_date,
               a.appointment_time,
               a.appointment_type, a.status, COALESCE(a.notes, '')
        FROM appointments a
        JOIN customers c ON a.customer_id = c.customer_id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [{
        "appointment_id": r[0],
        "customer_id": r[1],
        "customer_name": r[2],
        "doctor_name": r[3],
        "specialization": r[4],
        "clinic_name": r[5],
        "appointment_date": r[6],
        "appointment_time": r[7],
        "appointment_type": r[8],
        "status": r[9],
        "notes": r[10]
    } for r in rows]

# יצירת תור חדש
@app.post("/api/appointments")
def create_appointment(
        customer_id: int = Form(...),
        doctor_name: str = Form(...),
        specialization: str = Form(...),
        clinic_name: str = Form(...),
        appointment_date: str = Form(...),
        appointment_time: str = Form(...),
        appointment_type: str = Form(...),
        notes: str = Form("")
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments 
        (customer_id, doctor_name, specialization, clinic_name, appointment_date, appointment_time, appointment_type, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, doctor_name, specialization, clinic_name, appointment_date, appointment_time, appointment_type, notes))
    conn.commit()
    conn.close()
    return {"message": "התור נקבע בהצלחה!"}

# עדכון תור קיים
@app.put("/api/appointments/{appointment_id}")
def update_appointment(
        appointment_id: int,
        doctor_name: str = Form(...),
        specialization: str = Form(...),
        clinic_name: str = Form(...),
        appointment_date: str = Form(...),
        appointment_time: str = Form(...),
        appointment_type: str = Form(...),
        notes: str = Form("")
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments
        SET doctor_name = ?, specialization = ?, clinic_name = ?, appointment_date = ?, 
            appointment_time = ?, appointment_type = ?, notes = ?, status = 'עודכן', updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ?
    """, (doctor_name, specialization, clinic_name, appointment_date, appointment_time, appointment_type, notes, appointment_id))
    conn.commit()
    conn.close()
    return {"message": "התור עודכן בהצלחה!"}

# ביטול תור
@app.delete("/api/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments
        SET status = 'בוטל', updated_at = CURRENT_TIMESTAMP
        WHERE appointment_id = ?
    """, (appointment_id,))
    conn.commit()
    conn.close()
    return {"message": "התור בוטל בהצלחה!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
