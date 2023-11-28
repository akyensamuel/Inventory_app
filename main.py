import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medicines check system for Fakstins Pharmacy")
        # Create a database connection
        self.conn = sqlite3.connect('inventory.db')
        self.create_table()
        # Search functionality
        self.label_search = ttk.Label(root, text="Search Item:")
        self.entry_search = ttk.Entry(root)
        self.btn_search = ttk.Button(root, text="Search", command=self.search_inventory)
        self.label_search.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.entry_search.grid(row=0, column=3, padx=5, pady=5)
        self.btn_search.grid(row=0, column=4, pady=5)
        # GUI Components
        self.label_item = ttk.Label(root, text="Item:")
        self.entry_item = ttk.Entry(root)
        self.label_cartons = ttk.Label(root, text="Cartons:")
        self.entry_cartons = ttk.Entry(root, validate="key", validatecommand=(root.register(self.validate_quantity), "%P"))
        self.label_pieces_per_carton = ttk.Label(root, text="Pieces per Carton:")
        self.entry_pieces_per_carton = ttk.Entry(root, validate="key", validatecommand=(root.register(self.validate_quantity), "%P"))
        self.label_pieces = ttk.Label(root, text="Pieces:")
        self.entry_pieces = ttk.Entry(root, validate="key", validatecommand=(root.register(self.validate_quantity), "%P"))
        self.label_price = ttk.Label(root, text="Price per Piece:")
        self.entry_price = ttk.Entry(root, validate="key", validatecommand=(root.register(self.validate_price), "%P"))
        self.label_date = ttk.Label(root, text="Date:")
        self.entry_date = ttk.Entry(root)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.btn_add = ttk.Button(root, text="Add to Inventory", command=self.add_to_inventory)
        self.btn_remove = ttk.Button(root, text="Remove from Inventory", command=self.remove_from_inventory)
        self.tree = ttk.Treeview(root, columns=('Item', 'Cartons', 'Pieces per Carton', 'Pieces', 'Price per Piece', 'Total Cost'), show='headings')
        self.tree.heading('Item', text='Item')
        self.tree.heading('Cartons', text='Cartons')
        self.tree.heading('Pieces per Carton', text='Pieces per Carton')
        self.tree.heading('Pieces', text='Pieces')
        self.tree.heading('Price per Piece', text='Price per Piece')
        self.tree.heading('Total Cost', text='Total Cost')
        self.display_inventory()
        # Layout
        self.label_item.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_item.grid(row=0, column=1, padx=5, pady=5)
        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=1, columnspan=2, sticky="ew", pady=10)
        self.label_cartons.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_cartons.grid(row=2, column=1, padx=5, pady=5)
        self.label_pieces_per_carton.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_pieces_per_carton.grid(row=3, column=1, padx=5, pady=5)
        self.label_pieces.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_pieces.grid(row=4, column=1, padx=5, pady=5)
        self.label_price.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_price.grid(row=5, column=1, padx=5, pady=5)
        self.label_date.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_date.grid(row=6, column=1, padx=5, pady=5)
        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=7, columnspan=2, sticky="ew", pady=10)
        self.btn_add.grid(row=8, column=0, columnspan=2, pady=10)
        self.btn_remove.grid(row=9, column=0, columnspan=2, pady=10)
        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=10, columnspan=2, sticky="ew", pady=10)
        self.tree.grid(row=11, column=0, columnspan=2, pady=10)
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY,
                item TEXT NOT NULL,
                cartons INTEGER NOT NULL,
                pieces_per_carton INTEGER NOT NULL,
                pieces INTEGER NOT NULL,
                price_per_piece REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    def add_to_inventory(self):
        item = self.entry_item.get()
        cartons = self.entry_cartons.get()
        pieces_per_carton = self.entry_pieces_per_carton.get()
        pieces = self.entry_pieces.get()
        price_per_piece = self.entry_price.get()
        date = self.entry_date.get()
        if item and cartons and pieces_per_carton and pieces and price_per_piece and date:
            total_cost = ((int(cartons) * int(pieces_per_carton)) + int(pieces) )* float(price_per_piece)
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO inventory (item, cartons, pieces_per_carton, pieces, price_per_piece, date) VALUES (?, ?, ?, ?, ?, ?)",
            (item, cartons, pieces_per_carton, pieces, price_per_piece, date))
            self.conn.commit()
            self.display_inventory()
    def remove_from_inventory(self):
        item = self.entry_item.get()
        cartons = self.entry_cartons.get()
        pieces = self.entry_pieces.get()
        if item and cartons and pieces:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE item=?", (item,))
            result = cursor.fetchone()
            if result and result[2] >= int(cartons) and (result[3] > int(pieces) or result[2] > 1):
                # If there are enough cartons or pieces to be removed
                if int(cartons) > 0:
                    cursor.execute("UPDATE inventory SET cartons=cartons-? WHERE item=?", (cartons, item))
                if int(pieces) > 0:
                    cursor.execute("UPDATE inventory SET pieces=pieces-? WHERE item=?", (pieces, item))
                
                self.conn.commit()
                self.display_inventory()
            else:
                print("Error: Insufficient quantity in inventory.")
    def display_inventory(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        # Clear the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Insert data into the treeview
        for row in rows:
            total_cost = ((row[2] * row[3]) + row[4]) * row[5]
            self.tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], f'₵{row[5]:,.2f}', f'₵{total_cost:,.2f}'))
    def validate_quantity(self, new_value):
        return new_value.isdigit() or new_value == ""
    def validate_price(self, new_value):
        try:
            float(new_value)
            return True
        except ValueError:
            return False
    def validate_cost(self, new_value):
        try:
            float(new_value)
            return True
        except ValueError:
            return False
    def search_inventory(self):
        search_term = self.entry_search.get()
        if search_term:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE item LIKE ?", (f'%{search_term}%',))
            rows = cursor.fetchall()
            for row in self.tree.get_children():
                self.tree.delete(row)
            for row in rows:
                total_cost = ((row[2] * row[3]) + row[4]) * row[5]
                self.tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], f'₵{row[5]:,.2f}', f'₵{total_cost:,.2f}'))
    def edit_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            print("Error: Please select an item from the inventory.")
            return
        item = self.tree.item(selected_item, 'values')[0]
        cartons = self.tree.item(selected_item, 'values')[1]
        pieces_per_carton = self.tree.item(selected_item, 'values')[2]
        pieces = self.tree.item(selected_item, 'values')[3]
        price_per_piece = self.tree.item(selected_item, 'values')[4]
        date = self.tree.item(selected_item, 'values')[5]
        # Populate the entry widgets with the selected item's values
        self.entry_item.delete(0, tk.END)
        self.entry_item.insert(0, item)
        self.entry_cartons.delete(0, tk.END)
        self.entry_cartons.insert(0, cartons)
        self.entry_pieces_per_carton.delete(0, tk.END)
        self.entry_pieces_per_carton.insert(0, pieces_per_carton)
        self.entry_pieces.delete(0, tk.END)
        self.entry_pieces.insert(0, pieces)
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, price_per_piece)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, date)
    def search_inventory(self):
        search_term = self.entry_search.get()
        if search_term:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE item LIKE ?", (f'%{search_term}%',))
            rows = cursor.fetchall()    
            for row in self.tree.get_children():
                self.tree.delete(row)
            for row in rows:
                total_cost = ((row[2] * row[3]) + row[4]) * row[5]
                self.tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], f'₵{row[5]:,.2f}', f'₵{total_cost:,.2f}'))
    def edit_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            print("Error: Please select an item from the inventory.")
            return
        item = self.tree.item(selected_item, 'values')[0]
        cartons = self.tree.item(selected_item, 'values')[1]
        pieces_per_carton = self.tree.item(selected_item, 'values')[2]
        pieces = self.tree.item(selected_item, 'values')[3]
        price_per_piece = self.tree.item(selected_item, 'values')[4]
        date = self.tree.item(selected_item, 'values')[5]
        # Populate the entry widgets with the selected item's values
        self.entry_item.delete(0, tk.END)
        self.entry_item.insert(0, item)

        self.entry_cartons.delete(0, tk.END)
        self.entry_cartons.insert(0, cartons)

        self.entry_pieces_per_carton.delete(0, tk.END)
        self.entry_pieces_per_carton.insert(0, pieces_per_carton)

        self.entry_pieces.delete(0, tk.END)
        self.entry_pieces.insert(0, pieces)

        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, price_per_piece)

        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, date)
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()