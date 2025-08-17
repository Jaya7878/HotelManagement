def show_rooms():
    top = tk.Toplevel(root)
    top.title("Available Rooms")
    top.configure(bg="#f0f8ff")
    cursor.execute("SELECT * FROM Rooms")
    for i, row in enumerate(cursor.fetchall()):
        tk.Label(top, text=f"Room ID: {row[0]} | Type: {row[1]} | Price: Rs.{row[2]} | Status: {row[3]}",
                 font=("Arial", 12), bg="#f0f8ff", fg="#333").pack(anchor="w", padx=10, pady=3)
