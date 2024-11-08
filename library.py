from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
import mysql.connector
import sys

class LibraryDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Library")
        self.setGeometry(100, 100, 500, 400)

        self.db = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin",
            database="mydb"
        )
        self.cursor = self.db.cursor()

        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Book Name")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Author")
        self.page_count_input = QLineEdit()
        self.page_count_input.setPlaceholderText("Page Count")

        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Author:"))
        form_layout.addWidget(self.author_input)
        form_layout.addWidget(QLabel("Page Count:"))
        form_layout.addWidget(self.page_count_input)

        self.book_list = QListWidget()
        self.book_list.itemClicked.connect(self.on_book_select)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_book)

        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_book)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_book)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.book_list)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.load_books()

    def load_books(self):
        self.book_list.clear()
        self.cursor.execute("SELECT id, name, author, page_count FROM books")
        for (id, name, author, page_count) in self.cursor.fetchall():
            self.book_list.addItem(f"{id} - {name} - {author} - {page_count}")

    def add_book(self):
        name = self.name_input.text()
        author = self.author_input.text()
        page_count = self.page_count_input.text()

        if name and author and page_count:
            try:
                self.cursor.execute(
                    "INSERT INTO books (name, author, page_count) VALUES (%s, %s, %s)",
                    (name, author, page_count)
                )
                self.db.commit()
                self.clear_inputs()
                self.load_books()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Failed to add book: {err}")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all fields")

    def update_book(self):
        selected_item = self.book_list.currentItem()
        if selected_item:
            book_id = int(selected_item.text().split(" - ")[0])
            name = self.name_input.text()
            author = self.author_input.text()
            page_count = self.page_count_input.text()

            if name and author and page_count:
                try:
                    self.cursor.execute(
                        "UPDATE books SET name = %s, author = %s, page_count = %s WHERE id = %s",
                        (name, author, page_count, book_id)
                    )
                    self.db.commit()
                    self.clear_inputs()
                    self.load_books()
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Failed to update book: {err}")
            else:
                QMessageBox.warning(self, "Input Error", "Please fill all fields")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a book to update")

    def delete_book(self):
        selected_item = self.book_list.currentItem()
        if selected_item:
            book_id = int(selected_item.text().split(" - ")[0])
            try:
                self.cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                self.db.commit()
                self.clear_inputs()
                self.load_books()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Failed to delete book: {err}")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a book to delete")

    def on_book_select(self, item):
        book_data = item.text().split(" - ")
        if len(book_data) == 4:
            self.name_input.setText(book_data[1])
            self.author_input.setText(book_data[2])
            self.page_count_input.setText(book_data[3])

    def clear_inputs(self):
        self.name_input.clear()
        self.author_input.clear()
        self.page_count_input.clear()

    def closeEvent(self, event):
        self.cursor.close()
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = LibraryDialog()
    dialog.show()
    sys.exit(app.exec_())
