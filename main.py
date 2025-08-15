import sys
import sqlite3
from idlelib.search import SearchDialog

import PyQt6
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QComboBox, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QToolBar, QStatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        #Menu Bar
        file_menu_item = self.menuBar().addMenu("&File")
        add_student_action = QAction(QIcon("add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        help_menu_item = self.menuBar().addMenu("&Help")
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        edit_menu_item = self.menuBar().addMenu("&Edit")
        search_action = QAction(QIcon("search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        #Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        #Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


        #Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Course", "Phone"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.load_data()

        #Access cell clicked
        self.table.cellClicked.connect(self.cell_clicked)



    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM Students")
        self.table.setRowCount(0)
        for i, row in enumerate(result):
            self.table.insertRow(i)
            for j, col in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(col)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def cell_clicked(self):
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        self.status_bar.addWidget(edit_button)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)
        self.status_bar.addWidget(delete_button)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #Name dialog box
        self.student_name = QLineEdit(self)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        student_name = self.student_name.text()
        #connection = sqlite3.connect("database.db")
        #cursor = connection.cursor()
        #result = cursor.execute("SELECT * FROM Students WHERE name = ?", (student_name,))
        items = main_window.table.findItems(student_name, Qt.MatchFlag.MatchFixedString)
        # Deselect all previously selected items
        for item in main_window.table.selectedItems():
            item.setSelected(False)

        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        #cursor.close()
        #connection.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #Add student name
        self.student_name = QLineEdit(self)
        self.student_name.setPlaceholderText("Student Name")
        layout.addWidget(self.student_name)

        #Select Course
        self.course_name = QComboBox(self)
        courses = ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106"]
        self.course_name.setPlaceholderText("Select Course")
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #Add Phone Number
        self.phone = QLineEdit(self)
        self.phone.setPlaceholderText("Phone")
        layout.addWidget(self.phone)

        #Submit data to db
        submit_button = QPushButton(self)
        submit_button.setText("Submit")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        student_name = self.student_name.text()
        course_name = self.course_name.itemText(self.course_name.currentIndex())
        phone = self.phone.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Students (name, course, mobile) VALUES (?, ?, ?)",
                       (student_name, course_name, phone))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())