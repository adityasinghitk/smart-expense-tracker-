<<<<<<< HEAD
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector

# ================= DB CONNECTION =================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Aditya@123",
    database="smart_expense_tracker"
)
cursor = conn.cursor()
root = tk.Tk()
root.title("Smart Expense Tracker")
root.geometry("800x500")

income_list = []
expense_list = []
transactions = []
chart = None

# ================= HEADER =================
tk.Label(root, text="Smart Expense Tracker",
         bg="#2b5db7", fg="white",
         font=("Arial", 20), pady=10).pack(fill="x")

# ================= MAIN FRAME =================
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# ================= SIDEBAR =================
sidebar = tk.Frame(main_frame, bg="#2b5db7", width=150)
sidebar.pack(side="left", fill="y")

# ================= CONTENT =================
content = tk.Frame(main_frame, bg="#f2f2f2")
content.pack(side="right", fill="both", expand=True)

# ================= LOAD DATA =================
def load_data():
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    for row in data:
        t = {
            "id": row[0],
            "type": row[1],
            "amount": row[2],
            "date": row[3],
            "category": row[4],
            "source": row[5],
            "notes": row[6]
        }
        transactions.append(t)

        if row[1] == "income":
            income_list.append(row[2])
        else:
            expense_list.append(row[2])

# ================= CLEAR =================
def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

# ================= DELETE =================
def delete_transaction(index):
    item = transactions[index]

    cursor.execute("DELETE FROM transactions WHERE id=%s", (item["id"],))
    conn.commit()

    if item["type"] == "income":
        if item["amount"] in income_list:
            income_list.remove(item["amount"])
    else:
        if item["amount"] in expense_list:
            expense_list.remove(item["amount"])

    transactions.pop(index)
    show_dashboard()

# ================= EDIT =================
def edit_transaction(index):
    clear_content()
    data = transactions[index]

    tk.Label(content, text="Edit Amount").pack()
    amount = tk.Entry(content)
    amount.insert(0, data["amount"])
    amount.pack()

    tk.Label(content, text="Edit Date").pack()
    date = tk.Entry(content)
    date.insert(0, data["date"])
    date.pack()

    tk.Label(content, text="Edit Category").pack()
    category = tk.Entry(content)
    category.insert(0, data["category"])
    category.pack()

    tk.Label(content, text="Edit Source").pack()
    source = tk.Entry(content)
    source.insert(0, data["source"])
    source.pack()

    tk.Label(content, text="Edit Notes").pack()
    notes = tk.Entry(content)
    notes.insert(0, data["notes"])
    notes.pack()

    def update():
        try:
            new_amt = int(amount.get())

            cursor.execute(
                "UPDATE transactions SET amount=%s, date=%s, category=%s, source=%s, notes=%s WHERE id=%s",
                (new_amt, date.get(), category.get(), source.get(), notes.get(), data["id"])
            )
            conn.commit()

            if data["type"] == "income":
                if data["amount"] in income_list:
                    income_list.remove(data["amount"])
                income_list.append(new_amt)
            else:
                if data["amount"] in expense_list:
                    expense_list.remove(data["amount"])
                expense_list.append(new_amt)

            transactions[index] = {
                "id": data["id"],
                "type": data["type"],
                "amount": new_amt,
                "date": date.get(),
                "category": category.get(),
                "source": source.get(),
                "notes": notes.get()
            }

            show_dashboard()
        except:
            pass

    tk.Button(content, text="Update", command=update).pack(pady=10)

# ================= DASHBOARD =================
def show_dashboard():
    global chart
    clear_content()

    total_income = sum(income_list)
    total_expense = sum(expense_list)
    balance = total_income - total_expense

    tk.Label(content, text=f"Total Income: ₹{total_income}",
             font=("Arial", 14)).pack(pady=5)

    tk.Label(content, text=f"Total Expense: ₹{total_expense}",
             font=("Arial", 14)).pack(pady=5)

    tk.Label(content, text=f"Balance: ₹{balance}",
             font=("Arial", 16, "bold")).pack(pady=5)

    total = total_income + total_expense

    if total == 0:
        values = [0, 0]
    else:
        values = [(total_income/total)*100, (total_expense/total)*100]

    if chart:
        chart.get_tk_widget().destroy()

    fig, ax = plt.subplots(figsize=(5,2.5))
    y_pos = np.arange(2)

    ax.barh(y_pos, values, color=["green", "red"])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(["Income", "Expense"])
    ax.invert_yaxis()

    fig.subplots_adjust(left=0.30, bottom=0.20)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentage (%)")

    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v:.1f}%", va='center')

    chart = FigureCanvasTkAgg(fig, master=content)
    chart.draw()
    chart.get_tk_widget().pack(pady=5)

    # ================= TABLE =================
    bottom_frame = tk.Frame(content, bg="#f2f2f2")
    bottom_frame.pack(fill="both", expand=True, pady=10)

    headers = ["Source", "Amount", "Date", "Category", "Notes"]
    widths = [12, 10, 12, 12, 20]

    # -------- RECENT INCOME --------
    income_frame = tk.Frame(bottom_frame, bg="white", bd=1, relief="solid")
    income_frame.pack(side="left", expand=True, fill="both", padx=10)

    tk.Label(income_frame, text="Recent Income",
             font=("Arial", 12, "bold"), bg="white").pack(pady=5)

    header = tk.Frame(income_frame, bg="#e6e6e6")
    header.pack(fill="x", padx=5)
    for i, h in enumerate(headers):
        tk.Label(header, text=h, width=widths[i],
                 bg="#e6e6e6").grid(row=0, column=i)

    income_txn = [(i, t) for i, t in enumerate(transactions) if t["type"] == "income"]

    for idx, item in income_txn[-5:][::-1]:
        row = tk.Frame(income_frame, bg="white")
        row.pack(fill="x", padx=5)

        values = [item["source"], f"₹{item['amount']}", item["date"],
                  item["category"], item["notes"]]

        for i, val in enumerate(values):
            tk.Label(row, text=val, width=widths[i],
                     anchor="w", bg="white").grid(row=0, column=i, padx=2)

        tk.Button(row, text="Edit",
                  command=lambda i=idx: edit_transaction(i)).grid(row=0, column=5)

        tk.Button(row, text="Delete",
                  command=lambda i=idx: delete_transaction(i)).grid(row=0, column=6)

    # -------- RECENT EXPENSE --------
    expense_frame = tk.Frame(bottom_frame, bg="white", bd=1, relief="solid")
    expense_frame.pack(side="right", expand=True, fill="both", padx=10)

    tk.Label(expense_frame, text="Recent Expense",
             font=("Arial", 12, "bold"), bg="white").pack(pady=5)
  
    header2 = tk.Frame(expense_frame, bg="#e6e6e6")
    header2.pack(fill="x", padx=5)

    for i, h in enumerate(headers):
        tk.Label(header2, text=h, width=widths[i],
                 bg="#e6e6e6").grid(row=0, column=i)

    expense_txn = [(i, t) for i, t in enumerate(transactions) if t["type"] == "expense"]

    for idx, item in expense_txn[-5:][::-1]:
        row = tk.Frame(expense_frame, bg="white")
        row.pack(fill="x", padx=5)

        values = [item["source"], f"₹{item['amount']}", item["date"],
                  item["category"], item["notes"]]

        for i, val in enumerate(values):
            tk.Label(row, text=val, width=widths[i],
                     anchor="w", bg="white").grid(row=0, column=i, padx=2)

        tk.Button(row, text="Edit",
                  command=lambda i=idx: edit_transaction(i)).grid(row=0, column=5)

        tk.Button(row, text="Delete",
                  command=lambda i=idx: delete_transaction(i)).grid(row=0, column=6)

 # ================= INCOME =================
def show_income():
    clear_content()

    tk.Label(content, text="Amount").pack()
    amount = tk.Entry(content)
    amount.pack()

    tk.Label(content, text="Date").pack()
    date = tk.Entry(content)
    date.pack()

    tk.Label(content, text="Category").pack()
    category_var = tk.StringVar(value="Salary")
    tk.OptionMenu(content, category_var,
                  "Salary", "Freelance", "Business", "Investment").pack()
    
    tk.Label(content, text="Source").pack()
    source = tk.Entry(content)
    source.pack()
    
    tk.Label(content, text="Notes").pack()
    notes = tk.Entry(content)
    notes.pack()

    def save():
        try:
            amt = int(amount.get())

            cursor.execute(
                "INSERT INTO transactions (type, amount, date, category, source, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                ("income", amt, date.get(), category_var.get(), source.get(), notes.get())
            )
            conn.commit()

            transactions.append({
                "id": cursor.lastrowid,
                "type": "income",
                "amount": amt,
                "date": date.get(),
                "category": category_var.get(),
                "source": source.get(),
                "notes": notes.get()
            })

            income_list.append(amt)
            show_dashboard()
        except:
            pass

    tk.Button(content, text="Save Income", command=save).pack(pady=10)

# ================= EXPENSE =================
def show_expense():
    clear_content()

    tk.Label(content, text="Amount").pack()
    amount = tk.Entry(content)
    amount.pack()

    tk.Label(content, text="Date").pack()
    date = tk.Entry(content)
    date.pack()

    tk.Label(content, text="Category").pack()
    category_var = tk.StringVar(value="Food")
    tk.OptionMenu(content, category_var,
                  "Food", "Travel", "Shopping", "Bills",
                  "Entertainment", "Education", "Medical", "EMI").pack()

    tk.Label(content, text="Source").pack()
    source = tk.Entry(content)
    source.pack()

    tk.Label(content, text="Notes").pack()
    notes = tk.Entry(content)
    notes.pack()

    def save():
        try:
            amt = int(amount.get())

            cursor.execute(
                "INSERT INTO transactions (type, amount, date, category, source, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                ("expense", amt, date.get(), category_var.get(), source.get(), notes.get())
            )
            conn.commit()

            transactions.append({
                "id": cursor.lastrowid,
                "type": "expense",
                "amount": amt,
                "date": date.get(),
                "category": category_var.get(),
                "source": source.get(),
                "notes": notes.get()
            })

            expense_list.append(amt)
            show_dashboard()
        except:
            pass

    tk.Button(content, text="Save Expense", command=save).pack(pady=10)


# ================= REPORTS =================
def show_reports():
    clear_content()

    tk.Label(content, text="Category Wise Expense Report",
             font=("Arial", 16, "bold")).pack(pady=10)

    category_data = {}

    for t in transactions:
        if t["type"] == "expense":
            cat = t["category"]
            category_data[cat] = category_data.get(cat, 0) + t["amount"]

    if not category_data:
        tk.Label(content, text="No Expense Data").pack()
        return

    labels = list(category_data.keys())
    values = list(category_data.values())

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.pie(values, labels=labels, autopct="%1.1f%%")

    chart = FigureCanvasTkAgg(fig, master=content)
    chart.draw()
    chart.get_tk_widget().pack(pady=10)

# ================= SETTINGS =================
def show_settings():
    clear_content()

    tk.Label(content, text="Settings",
             font=("Arial", 16, "bold")).pack(pady=10)

    box = tk.Frame(content, bg="white", bd=1, relief="solid")
    box.pack(pady=20, padx=20)

    tk.Label(box, text="Profile Settings", bg="white").pack(anchor="w", padx=10, pady=5)
    tk.Label(box, text="Change Password", bg="white").pack(anchor="w", padx=10, pady=5)
    tk.Label(box, text="Currency", bg="white").pack(anchor="w", padx=10, pady=5)

    notif_var = tk.IntVar()
    tk.Checkbutton(box, text="Enable Notifications",
                   variable=notif_var, bg="white").pack(anchor="w", padx=10, pady=5)

    dark_var = tk.IntVar()
    tk.Checkbutton(box, text="Dark Mode",
                   variable=dark_var, bg="white").pack(anchor="w", padx=10, pady=5)

    tk.Button(box, text="Logout").pack(pady=10)

    tk.Button(content, text="Save Settings").pack(pady=10)


# ================= SIDEBAR =================
tk.Button(sidebar, text="🏠 Dashboard", bg="#2b5db7", fg="white",
          bd=0, command=show_dashboard).pack(pady=15)

tk.Button(sidebar, text="💰 Income", bg="#2b5db7", fg="white",
          bd=0, command=show_income).pack(pady=15)

tk.Button(sidebar, text="💸 Expense", bg="#2b5db7", fg="white",
          bd=0, command=show_expense).pack(pady=15)

tk.Button(sidebar, text="📊 Reports", bg="#2b5db7", fg="white",
          bd=0, command=show_reports).pack(pady=15)

tk.Button(sidebar, text="⚙️ Settings", bg="#2b5db7", fg="white",
          bd=0, command=show_settings).pack(pady=15)

# ================= START =================
load_data()
show_dashboard()

root.mainloop()
=======
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector

# ================= DB CONNECTION =================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="*******",
    database="smart_expense_tracker"
)
cursor = conn.cursor()
root = tk.Tk()
root.title("Smart Expense Tracker")
root.geometry("800x500")

income_list = []
expense_list = []
transactions = []
chart = None

# ================= HEADER =================
tk.Label(root, text="Smart Expense Tracker",
         bg="#2b5db7", fg="white",
         font=("Arial", 20), pady=10).pack(fill="x")

# ================= MAIN FRAME =================
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# ================= SIDEBAR =================
sidebar = tk.Frame(main_frame, bg="#2b5db7", width=150)
sidebar.pack(side="left", fill="y")

# ================= CONTENT =================
content = tk.Frame(main_frame, bg="#f2f2f2")
content.pack(side="right", fill="both", expand=True)

# ================= LOAD DATA =================
def load_data():
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    for row in data:
        t = {
            "id": row[0],
            "type": row[1],
            "amount": row[2],
            "date": row[3],
            "category": row[4],
            "source": row[5],
            "notes": row[6]
        }
        transactions.append(t)

        if row[1] == "income":
            income_list.append(row[2])
        else:
            expense_list.append(row[2])

# ================= CLEAR =================
def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

# ================= DELETE =================
def delete_transaction(index):
    item = transactions[index]

    cursor.execute("DELETE FROM transactions WHERE id=%s", (item["id"],))
    conn.commit()

    if item["type"] == "income":
        if item["amount"] in income_list:
            income_list.remove(item["amount"])
    else:
        if item["amount"] in expense_list:
            expense_list.remove(item["amount"])

    transactions.pop(index)
    show_dashboard()

# ================= EDIT =================
def edit_transaction(index):
    clear_content()
    data = transactions[index]

    tk.Label(content, text="Edit Amount").pack()
    amount = tk.Entry(content)
    amount.insert(0, data["amount"])
    amount.pack()

    tk.Label(content, text="Edit Date").pack()
    date = tk.Entry(content)
    date.insert(0, data["date"])
    date.pack()

    tk.Label(content, text="Edit Category").pack()
    category = tk.Entry(content)
    category.insert(0, data["category"])
    category.pack()

    tk.Label(content, text="Edit Source").pack()
    source = tk.Entry(content)
    source.insert(0, data["source"])
    source.pack()

    tk.Label(content, text="Edit Notes").pack()
    notes = tk.Entry(content)
    notes.insert(0, data["notes"])
    notes.pack()

    def update():
        try:
            new_amt = int(amount.get())

            cursor.execute(
                "UPDATE transactions SET amount=%s, date=%s, category=%s, source=%s, notes=%s WHERE id=%s",
                (new_amt, date.get(), category.get(), source.get(), notes.get(), data["id"])
            )
            conn.commit()

            if data["type"] == "income":
                if data["amount"] in income_list:
                    income_list.remove(data["amount"])
                income_list.append(new_amt)
            else:
                if data["amount"] in expense_list:
                    expense_list.remove(data["amount"])
                expense_list.append(new_amt)

            transactions[index] = {
                "id": data["id"],
                "type": data["type"],
                "amount": new_amt,
                "date": date.get(),
                "category": category.get(),
                "source": source.get(),
                "notes": notes.get()
            }

            show_dashboard()
        except:
            pass

    tk.Button(content, text="Update", command=update).pack(pady=10)

# ================= DASHBOARD =================
def show_dashboard():
    global chart
    clear_content()

    total_income = sum(income_list)
    total_expense = sum(expense_list)
    balance = total_income - total_expense

    tk.Label(content, text=f"Total Income: ₹{total_income}",
             font=("Arial", 14)).pack(pady=5)

    tk.Label(content, text=f"Total Expense: ₹{total_expense}",
             font=("Arial", 14)).pack(pady=5)

    tk.Label(content, text=f"Balance: ₹{balance}",
             font=("Arial", 16, "bold")).pack(pady=5)

    total = total_income + total_expense

    if total == 0:
        values = [0, 0]
    else:
        values = [(total_income/total)*100, (total_expense/total)*100]

    if chart:
        chart.get_tk_widget().destroy()

    fig, ax = plt.subplots(figsize=(5,2.5))
    y_pos = np.arange(2)

    ax.barh(y_pos, values, color=["green", "red"])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(["Income", "Expense"])
    ax.invert_yaxis()

    fig.subplots_adjust(left=0.30, bottom=0.20)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentage (%)")

    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v:.1f}%", va='center')

    chart = FigureCanvasTkAgg(fig, master=content)
    chart.draw()
    chart.get_tk_widget().pack(pady=5)

    # ================= TABLE =================
    bottom_frame = tk.Frame(content, bg="#f2f2f2")
    bottom_frame.pack(fill="both", expand=True, pady=10)

    headers = ["Source", "Amount", "Date", "Category", "Notes"]
    widths = [12, 10, 12, 12, 20]

    # -------- RECENT INCOME --------
    income_frame = tk.Frame(bottom_frame, bg="white", bd=1, relief="solid")
    income_frame.pack(side="left", expand=True, fill="both", padx=10)

    tk.Label(income_frame, text="Recent Income",
             font=("Arial", 12, "bold"), bg="white").pack(pady=5)

    header = tk.Frame(income_frame, bg="#e6e6e6")
    header.pack(fill="x", padx=5)
    for i, h in enumerate(headers):
        tk.Label(header, text=h, width=widths[i],
                 bg="#e6e6e6").grid(row=0, column=i)

    income_txn = [(i, t) for i, t in enumerate(transactions) if t["type"] == "income"]

    for idx, item in income_txn[-5:][::-1]:
        row = tk.Frame(income_frame, bg="white")
        row.pack(fill="x", padx=5)

        values = [item["source"], f"₹{item['amount']}", item["date"],
                  item["category"], item["notes"]]

        for i, val in enumerate(values):
            tk.Label(row, text=val, width=widths[i],
                     anchor="w", bg="white").grid(row=0, column=i, padx=2)

        tk.Button(row, text="Edit",
                  command=lambda i=idx: edit_transaction(i)).grid(row=0, column=5)

        tk.Button(row, text="Delete",
                  command=lambda i=idx: delete_transaction(i)).grid(row=0, column=6)

    # -------- RECENT EXPENSE --------
    expense_frame = tk.Frame(bottom_frame, bg="white", bd=1, relief="solid")
    expense_frame.pack(side="right", expand=True, fill="both", padx=10)

    tk.Label(expense_frame, text="Recent Expense",
             font=("Arial", 12, "bold"), bg="white").pack(pady=5)
  
    header2 = tk.Frame(expense_frame, bg="#e6e6e6")
    header2.pack(fill="x", padx=5)

    for i, h in enumerate(headers):
        tk.Label(header2, text=h, width=widths[i],
                 bg="#e6e6e6").grid(row=0, column=i)

    expense_txn = [(i, t) for i, t in enumerate(transactions) if t["type"] == "expense"]

    for idx, item in expense_txn[-5:][::-1]:
        row = tk.Frame(expense_frame, bg="white")
        row.pack(fill="x", padx=5)

        values = [item["source"], f"₹{item['amount']}", item["date"],
                  item["category"], item["notes"]]

        for i, val in enumerate(values):
            tk.Label(row, text=val, width=widths[i],
                     anchor="w", bg="white").grid(row=0, column=i, padx=2)

        tk.Button(row, text="Edit",
                  command=lambda i=idx: edit_transaction(i)).grid(row=0, column=5)

        tk.Button(row, text="Delete",
                  command=lambda i=idx: delete_transaction(i)).grid(row=0, column=6)

 # ================= INCOME =================
def show_income():
    clear_content()

    tk.Label(content, text="Amount").pack()
    amount = tk.Entry(content)
    amount.pack()

    tk.Label(content, text="Date").pack()
    date = tk.Entry(content)
    date.pack()

    tk.Label(content, text="Category").pack()
    category_var = tk.StringVar(value="Salary")
    tk.OptionMenu(content, category_var,
                  "Salary", "Freelance", "Business", "Investment").pack()
    
    tk.Label(content, text="Source").pack()
    source = tk.Entry(content)
    source.pack()
    
    tk.Label(content, text="Notes").pack()
    notes = tk.Entry(content)
    notes.pack()

    def save():
        try:
            amt = int(amount.get())

            cursor.execute(
                "INSERT INTO transactions (type, amount, date, category, source, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                ("income", amt, date.get(), category_var.get(), source.get(), notes.get())
            )
            conn.commit()

            transactions.append({
                "id": cursor.lastrowid,
                "type": "income",
                "amount": amt,
                "date": date.get(),
                "category": category_var.get(),
                "source": source.get(),
                "notes": notes.get()
            })

            income_list.append(amt)
            show_dashboard()
        except:
            pass

    tk.Button(content, text="Save Income", command=save).pack(pady=10)

# ================= EXPENSE =================
def show_expense():
    clear_content()

    tk.Label(content, text="Amount").pack()
    amount = tk.Entry(content)
    amount.pack()

    tk.Label(content, text="Date").pack()
    date = tk.Entry(content)
    date.pack()

    tk.Label(content, text="Category").pack()
    category_var = tk.StringVar(value="Food")
    tk.OptionMenu(content, category_var,
                  "Food", "Travel", "Shopping", "Bills",
                  "Entertainment", "Education", "Medical", "EMI").pack()

    tk.Label(content, text="Source").pack()
    source = tk.Entry(content)
    source.pack()

    tk.Label(content, text="Notes").pack()
    notes = tk.Entry(content)
    notes.pack()

    def save():
        try:
            amt = int(amount.get())

            cursor.execute(
                "INSERT INTO transactions (type, amount, date, category, source, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                ("expense", amt, date.get(), category_var.get(), source.get(), notes.get())
            )
            conn.commit()

            transactions.append({
                "id": cursor.lastrowid,
                "type": "expense",
                "amount": amt,
                "date": date.get(),
                "category": category_var.get(),
                "source": source.get(),
                "notes": notes.get()
            })

            expense_list.append(amt)
            show_dashboard()
        except:
            pass

    tk.Button(content, text="Save Expense", command=save).pack(pady=10)


# ================= REPORTS =================
def show_reports():
    clear_content()

    tk.Label(content, text="Category Wise Expense Report",
             font=("Arial", 16, "bold")).pack(pady=10)

    category_data = {}

    for t in transactions:
        if t["type"] == "expense":
            cat = t["category"]
            category_data[cat] = category_data.get(cat, 0) + t["amount"]

    if not category_data:
        tk.Label(content, text="No Expense Data").pack()
        return

    labels = list(category_data.keys())
    values = list(category_data.values())

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.pie(values, labels=labels, autopct="%1.1f%%")

    chart = FigureCanvasTkAgg(fig, master=content)
    chart.draw()
    chart.get_tk_widget().pack(pady=10)

# ================= SETTINGS =================
def show_settings():
    clear_content()

    tk.Label(content, text="Settings",
             font=("Arial", 16, "bold")).pack(pady=10)

    box = tk.Frame(content, bg="white", bd=1, relief="solid")
    box.pack(pady=20, padx=20)

    tk.Label(box, text="Profile Settings", bg="white").pack(anchor="w", padx=10, pady=5)
    tk.Label(box, text="Change Password", bg="white").pack(anchor="w", padx=10, pady=5)
    tk.Label(box, text="Currency", bg="white").pack(anchor="w", padx=10, pady=5)

    notif_var = tk.IntVar()
    tk.Checkbutton(box, text="Enable Notifications",
                   variable=notif_var, bg="white").pack(anchor="w", padx=10, pady=5)

    dark_var = tk.IntVar()
    tk.Checkbutton(box, text="Dark Mode",
                   variable=dark_var, bg="white").pack(anchor="w", padx=10, pady=5)

    tk.Button(box, text="Logout").pack(pady=10)

    tk.Button(content, text="Save Settings").pack(pady=10)


# ================= SIDEBAR =================
tk.Button(sidebar, text="🏠 Dashboard", bg="#2b5db7", fg="white",
          bd=0, command=show_dashboard).pack(pady=15)

tk.Button(sidebar, text="💰 Income", bg="#2b5db7", fg="white",
          bd=0, command=show_income).pack(pady=15)

tk.Button(sidebar, text="💸 Expense", bg="#2b5db7", fg="white",
          bd=0, command=show_expense).pack(pady=15)

tk.Button(sidebar, text="📊 Reports", bg="#2b5db7", fg="white",
          bd=0, command=show_reports).pack(pady=15)

tk.Button(sidebar, text="⚙️ Settings", bg="#2b5db7", fg="white",
          bd=0, command=show_settings).pack(pady=15)

# ================= START =================
load_data()
show_dashboard()

root.mainloop()
>>>>>>> fad9d55166c63683925e3806a1767d87b5fb5f4a
