import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt, QTimer, QPointF, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QFont

class Rura:
    def __init__(self, punkty, grubosc=12, kolor=QColor(100, 100, 100)):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty] # lista punktow rur
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False # czy w rurze przeplywa ciecz

    # stan przeplywu cieczy
    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2:
            return
        
        path = QPainterPath() # sciezka rysowania rury
        path.moveTo(self.punkty[0]) # punkt poczatkowy rury
        for p in self.punkty[1:]:
            path.lineTo(p)

        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)
        painter.setPen(pen_rura) 
        painter.drawPath(path) # rura jest rysowana

        # jezeli ciecz plynie, rysowana jest wewnatrz rury
        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)

class Pompa:
    def __init__(self, x, y, r=22):
        self.x, self.y = x, y
        self.r = r
        self.kat = 0 # poczatkowy kat obrotu wirnika pompy

    # obracanie wirnika pompy
    def obroc(self, predkosc):
        self.kat = (self.kat + predkosc * 15) % 360 # Zwiększamy kąt obrotu zależnie od prędkości

    def draw(self, painter):
        # rysowanie obudowy pompy
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(70, 130, 180))
        painter.drawEllipse(int(self.x - self.r), int(self.y - self.r), int(self.r*2), int(self.r*2))
        
        # rysowanie wirnika
        painter.setPen(QPen(Qt.white, 3))
        for i in range(4):
            kat_rad = math.radians(self.kat + i * 90) # obliczanie katu ramienia wirnika

            # obliczanie wspolrzednych konca ramienia
            x2 = self.x + (self.r - 6) * math.cos(kat_rad)
            y2 = self.y + (self.r - 6) * math.sin(kat_rad)

            painter.drawLine(int(self.x), int(self.y), int(x2), int(y2))  # rysowanie ramienia wirnika

class Zbiornik:
    def __init__(self, x, y, width=100, height=150, nazwa=""):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.nazwa = nazwa
        self.pojemnosc = 100.0 # maksymalna pojemnosc zbiornika
        self.aktualna_ilosc = 0.0 # aktualna ilosc cieczy

    # dodawanie cieczy do zbiornika
    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        
        # aktualizacja ilosci cieczy
        self.aktualna_ilosc += dodano
        return dodano

    # usuwanie cieczy
    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        return usunieto

    # rysowanie zbiornika
    def draw(self, painter):
        procent = self.aktualna_ilosc / self.pojemnosc

        # jesli zbiornik nie jest pusty, wtedy rysowana jest ciecz
        if procent > 0:
            # wysokosc slupa cieczy
            h_wody = (self.height - 4) * procent

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255))

            # rysowanie cieczy
            painter.drawRect(
                int(self.x + 2),
                int(self.y + self.height - h_wody - 2),
                int(self.width - 4),
                int(h_wody)
            )

        # obramowanie zbiornika
        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(Qt.NoBrush)
        rect = QRect(int(self.x), int(self.y), int(self.width), int(self.height))
        painter.drawRect(rect)

        # tekst wewnatrz zbiornika
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 10, QFont.Bold))
        display_text = f"{self.nazwa}\n{int(self.aktualna_ilosc)}%"
        painter.drawText(rect, Qt.AlignCenter, display_text)

class SystemProcesowy(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulacja Przepływu - Projekt")
        self.setFixedSize(1000, 900) # Zwiększona wysokość
        self.setStyleSheet("background-color: #f0f0f0;") 

        ox, oy = 100, 30

        # inicjalizacja utworzonych obiektów
        self.z1 = Zbiornik(100+ox, 50+oy, nazwa="Z1")
        self.z2 = Zbiornik(400+ox, 300+oy, nazwa="Z2")
        self.z3 = Zbiornik(200+ox, 550+oy, nazwa="Z3")
        self.z4 = Zbiornik(600+ox, 550+oy, nazwa="Z4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        self.pompa = Pompa(300+ox, 215+oy)

        self.r1 = Rura([(150+ox, 200+oy), (150+ox, 215+oy), (450+ox, 215+oy), (450+ox, 300+oy)])
        self.r2 = Rura([(450+ox, 450+oy), (450+ox, 500+oy), (250+ox, 500+oy), (250+ox, 550+oy)])
        self.r3 = Rura([(450+ox, 450+oy), (450+ox, 500+oy), (650+ox, 500+oy), (650+ox, 550+oy)])
        self.rury = [self.r1, self.r2, self.r3]

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_procesu)
        self.running = False

    def init_ui(self):
        style_input = "background-color: white; border: 1px solid #ccc; font-size: 14px; padding: 2px;"
        
        # inicjalizacja danych przez uzytkownika: poziom i predkosc
        lbl_z1 = QLabel("Poziom Zbiornika 1 (%)", self)
        lbl_z1.setGeometry(50, 750, 200, 20)
        self.in_z1 = QLineEdit("100", self)
        self.in_z1.setGeometry(50, 775, 150, 30)
        self.in_z1.setStyleSheet(style_input)

        lbl_speed = QLabel("Prędkość przepływu", self)
        lbl_speed.setGeometry(50, 815, 200, 20)
        self.in_speed = QLineEdit("1.0", self)
        self.in_speed.setGeometry(50, 840, 150, 30)
        self.in_speed.setStyleSheet(style_input)

        # przyciski: START i RESET
        self.btn_start = QPushButton("START", self)
        self.btn_start.setGeometry(400, 790, 130, 50)
        self.btn_start.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 16px; border-radius: 8px;")
        self.btn_start.clicked.connect(self.uruchom_start)

        self.btn_reset = QPushButton("RESET", self)
        self.btn_reset.setGeometry(550, 790, 130, 50)
        self.btn_reset.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 16px; border-radius: 8px;")
        self.btn_reset.clicked.connect(self.uruchom_reset)

    def uruchom_start(self):
        try:
            self.speed = float(self.in_speed.text())
            # Pobranie wartości i ograniczenie jej do 0-100
            input_val = float(self.in_z1.text())
            walidowana_wartosc = max(0.0, min(100.0, input_val))
            
            # ustawienie/dolewanie wody do pierwszego zbiornika
            self.z1.aktualna_ilosc = walidowana_wartosc
            
            self.running = True
            if not self.timer.isActive():
                self.timer.start(30)
        except ValueError:
            pass

    def uruchom_reset(self):
        self.running = False
        self.timer.stop()
        for z in self.zbiorniki: z.aktualna_ilosc = 0
        for r in self.rury: r.ustaw_przeplyw(False)
        self.update()

    def logika_procesu(self):
        if not self.running: return

        # przeplyw cieczy ze zbiornika 1 do 2
        plynie1 = False
        if self.z1.aktualna_ilosc > 0 and self.z2.aktualna_ilosc < 100:
            v = self.z1.usun_ciecz(self.speed)
            self.z2.dodaj_ciecz(v)
            plynie1 = True
            self.pompa.obroc(self.speed)
        self.r1.ustaw_przeplyw(plynie1)

        # przeplyw cieczy ze zbiornika 2 do zboiorników 3 i 4
        plynie_dol = False
        if self.z2.aktualna_ilosc > 0:
            porcja = self.speed
            # przelewanie wody do zbiornika 3 i 4
            oddane = self.z3.dodaj_ciecz(porcja/2) + self.z4.dodaj_ciecz(porcja/2)
            if oddane > 0:
                self.z2.usun_ciecz(oddane)
                plynie_dol = True
            
        self.r2.ustaw_przeplyw(plynie_dol)
        self.r3.ustaw_przeplyw(plynie_dol)
        
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        for r in self.rury: r.draw(qp)
        self.pompa.draw(qp)
        for z in self.zbiorniki: z.draw(qp)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemProcesowy()
    window.show()
    sys.exit(app.exec_())