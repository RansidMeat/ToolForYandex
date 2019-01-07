import math
import datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from mainWindow import Ui_MainWindow
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from pycbrf import ExchangeRates, Banks


Bd = declarative_base()


class Note(Bd):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    text = Column(String(1000), nullable=False)
    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)


engine = create_engine('sqlite:///BD.db')
Bd.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

_ACTIVE_NOTES = {}

num1 = 0
num2 = 0
char = ""


def create_new_note():
    MainWindow()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.show()

        if obj:
            self.obj = obj
            self.load()
        else:
            self.obj = Note()
            self.save()

        self.closeButton.pressed.connect(self.delete_window)
        self.moreButton.pressed.connect(create_new_note)
        self.textEdit.textChanged.connect(self.save)

        self._drag_active = False
        today = datetime.datetime.now()
        str22 = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
        rates = ExchangeRates(str22, locale_en=True)
        rates.dates_match

        self.label.setText(str(rates['USD'].value)[:4] + "$" + " " + str(rates['EUR'].value)[:4] + "€")
        if len(str(today.minute))==2:
            self.label_2.setText("Time: " + str(today.hour) + ":" + str(today.minute))
        else:
            self.label_2.setText("Time: 0" + str(today.hour) + ":0" + str(today.minute))
        self.label_3.setText("Date: " + str(today.month) + "-" + str(today.day))

        for n in range(0, 10):
            getattr(self, 'pushButton_n%s' % n).pressed.connect(lambda v=n: self.input_number(v))

        self.pushButton_add.pressed.connect(lambda: self.equals("+"))
        self.pushButton_sub.pressed.connect(lambda: self.equals("-"))
        self.pushButton_mul.pressed.connect(lambda: self.equals("*"))
        self.pushButton_div.pressed.connect(lambda: self.equals("/"))
        self.pushButton_cvad.pressed.connect(lambda: self.equals("2"))
        self.pushButton_cor.pressed.connect(lambda: self.equals("/2"))
        self.pushButton_eq.pressed.connect(lambda: self.equals("="))
        self.pushButton_ac.pressed.connect(lambda: self.input_number("del"))

    def load(self):
        self.move(self.obj.x, self.obj.y)
        self.textEdit.setHtml(self.obj.text)
        _ACTIVE_NOTES[self.obj.id] = self

    def save(self):
        self.obj.x = self.x()
        self.obj.y = self.y()
        self.obj.text = self.textEdit.toHtml()
        session.add(self.obj)
        session.commit()
        _ACTIVE_NOTES[self.obj.id] = self

    def mousePressEvent(self, e):
        self.previous_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        delta = e.globalPos() - self.previous_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.previous_pos = e.globalPos()

        self._drag_active = True

    def mouseReleaseEvent(self, e):
        if self._drag_active:
            self.save()
            self._drag_active = False

    def delete_window(self):
        result = QMessageBox.question(self, "Удалить?", "Вы уверены, что хотите удалить? ")
        if result == QMessageBox.Yes:
            session.delete(self.obj)
            session.commit()
            self.close()

    def input_number(self, n):
        global num1, num2, char
        if n == "del":
            num1, num2 = 0, 0
            self.display(0)
        else:
            num1 = int(str(num1) + str(n))
            self.display(num1)

    def equals(self, _str):
        global num1, num2, char
        if _str == "+":
            num2, num1, char = num1, 0, "+"
            self.display(num2)
        elif _str == "-":
            num2, num1, char = num1, 0, "-"
            self.display(num2)
        elif _str == "*":
            num2, num1, char = num1, 0, "*"
            self.display(num2)
        elif _str == "/":
            num2, num1, char = num1, 0, "/"
            self.display(num2)
        elif _str == "2":
            num2, num1, char = num1, 0, "2"
            self.equals("=")
        elif _str == "/2":
            num2, num1, char = num1, 0, "/2"
            self.display(math.sqrt(num2))
        elif _str == "=":
            if char == "+":
                self.display(int(num1) + int(num2))
            elif char == "-":
                self.display(int(num2) - int(num1))
            elif char == "*":
                self.display(int(num1) * int(num2))
            elif char == "/":
                if num1 != 0:
                    self.display(int(num2) / int(num1))
            elif char == "2":
                self.display(int(num2) ** 2)

    def display(self, arg):
        self.lcdNumber.display(arg)


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Brown Note")
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(0, 0, 0))
    palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0))
    app.setPalette(palette)

    existing_notes = session.query(Note).all()

    if len(existing_notes) == 0:
        MainWindow()
    else:
        for note in existing_notes:
            MainWindow(obj=note)

    app.exec_()
