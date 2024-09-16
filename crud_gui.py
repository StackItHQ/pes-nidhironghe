import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'shivaji9',
    'database': 'Superjoin_Hiring_Process'
}

def configure_styles():
    style = ttk.Style()
    
    bg_color = "#f0f4f8"
    primary_color = "#1a73e8"
    secondary_color = "#34a853"
    text_color = "#000000"
    
    style.configure(".",
                    font=("Helvetica", 10),
                    background=bg_color,
                    foreground=text_color)

    style.configure("Treeview",
                    background=bg_color,
                    foreground=text_color,
                    rowheight=25,
                    fieldbackground=bg_color)
    style.configure("Treeview.Heading",
                    background=primary_color,
                    foreground=text_color,
                    font=("Helvetica", 11, "bold"),
                    relief="flat")
    style.map('Treeview',
              background=[('selected', secondary_color)],
              foreground=[('selected', 'black')])

    style.configure("TButton",
                    padding=10,
                    relief="flat",
                    background=primary_color,
                    foreground=text_color,
                    font=("Helvetica", 10, "bold"))
    style.map("TButton",
              background=[("active", secondary_color)],
              foreground=[("active", "black")])

    style.configure("TLabel",
                    background=bg_color,
                    foreground=text_color,
                    font=("Helvetica", 11))

    style.configure("TEntry",
                    fieldbackground="white",
                    foreground=text_color,
                    padding=5)

class CRUDApp:
    def __init__(self, root, db_connection):
        self.root = root
        self.db_connection = db_connection
        self.root.title("Candidate Management System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f4f8")

        configure_styles()

        main_frame = tk.Frame(root, bg="#f0f4f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="Candidate Management System", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=(0, 20))

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Score", "Strength", "Weakness", "Feedback", "LastUpdated"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Score", text="Score")
        self.tree.heading("Strength", text="Strength")
        self.tree.heading("Weakness", text="Weakness")
        self.tree.heading("Feedback", text="Feedback")
        self.tree.heading("LastUpdated", text="Last Updated")
        
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Score", width=50)
        self.tree.column("Strength", width=150)
        self.tree.column("Weakness", width=150)
        self.tree.column("Feedback", width=200)
        self.tree.column("LastUpdated", width=150)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        self.load_data_button = ttk.Button(button_frame, text="Load Data", command=self.load_data)
        self.load_data_button.pack(side=tk.LEFT, padx=5)

        self.create_button = ttk.Button(button_frame, text="Create", command=self.create_candidate)
        self.create_button.pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(button_frame, text="Update", command=self.update_candidate)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_candidate)
        self.delete_button.pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        data = read_candidates(self.db_connection)
        for row in data:
            self.tree.insert('', tk.END, values=(row['candidate_id'], row['candidate_name'], row['interview_score'], row['strength'], row['weakness'], row['feedback'], row['last_updated']))

    def create_candidate(self):
        CreateUpdateDialog(self.root, self.db_connection, "Create")

    def update_candidate(self):
        CreateUpdateDialog(self.root, self.db_connection, "Update")

    def delete_candidate(self):
        candidate_id = self.prompt_for_id("Delete")
        if candidate_id:
            delete_candidate(self.db_connection, candidate_id)
            self.load_data()

    def prompt_for_id(self, action):
        def submit_id():
            nonlocal candidate_id
            candidate_id = id_entry.get()
            dialog.destroy()
        candidate_id = None
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{action} Candidate")
        dialog.configure(bg="#f0f0f0")
        tk.Label(dialog, text="Candidate ID:", bg="#f0f0f0").pack(pady=10)
        id_entry = tk.Entry(dialog)
        id_entry.pack(pady=5)
        tk.Button(dialog, text="Submit", command=submit_id).pack(pady=10)
        dialog.wait_window()
        return candidate_id

class CreateUpdateDialog:
    def __init__(self, parent, db_connection, action):
        self.db_connection = db_connection
        self.action = action
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{action} Candidate")
        self.dialog.configure(bg="#f0f4f8")
        self.dialog.geometry("400x450")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text=f"{self.action} Candidate", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(0, 20))

        self.fields = ['ID', 'Name', 'Score', 'Strength', 'Weakness', 'Feedback']
        self.entries = {}
        for field in self.fields:
            field_frame = ttk.Frame(main_frame)
            field_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(field_frame, text=field, width=15).pack(side=tk.LEFT)
            entry = ttk.Entry(field_frame)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.entries[field] = entry

        ttk.Button(main_frame, text=self.action, command=self.execute).pack(pady=20)

    def execute(self):
        data = {field: entry.get() for field, entry in self.entries.items()}
        candidate_id = data.pop('ID')
        if self.action == "Create":
            create_candidate(self.db_connection, (candidate_id, data['Name'], int(data['Score']), data['Strength'], data['Weakness'], data['Feedback'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        elif self.action == "Update":
            update_candidate(self.db_connection, (data['Name'], int(data['Score']), data['Strength'], data['Weakness'], data['Feedback'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), candidate_id))
        self.dialog.destroy()
        messagebox.showinfo("Success", f"Candidate {self.action}d successfully.")

def create_candidate(db_connection, candidate_data):
    query = """
    INSERT INTO candidates (candidate_id, candidate_name, interview_score, strength, weakness, feedback, last_updated)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, candidate_data)
        db_connection.commit()
        print("Candidate created successfully.")
    except Error as e:
        print(f"Error creating candidate: {e}")
        db_connection.rollback()

def read_candidates(db_connection):
    query = "SELECT * FROM candidates"
    try:
        with db_connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        print("Fetched candidates from database.")
        return data
    except Error as e:
        print(f"Error reading candidates: {e}")
        return []

def update_candidate(db_connection, candidate_data):
    query = """
    UPDATE candidates
    SET candidate_name = %s, interview_score = %s, strength = %s, weakness = %s, feedback = %s, last_updated = %s
    WHERE candidate_id = %s;
    """
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, candidate_data)
        db_connection.commit()
        print("Candidate updated successfully.")
    except Error as e:
        print(f"Error updating candidate: {e}")
        db_connection.rollback()

def delete_candidate(db_connection, candidate_id):
    query = "DELETE FROM candidates WHERE candidate_id = %s"
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, (candidate_id,))
        db_connection.commit()
        print("Candidate deleted successfully.")
    except Error as e:
        print(f"Error deleting candidate: {e}")
        db_connection.rollback()

def main():
    db_connection = mysql.connector.connect(**DB_CONFIG)
    root = tk.Tk()
    app = CRUDApp(root, db_connection)
    root.mainloop()
    db_connection.close()

if __name__ == '__main__':
    main()