import sqlite3

def init_db():
    conn = sqlite3.connect('clalit.db')
    cursor = conn.cursor()

    # יצירת טבלת Customers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_number TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'פעיל',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # יצירת טבלת Appointments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        doctor_name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        clinic_name TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        appointment_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'נקבע',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')

    # הכנסת נתונים ראשוניים אם הטבלה ריקה
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO customers (id_number, first_name, last_name, phone, email, username, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('123456789', 'עומר', 'כהן', '0501234567', 'omer@example.com', 'omer', 'demo_hash'),
            ('987654321', 'נועה', 'לוי', '0527654321', 'noa@example.com', 'noa', 'demo_hash'),
            ('288569823', 'מירי', 'בן לוי', '0525381648', 'miri@example.com', 'miri', 'demo_hash'),
            ('223344556', 'עודד', 'בן עמי', '0507864249', 'oded@example.com', 'oded', 'demo_hash'),
            ('443322115', 'סיון', 'בן ציון', '0557098567', 'sivan@example.com', 'sivan', 'demo_hash'),
            ('889977666', 'עמרי', 'חן פרסיה', '0503457862', 'omri@example.com', 'omri', 'demo_hash')
        ])

        cursor.execute('''
        INSERT INTO appointments (customer_id, doctor_name, specialization, clinic_name, appointment_date, appointment_time, appointment_type, status, notes)
        VALUES (1, 'ד"ר יעל ישראלי', 'רפואת משפחה', 'מרפאת כללית מרכז', '2026-07-27', '10:30', 'ביקור במרפאה', 'נקבע', 'תור לדוגמה')
        ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
