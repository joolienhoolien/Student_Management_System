import sys
import sqlite3
import PyQt6
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QComboBox, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Manage System")

        #Menu Bar
        file_menu_item = self.menuBar().addMenu("&File")
        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        help_menu_item = self.menuBar().addMenu("&Help")
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        #Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Course", "Phone"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.load_data()


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