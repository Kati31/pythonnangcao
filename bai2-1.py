import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from psycopg2 import sql

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Database App")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        self.root.option_add("*TButton.Font", "Arial 10 bold")
        self.root.option_add("*TLabel.Font", "Arial 10")

        self.db_name = tk.StringVar(value='kimtai')
        self.user = tk.StringVar(value='postgres')
        self.password = tk.StringVar(value='0934136619Tai')
        self.host = tk.StringVar(value='localhost')
        self.port = tk.StringVar(value='5432')
        self.table_name = tk.StringVar(value='danhsach')

        self.create_menu()

        self.create_tabs()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_info)

    def show_about_info(self):
        messagebox.showinfo("About", "Database Application\nVersion 1.0\nCreated by Kim Tài")

    def create_tabs(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both')

        self.connection_tab = ttk.Frame(notebook)
        self.query_tab = ttk.Frame(notebook)
        self.insert_tab = ttk.Frame(notebook)

        notebook.add(self.connection_tab, text='Connection')
        notebook.add(self.query_tab, text='Query Data')
        notebook.add(self.insert_tab, text='Insert Data')

        self.create_connection_tab()
        self.create_query_tab()
        self.create_insert_tab()

    def create_connection_tab(self):
        connection_frame = ttk.Frame(self.connection_tab, padding=10)
        connection_frame.grid(pady=10)

        ttk.Label(connection_frame, text="DB Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(connection_frame, textvariable=self.db_name).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(connection_frame, text="User:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(connection_frame, textvariable=self.user).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(connection_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(connection_frame, textvariable=self.password, show="*").grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(connection_frame, text="Host:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(connection_frame, textvariable=self.host).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(connection_frame, text="Port:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(connection_frame, textvariable=self.port).grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(connection_frame, text="Connect", command=self.connect_db).grid(row=5, columnspan=2, pady=10)

    def create_query_tab(self):
        query_frame = ttk.Frame(self.query_tab, padding=10)
        query_frame.pack(pady=10)

        ttk.Label(query_frame, text="Table Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(query_frame, textvariable=self.table_name).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(query_frame, text="Load Data", command=self.load_data).grid(row=1, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.query_tab, columns=('Ho ten', 'Dia chi'), show='headings', height=10)
        self.tree.heading('Ho ten', text='Ho ten')
        self.tree.heading('Dia chi', text='Dia chi')
        self.tree.column('Ho ten', width=200)
        self.tree.column('Dia chi', width=200)
        self.tree.pack(pady=10, fill='x')

    def create_insert_tab(self):
        insert_frame = ttk.Frame(self.insert_tab, padding=10)
        insert_frame.pack(pady=10)

        self.column1 = tk.StringVar()
        self.column2 = tk.StringVar()

        ttk.Label(insert_frame, text="Ho ten:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(insert_frame, textvariable=self.column1).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(insert_frame, text="Dia chi:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(insert_frame, textvariable=self.column2).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(insert_frame, text="Insert Data", command=self.insert_data).grid(row=2, columnspan=2, pady=10)

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name.get(),
                user=self.user.get(),
                password=self.password.get(),
                host=self.host.get(),
                port=self.port.get()
            )
            self.cur = self.conn.cursor()
            messagebox.showinfo("Success", "Connected to the database successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error connecting to the database: {e}")

    def load_data(self):
        try:
            query = sql.SQL("SELECT hoten, diachi FROM {}").format(sql.Identifier(self.table_name.get()))
            self.cur.execute(query)
            rows = self.cur.fetchall()

            for i in self.tree.get_children():
                self.tree.delete(i)

            for row in rows:
                self.tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {e}")

    def insert_data(self):
        try:
            insert_query = sql.SQL("INSERT INTO {} (hoten, diachi) VALUES (%s, %s)").format(sql.Identifier(self.table_name.get()))
            data_to_insert = (self.column1.get(), self.column2.get())
            self.cur.execute(insert_query, data_to_insert)
            self.conn.commit()
            messagebox.showinfo("Success", "Data inserted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
