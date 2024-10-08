import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import psycopg2
from tkinter import messagebox

class CalculationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculation App")
        self.root.geometry("500x400")

        self.create_menu()
 
        self.tabControl = ttk.Notebook(root)

        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Calculation')
        self.create_calculation_tab(self.tab1)

        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text='History')
        self.create_history_tab(self.tab2)

        self.tabControl.pack(expand=1, fill="both")
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        messagebox.showinfo("About", "This is an Calculation App using Python and PostgreSQL.")

    def create_calculation_tab(self, frame):
        tk.Label(frame, text="Số thứ nhất:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input1 = tk.Entry(frame)
        self.input1.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(frame, text="Số thứ hai:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.input2 = tk.Entry(frame)
        self.input2.grid(row=0, column=3, padx=10, pady=10)

        self.calculate_button = tk.Button(frame, text="Kết quả", command=self.calculate)
        self.calculate_button.grid(row=0, column=4, padx=10, pady=10)

        self.addition = tk.BooleanVar()
        self.subtraction = tk.BooleanVar()
        self.multiplication = tk.BooleanVar()
        self.division = tk.BooleanVar()

        tk.Checkbutton(frame, text="Cộng", variable=self.addition).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Checkbutton(frame, text="Trừ", variable=self.subtraction).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        tk.Checkbutton(frame, text="Nhân", variable=self.multiplication).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        tk.Checkbutton(frame, text="Chia", variable=self.division).grid(row=1, column=3, padx=10, pady=5, sticky="w")

        self.result_display = ScrolledText(frame, height=5, width=40)
        self.result_display.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

    def create_history_tab(self, frame):
        self.history_list = tk.Listbox(frame)
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_history()

    def calculate(self):
        try:
            val1 = float(self.input1.get())
            val2 = float(self.input2.get())
            result = 0
            operations = []
            
            if self.addition.get():
                result = val1 + val2
                operations.append(f"{val1} + {val2} = {result}")
            if self.subtraction.get():
                result = val1 - val2
                operations.append(f"{val1} - {val2} = {result}")
            if self.multiplication.get():
                result = val1 * val2
                operations.append(f"{val1} * {val2} = {result}")
            if self.division.get() and val2 != 0:
                result = val1 / val2
                operations.append(f"{val1} / {val2} = {result}")

            if not operations:
                self.result_display.insert(tk.END, "Please select at least one operation.\n")
            else:
                self.result_display.insert(tk.END, "\n".join(operations) + "\n")
            
            self.save_to_database(val1, val2, result)

            self.load_history()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for Input 1 and Input 2")

    def save_to_database(self, val1, val2, result):
        try:
            conn = psycopg2.connect(
                database="kimtai",
                user="postgres",
                password="0934136619Tai",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO calculation_data (input_value_1, input_value_2, result) VALUES (%s, %s, %s)", (val1, val2, result))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving to database: {e}")
    
    def load_history(self):
        self.history_list.delete(0, tk.END)
        
        try:
            conn = psycopg2.connect(
                database="kimtai",
                user="postgres",
                password="0934136619Tai",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT input_value_1, input_value_2, result FROM calculation_data ORDER BY created_at DESC")
            rows = cursor.fetchall()
            for row in rows:
                self.history_list.insert(tk.END, f"{row[0]} + {row[1]} = {row[2]}")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading history: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculationApp(root)
    root.mainloop()
