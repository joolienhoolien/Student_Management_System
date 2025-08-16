import sys
from idlelib.help_about import AboutDialog
from idlelib.search import SearchDialog

import PyQt6
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QComboBox, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QToolBar, QStatusBar, QMessageBox
import pymysql

class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="mypassword", database="school"):
        self.host=host
        self.user=user
        self.password=password
        self.database=database

    def connect(self):
        connection = pymysql.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection

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
        about_action.triggered.connect(self.about)

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
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students;")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for i, row in enumerate(result):
            self.table.insertRow(i)
            for j, col in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(col)))
        connection.close()

        self.table.setCurrentIndex(QModelIndex())
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

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

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        Student management system which is free to use and modify for your personal uses.
        """
        self.setText(content)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #Access selected row
        selected_row_index = main_window.table.currentRow()

        #Student ID
        self.student_id = main_window.table.item(selected_row_index, 0)

        #Student name
        student_name = main_window.table.item(selected_row_index, 1).text()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Courses
        course_name = main_window.table.item(selected_row_index, 2).text()
        self.course_name = QComboBox()
        courses = ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106"]
        self.course_name.setPlaceholderText("Select Course")
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        #Phone
        phone_number = main_window.table.item(selected_row_index, 3).text()
        self.phone_number = QLineEdit(phone_number)
        self.phone_number.setPlaceholderText("Phone")
        layout.addWidget(self.phone_number)

        #Update button
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update(self):
        student_id = self.student_id.text()
        student_name = self.student_name.text()
        course_name = self.course_name.itemText(self.course_name.currentIndex())
        phone_number = self.phone_number.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE Students "
                       "SET name = %s, course = %s, mobile = %s"
                       "WHERE ID = %s", (student_name, course_name, phone_number, student_id))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()
        self.close()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Record")
        self.setFixedWidth(300)
        self.setFixedHeight(100)

        grid = QGridLayout()

        #Access selected row
        selected_row_index = main_window.table.currentRow()
        self.student_id = main_window.table.item(selected_row_index, 0)
        self.student_name = main_window.table.item(selected_row_index, 1)

        are_you_sure_label = QLabel("Are you sure you want to delete this record?")
        grid.addWidget(are_you_sure_label, 0, 0, 1, 2)

        student_name_label = QLabel(f"Student Name: {self.student_name.text()}")
        grid.addWidget(student_name_label, 1, 0, 1, 2)

        yes_button = QPushButton("YES")
        yes_button.clicked.connect(self.delete)
        grid.addWidget(yes_button, 2, 0)

        no_button = QPushButton("NO")
        no_button.clicked.connect(self.close)
        grid.addWidget(no_button, 2, 1)

        self.setLayout(grid)

    def delete(self):
        student_name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Students WHERE ID = %s", (self.student_id.text(),))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success!")
        confirmation_message.setText(f"{student_name} deleted successfully!")
        confirmation_message.exec()

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
        items = main_window.table.findItems(student_name, Qt.MatchFlag.MatchFixedString)
        # Deselect all previously selected items
        for item in main_window.table.selectedItems():
            item.setSelected(False)

        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        self.close()

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
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Students (name, course, mobile) VALUES (%s, %s, %s)",
                       (student_name, course_name, phone))
        connection.commit()
        cursor.close()
        connection.close()

        main_window.load_data()
        self.close()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())