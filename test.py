import psycopg2
from psycopg2 import sql
from tkinter import messagebox

def connect():
    try:
        conn = psycopg2.connect(
            database="kimtai",
            user="postgres",
            password="0934136619Tai",
            host="localhost",
            port="5432"
        )
        messagebox.showinfo("Success", f"Connected to database successfully!")
        return conn
    except Exception as ex:
        messagebox.showerror("Error", f"Error connecting to database: {ex}")
        return None

def selectSV(cur):
    try:
        query = sql.SQL("SELECT * FROM sinhvien")
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Exception as ex:
        print(f"Error during select: {ex}")

def insertDB(conn, mssv, hoten):
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO sinhvien (mssv, hoten) VALUES (%s, %s)", (mssv, hoten))
        conn.commit()
        print("Thêm thành công")
    except Exception as ex:
        conn.rollback()
        print(f"Error during insert: {ex}")

if __name__ == "__main__":
    conn = connect()
    if conn:
        cur = conn.cursor()
        selectSV(cur)
        print("Insert sinhvien:-------------")
        insertDB(conn, '2049281', 'Nguyen Hieu')
        selectSV(cur)
        conn.close()
    else:
        print("Connection failed.")
