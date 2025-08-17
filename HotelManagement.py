import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import date, timedelta, datetime

# ----------------- DB Setup -----------------
conn = sqlite3.connect("hotel_gui.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type TEXT,
    price REAL,
    status TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    room_id INTEGER,
    check_in DATE,
    check_out DATE,
    FOREIGN KEY(room_id) REFERENCES Rooms(room_id)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS FoodMenu (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    price REAL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY(item_id) REFERENCES FoodMenu(item_id)
)''')

# Insert default data if empty
cursor.execute("SELECT COUNT(*) FROM Rooms")
if cursor.fetchone()[0] == 0:
    rooms = [("Single", 1000, "Available"), ("Double", 1800, "Available"), ("Suite", 3000, "Available")]
    cursor.executemany("INSERT INTO Rooms(room_type, price, status) VALUES (?, ?, ?)", rooms)

cursor.execute("SELECT COUNT(*) FROM FoodMenu")
if cursor.fetchone()[0] == 0:
    menu = [("Pasta", 250), ("Burger", 150), ("Pizza", 400), ("Coffee", 100), ("Sandwich", 120)]
    cursor.executemany("INSERT INTO FoodMenu(item_name, price) VALUES (?, ?)", menu)

conn.commit()

# ----------------- GUI Functions -----------------
def show_rooms():
    top = tk.Toplevel(root)
    top.title("Available Rooms")
    top.configure(bg="#195183")
    cursor.execute("SELECT * FROM Rooms")
    for i, row in enumerate(cursor.fetchall()):
        tk.Label(top, text=f"Room ID: {row[0]} | Type: {row[1]} | Price: Rs.{row[2]} | Status: {row[3]}",
                 font=("Arial", 12), bg="#f0f8ff", fg="#333").pack(anchor="w", padx=10, pady=3)

def book_room():
    name = simpledialog.askstring("Input", "Enter Customer Name:")
    phone = simpledialog.askstring("Input", "Enter Phone Number:")
    show_rooms()
    room_id = simpledialog.askinteger("Input", "Enter Room ID to book:")
    cursor.execute("SELECT status FROM Rooms WHERE room_id=?", (room_id,))
    result = cursor.fetchone()
    if not result or result[0] != "Available":
        messagebox.showerror("Error", "Room not available")
        return
    days = simpledialog.askinteger("Input", "Enter number of days:")
    check_in = date.today()
    check_out = check_in + timedelta(days=days)
    cursor.execute("INSERT INTO Customers(name, phone, room_id, check_in, check_out) VALUES (?, ?, ?, ?, ?)",
                   (name, phone, room_id, check_in, check_out))
    cursor.execute("UPDATE Rooms SET status='Booked' WHERE room_id=?", (room_id,))
    conn.commit()
    messagebox.showinfo("Success", "Room booked successfully!")

def show_menu():
    top = tk.Toplevel(root)
    top.title("Food Menu")
    top.configure(bg="#fff8dc")
    cursor.execute("SELECT * FROM FoodMenu")
    for i, row in enumerate(cursor.fetchall()):
        tk.Label(top, text=f"ID: {row[0]} | {row[1]} | Rs.{row[2]}", font=("Arial", 12), bg="#fff8dc", fg="#444").pack(anchor="w", padx=10, pady=3)

def order_food():
    customer_id = simpledialog.askinteger("Input", "Enter Customer ID:")
    show_menu()
    item_id = simpledialog.askinteger("Input", "Enter Food Item ID:")
    qty = simpledialog.askinteger("Input", "Enter Quantity:")
    cursor.execute("INSERT INTO Orders(customer_id, item_id, quantity) VALUES (?, ?, ?)",
                   (customer_id, item_id, qty))
    conn.commit()
    messagebox.showinfo("Ordered", "Food ordered successfully!")

def generate_bill():
    customer_id = simpledialog.askinteger("Input", "Enter Customer ID:")
    cursor.execute("SELECT c.name, r.room_type, r.price, c.check_in, c.check_out FROM Customers c JOIN Rooms r ON c.room_id=r.room_id WHERE c.customer_id=?", (customer_id,))
    data = cursor.fetchone()
    if not data:
        messagebox.showerror("Error", "Customer not found")
        return
    name, room_type, price, check_in, check_out = data
    days = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
    room_bill = price * days
    cursor.execute("SELECT f.item_name, f.price, o.quantity FROM Orders o JOIN FoodMenu f ON o.item_id=f.item_id WHERE o.customer_id=?", (customer_id,))
    orders = cursor.fetchall()
    food_bill = sum([o[1] * o[2] for o in orders])
    total = room_bill + food_bill
    bill_win = tk.Toplevel(root)
    bill_win.title("Bill")
    bill_win.configure(bg="#f5f5f5")
    tk.Label(bill_win, text=f"Customer: {name}", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="#111").pack(pady=5)
    tk.Label(bill_win, text=f"Room: {room_type} | Days: {days} | Rs.{room_bill}", font=("Arial", 12), bg="#f5f5f5").pack()
    for o in orders:
        tk.Label(bill_win, text=f"{o[0]} x{o[2]} = Rs.{o[1]*o[2]}", font=("Arial", 12), bg="#f5f5f5").pack()
    tk.Label(bill_win, text=f"Total = Rs.{total}", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="green").pack(pady=5)

def checkout():
    customer_id = simpledialog.askinteger("Input", "Enter Customer ID:")
    cursor.execute("SELECT room_id FROM Customers WHERE customer_id=?", (customer_id,))
    room = cursor.fetchone()
    if not room:
        messagebox.showerror("Error", "Customer not found")
        return
    room_id = room[0]
    generate_bill()
    cursor.execute("UPDATE Rooms SET status='Available' WHERE room_id=?", (room_id,))
    cursor.execute("DELETE FROM Customers WHERE customer_id=?", (customer_id,))
    cursor.execute("DELETE FROM Orders WHERE customer_id=?", (customer_id,))
    conn.commit()
    messagebox.showinfo("Checked Out", "Customer checked out successfully")

# ----------------- Styled GUI Setup -----------------
root = tk.Tk()
root.title("Hotel Management System")
root.geometry("450x500")
root.configure(bg="#e6f2ff")

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=8)
style.map("TButton", foreground=[("pressed", "white"), ("active", "blue")], background=[("pressed", "#0059b3"), ("active", "#99ccff")])

tk.Label(root, text="🏨 Hotel Management System", font=("Arial", 20, "bold"), bg="#e6f2ff", fg="#003366").pack(pady=15)

buttons = [
    ("Show Rooms", show_rooms),
    ("Book Room", book_room),
    ("Show Food Menu", show_menu),
    ("Order Food", order_food),
    ("Generate Bill", generate_bill),
    ("Checkout", checkout),
    ("Exit", root.destroy)
]

for text, cmd in buttons:
    ttk.Button(root, text=text, command=cmd).pack(pady=8, fill="x", padx=40)

root.mainloop()