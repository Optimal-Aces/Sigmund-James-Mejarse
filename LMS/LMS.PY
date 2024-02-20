import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3

class Library:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY,
                            title TEXT,
                            author TEXT,
                            pages INTEGER,
                            borrower TEXT,
                            borrowed_datetime TEXT,
                            return_datetime TEXT,
                            status TEXT
                            )''')
        self.conn.commit()

    def display_available_books(self):
        self.cur.execute("SELECT id, title, author, pages, COUNT(*) AS amount_available FROM books WHERE status='Available' GROUP BY title")
        books = self.cur.fetchall()
        if not books:
            return "No books available in the library."
        else:
            book_list = "Available Books:\n"
            for book in books:
                book_list += f"Code: {book[0]}, Title: {book[1]}, Author: {book[2]}, Pages: {book[3]}, Amount Available: {book[4]}\n"
            return book_list

    def display_borrowed_books(self):
        self.cur.execute("SELECT id, borrower, title, return_datetime FROM books WHERE status='Borrowed'")
        books = self.cur.fetchall()
        if not books:
            return "No books are currently borrowed."
        else:
            book_list = "Borrowed Books:\n"
            for book in books:
                book_list += f"Code: {book[0]}, Borrower: {book[1]}, Book: {book[2]}, Return Date: {book[3]}\n"
            return book_list

    def add_book(self, title, author, pages):
        try:
            self.cur.execute("INSERT INTO books (title, author, pages, status) VALUES (?, ?, ?, ?)", (title, author, pages, 'Available'))
            self.conn.commit()
            return f"{title} has been added to the library."
        except Exception as e:
            return f"Error occurred while adding book: {e}"

    def borrow_book(self, book_id, borrower):
        borrow_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return_datetime = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')  # Return after 7 days
        try:
            self.cur.execute("UPDATE books SET borrower=?, borrowed_datetime=?, return_datetime=?, status=? WHERE id=?", 
                             (borrower, borrow_datetime, return_datetime, 'Borrowed', book_id))
            self.conn.commit()
            return f"{borrower} has borrowed the book with ID {book_id}."
        except Exception as e:
            return f"Error occurred while borrowing book: {e}"

    def return_book(self, book_id):
        self.cur.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.cur.fetchone()
        if not book:
            return f"Book with ID {book_id} is not a valid book."
        if book[7] == 'Available':
            return f"Book with ID {book_id} is already available in the library."
        borrow_datetime = datetime.strptime(book[5], '%Y-%m-%d %H:%M:%S')
        return_datetime = datetime.strptime(book[6], '%Y-%m-%d %H:%M:%S')
        return_date = datetime.now()
        if return_date > return_datetime:
            return f"Book with ID {book_id} is returned late."
        else:
            self.cur.execute("UPDATE books SET borrower=NULL, borrowed_datetime=NULL, return_datetime=NULL, status='Available' WHERE id=?", (book_id,))
            self.conn.commit()  # Commit the changes to the database
            return f"Book with ID {book_id} has been returned successfully."

    def delete_book(self, book_id):
        try:
            self.cur.execute("DELETE FROM books WHERE id = ?", (book_id,))
            self.conn.commit()
            return f"Book with ID {book_id} has been deleted."
        except Exception as e:
            return f"Error occurred while deleting book: {e}"

    def __del__(self):
        self.conn.close()


def display_available_books_command():
    result = library.display_available_books()
    if result:
        book_info_text.config(state=tk.NORMAL)
        book_info_text.delete('1.0', tk.END)
        book_info_text.insert(tk.END, result)
        book_info_text.config(state=tk.DISABLED)
    else:
        book_info_text.config(state=tk.NORMAL)
        book_info_text.delete('1.0', tk.END)
        book_info_text.insert(tk.END, "No books are currently available in the library.")
        book_info_text.config(state=tk.DISABLED)

def display_borrowed_books_command():
    result = library.display_borrowed_books()
    if result:
        borrowed_books_text.config(state=tk.NORMAL)
        borrowed_books_text.delete('1.0', tk.END)
        borrowed_books_text.insert(tk.END, result)
        borrowed_books_text.config(state=tk.DISABLED)
    else:
        borrowed_books_text.config(state=tk.NORMAL)
        borrowed_books_text.delete('1.0', tk.END)
        borrowed_books_text.insert(tk.END, "No books are currently borrowed.")
        borrowed_books_text.config(state=tk.DISABLED)

def add_book_command():
    title = title_entry.get()
    author = author_entry.get()
    pages = int(pages_entry.get())
    result = library.add_book(title, author, pages)
    messagebox.showinfo("Add Book", result)

def borrow_book_command():
    book_id = int(borrow_book_id_entry.get())
    borrower = borrower_entry.get()
    result = library.borrow_book(book_id, borrower)
    messagebox.showinfo("Borrow Book", result)

def return_book_command():
    book_id = int(return_book_id_entry.get())
    result = library.return_book(book_id)
    messagebox.showinfo("Return Book", result)
    # Update the display after returning the book
    update_info_display()

def delete_book_command():
    book_id = int(delete_book_id_entry.get())
    result = library.delete_book(book_id)
    messagebox.showinfo("Delete Book", result)

def update_info_display():
    available_books = library.display_available_books()
    if available_books:
        book_info_text.config(state=tk.NORMAL)
        book_info_text.delete('1.0', tk.END)
        book_info_text.insert(tk.END, available_books)
        book_info_text.config(state=tk.DISABLED)

    borrowed_books = library.display_borrowed_books()
    if borrowed_books:
        borrowed_books_text.config(state=tk.NORMAL)
        borrowed_books_text.delete('1.0', tk.END)
        borrowed_books_text.insert(tk.END, borrowed_books)
        borrowed_books_text.config(state=tk.DISABLED)

def display_borrowed_books_window():
    borrowed_books_window = tk.Toplevel()
    borrowed_books_window.title("Borrowed Books")
    borrowed_books_window.geometry("400x300")

    borrowed_books_label = ttk.Label(borrowed_books_window, text="Borrowed Books:")
    borrowed_books_label.pack(pady=10)

    borrowed_books_text = tk.Text(borrowed_books_window, height=10, width=50)
    borrowed_books_text.pack()

    borrowed_books = library.display_borrowed_books()
    borrowed_books_text.insert(tk.END, borrowed_books)

    borrowed_books_text.config(state=tk.DISABLED)

db_file = "library.db"
library = Library(db_file)

window = tk.Tk()
window.title("Library Management System")
window.geometry("1000x400")

style = ttk.Style()
style.theme_use("clam")  # Choose a modern theme, "clam" is one of them

title_label = ttk.Label(window, text="Title:")
title_label.grid(row=0, column=0, padx=10, pady=5)
title_entry = ttk.Entry(window)
title_entry.grid(row=0, column=1, padx=10, pady=5)

author_label = ttk.Label(window, text="Author:")
author_label.grid(row=1, column=0, padx=10, pady=5)
author_entry = ttk.Entry(window)
author_entry.grid(row=1, column=1, padx=10, pady=5)

pages_label = ttk.Label(window, text="Pages:")
pages_label.grid(row=2, column=0, padx=10, pady=5)
pages_entry = ttk.Entry(window)
pages_entry.grid(row=2, column=1, padx=10, pady=5)

add_book_button = ttk.Button(window, text="Add Book", command=add_book_command)
add_book_button.grid(row=3, column=0, columnspan=2, pady=10)

display_available_books_button = ttk.Button(window, text="Display Available Books", command=display_available_books_command)
display_available_books_button.grid(row=4, column=0, columnspan=2, pady=10)

borrow_book_id_label = ttk.Label(window, text="Book ID to Borrow:")
borrow_book_id_label.grid(row=5, column=0, padx=10, pady=5)
borrow_book_id_entry = ttk.Entry(window)
borrow_book_id_entry.grid(row=5, column=1, padx=10, pady=5)

borrower_label = ttk.Label(window, text="Borrower:")
borrower_label.grid(row=6, column=0, padx=10, pady=5)
borrower_entry = ttk.Entry(window)
borrower_entry.grid(row=6, column=1, padx=10, pady=5)

borrow_book_button = ttk.Button(window, text="Borrow Book", command=borrow_book_command)
borrow_book_button.grid(row=7, column=0, columnspan=2, pady=10)

return_book_id_label = ttk.Label(window, text="Book ID to Return:")
return_book_id_label.grid(row=8, column=0, padx=10, pady=5)
return_book_id_entry = ttk.Entry(window)
return_book_id_entry.grid(row=8, column=1, padx=10, pady=5)

return_book_button = ttk.Button(window, text="Return Book", command=return_book_command)
return_book_button.grid(row=9, column=0, columnspan=2, pady=10)

# Delete Book Section
delete_book_id_label = ttk.Label(window, text="Book ID to Delete:")
delete_book_id_label.grid(row=10, column=0, padx=10, pady=5)
delete_book_id_entry = ttk.Entry(window)
delete_book_id_entry.grid(row=10, column=1, padx=10, pady=5)

delete_book_button = ttk.Button(window, text="Delete Book", command=delete_book_command)
delete_book_button.grid(row=11, column=0, columnspan=2, pady=10)

# Right side info display
available_books_label = ttk.Label(window, text="Available Books:")
available_books_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

book_info_text = tk.Text(window, height=10, width=50, state=tk.DISABLED)
book_info_text.grid(row=1, column=2, rowspan=5, padx=10, pady=5, sticky=tk.W)

borrowed_books_label = ttk.Label(window, text="Borrowed Books:")
borrowed_books_label.grid(row=6, column=2, padx=10, pady=5, sticky=tk.W)

borrowed_books_text = tk.Text(window, height=10, width=50, state=tk.DISABLED)
borrowed_books_text.grid(row=7, column=2, rowspan=12, padx=10, pady=5, sticky=tk.W)

update_info_display()

view_borrowed_books_button = ttk.Button(window, text="View Borrowed Books", command=display_borrowed_books_window)
view_borrowed_books_button.grid(row=12, column=2, pady=10)

window.mainloop()
