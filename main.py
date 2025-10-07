from datetime import datetime
from datetime import timedelta 
from abc import ABC, abstractmethod
from collections import defaultdict
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


LOG_FILE = "hotel.log"

def log(level: str, msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} - {level} - {msg}"
    print(line)
    file_open = None
    try:
        file_open = open(LOG_FILE, "a", encoding="utf-8")
        file_open.write(line + "\n")
    except IOError as e:
        print(f"{ts} - ERROR - Не удалось записать в лог-файл: {e}")
    finally:
        if file_open:
            file_open.close()

def info(msg: str): log("INFO", msg)
def warning(msg: str): log("WARNING", msg)
def error(msg: str): log("ERROR", msg)

class BaseHotelError(Exception): pass
class HotelBookingError(BaseHotelError): pass
class RoomNotAvailableError(HotelBookingError): pass
class InvalidGuestDataError(HotelBookingError): pass
class DataProcessingError(BaseHotelError): pass
class EmptyRoomListError(DataProcessingError): pass

def validate_guest_data(name: str, lastname: str):
    if not isinstance(name, str) or not name.strip():
        raise InvalidGuestDataError("Имя не должно быть пустой строкой")
    if not isinstance(lastname, str) or not lastname.strip():
        raise InvalidGuestDataError("Фамилия не должна быть пустой строкой")
    
    if len(name.strip()) < 2 or len(lastname.strip()) < 2:
        raise InvalidGuestDataError("Имя и фамилия должны быть от 2 символов")
    

class Person(ABC):
    def __init__(self, name, lastName, age=None):
        self.name = name
        self.lastName = lastName
        self.age = age

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def get_role(self):
        pass

    def get_full_name(self): 
        return f"{self.name} {self.lastName}"
    
    def __str__(self):
        return self.info()

    def __repr__(self):
        age_str = f", age={self.age}" if self.age is not None else ""
        return f"{self.__class__.__name__}('{self.name}', '{self.lastName}'{age_str})"
class Guest(Person):
    def __init__(self, name, lastName, age=None):
        self.reservations = []
        super().__init__(name, lastName, age) 
        info(f"Создан гость: {self.name} {self.lastName}")

    def add_reservation(self, reservation):
        self.reservations.append(reservation)

    def info(self):
        return f"Гость {self.name} {self.lastName}, бронирований: {len(self.reservations)}"

    def get_role(self):
        return "guest"
class Employee(Person):
    def __init__(self, name, lastName, position, _salary=0):
        super().__init__(name, lastName) 
        self.position = position
        self._salary = _salary 
        info(f"Создан сотрудник: {self.name} {self.lastName} ({self.position})")

    def get_full_name(self):
        return f"{self.lastName} {self.name} ({self.position})"

    def display_info(self, use_base_first=False):
        base_name = super().get_full_name() 
        derived_name = self.get_full_name() 
        salary_access = self._salary 
        
        info(f"Доступ к защищенному атрибуту _salary из Employee: {salary_access}₽")

        if use_base_first:
            return (f"1. Базовый (Person): {base_name}\n"
                    f"2. Производный (Employee): {derived_name}")
        else:
            return (f"1. Производный (Employee): {derived_name}\n"
                    f"2. Базовый (Person): {base_name}")

    def info(self):
        return f"Сотрудник {self.get_full_name()}, ЗП: {self._salary}₽"

    def get_role(self):
        return self.position
class Room:
    total_rooms = 0
    ROOM_TYPES = {"Single", "Double", "Suite", "Deluxe"}
    TAX_RATE = 0.18
    
    def __init__(self, room_number, room_type, price):
        if not Room.is_valid_room_type(room_type):
            raise ValueError(f"Неизвестный тип номера: {room_type}")
        self.room_number = int(room_number) 
        self.room_type = room_type
        self.price = float(price) 
        self.is_available = True
        Room.total_rooms += 1

    def __str__(self):
        return f"комната {self.room_number} ({self.room_type}), {self.price:.2f}₽, {'доступна' if self.is_available else 'недоступна'}"

    def __repr__(self):
        return f"Room({self.room_number}, '{self.room_type}', {self.price})"
        
    def __eq__(self, other):
        return isinstance(other, Room) and self.room_number == other.room_number
        
    def __lt__(self, other):
        if not isinstance(other, Room):
            return NotImplemented
        return self.price < other.price
        
    def __add__(self, other):
        if isinstance(other, Room):
            return self.price + other.price
        if isinstance(other, (int, float)):
            return self.price + other
        return NotImplemented
        
    def __mul__(self, nights):
        if isinstance(nights, (int, float)):
            return self.price * nights
        return NotImplemented
        
    def __contains__(self, room_type):
        return self.room_type.lower() == str(room_type).lower()

    @staticmethod
    def is_valid_room_type(room_type):
        return room_type in Room.ROOM_TYPES

    @staticmethod
    def calculate_total_price(base_price, nights=1, include_tax=True):
        total = base_price * nights
        if include_tax:
            total *= (1 + Room.TAX_RATE)
        return round(total, 2)

    @classmethod
    def get_room_statistics(cls):
        return {"total_rooms": cls.total_rooms,
                "available_types": cls.ROOM_TYPES,
                "tax_rate": cls.TAX_RATE}
class Reservation:
    def __init__(self, guest, room, check_in_date="N/A", check_out_date="N/A"):
        self.guest = guest
        self.room = room
        self.dates = (check_in_date, check_out_date)
        guest.add_reservation(self)
        room.is_available = False

    def __str__(self):
        return f"Бронь: {self.guest.name} {self.guest.lastName} / Room {self.room.room_number} / {self.dates[0]} - {self.dates[1]}"
        
    def __repr__(self):
        guest_repr = repr(self.guest)
        room_repr = repr(self.room)
        return (f"Reservation_Placeholder({guest_repr}, {room_repr}, "
                f"'{self.dates[0]}', '{self.dates[1]}')")
class RoomManager:
    def __init__(self):
        self.rooms_1d = []
        self.rooms_2d = []

    def add_room_1d(self, room: Room):
        self.rooms_1d.append(room)
        info(f"Добавлена комната в 1D массив: {room.room_number}")

    def set_rooms_2d(self, room_matrix: list[list[Room]]):
        self.rooms_2d = room_matrix
        info(f"Установлен 2D массив, размер: {len(room_matrix)}x{len(room_matrix[0]) if room_matrix and room_matrix[0] else 0}")
    
    def find_room_with_max_price(self) -> Room | None:
        if not self.rooms_2d or not any(row for row in self.rooms_2d):
            raise EmptyRoomListError("Двумерный список номеров пуст.")

        max_room = None
        max_price = -1

        for row in self.rooms_2d:
            for room in row:
                if room is not None and room.price > max_price:
                    max_price = room.price
                    max_room = room

        if max_room is None:
            raise DataProcessingError("Не удалось найти действительный объект Room.")
            
        return max_room
class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms_by_number = {}
        self.rooms_by_type = defaultdict(list)
        self.guests_dict = {}
        self.guests_set = set()
        self.reservations = []
        info(f"Создан отель: {self.name}")

    def add_room(self, room):
        self.rooms_by_number[room.room_number] = room
        self.rooms_by_type[room.room_type].append(room)
        info(f"Добавлена {room}")
        return room

    def find_guest(self, name, lastName):
        return self.guests_dict.get((name, lastName))

    def add_guest(self, guest):
        key = (guest.name, guest.lastName)
        if key not in self.guests_dict:
            self.guests_dict[key] = guest
            self.guests_set.add(key)
            info(f"Добавлен {guest}")
        else:
            info(f"Гость уже существует: {self.guests_dict[key]}")
        return self.guests_dict[key]

    def make_reservation(self, guest, room, check_in_date="N/A", check_out_date="N/A"):
        reservation = None
        try:
            if guest is None or not isinstance(guest, Guest):
                raise InvalidGuestDataError("Гость отсутствует или неверного типа")
            if room is None or not isinstance(room, Room):
                raise BaseHotelError("Комната отсутствует или неверного типа")
            if not room.is_available:
                raise RoomNotAvailableError(f"Номер {room.room_number} недоступен")
            
            reservation = Reservation(guest, room, check_in_date, check_out_date)
            self.reservations.append(reservation)
            info(f"Бронирование создано: {reservation}")
            return reservation
            
        except InvalidGuestDataError as e:
            error(f"Ошибка данных гостя: {e}")
            messagebox.showerror("Ошибка", f"Ошибка данных гостя: {e}")
        except RoomNotAvailableError as e:
            error(f"Номер недоступен: {e}")
            messagebox.showerror("Ошибка", f"Номер недоступен: {e}")
        except BaseHotelError as e:
            error(f"Общая ошибка отеля: {e}")
            messagebox.showerror("Ошибка", f"Общая ошибка отеля: {e}")
        except Exception as e:
            error(f"Неожиданная ошибка: {type(e).__name__}: {e}")
            messagebox.showerror("Ошибка", f"Неожиданная ошибка: {e}")
        finally:
            info(f"Завершение попытки бронирования. Результат: {'Успех' if reservation else 'Провал'}")
        
        return None
    
    def available_rooms(self):
        return [r for r in self.rooms_by_number.values() if r.is_available]
def Sort_guests_and_employees(hotel: Hotel):
    info("\n--- Демонстрация Задания 3: Лямбда-выражения ---")
    
    people = list(hotel.guests_dict.values())
    people.append(Employee("John", "Doe", "Porter", 30000))
    people.append(Employee("Jane", "Smith", "Admin", 75000))
    people.append(Guest("Xavier", "Guest", 65))

    sorted_by_name = sorted(people, key=lambda p: p.name)
    info(f"Сортировка по имени: {[p.name for p in sorted_by_name]}") 
    
    guests_only = list(filter(lambda p: p.get_role() == "guest", people))
    info(f"Только гости (роль 'guest'): {[p.name for p in guests_only]}")

    high_paid = [p for p in people if p.get_role() != 'guest' and p._salary > 50000]
    
    output_info = list(map(
        lambda e: f"{e.lastName} ({e.position}): {e._salary}₽", 
        high_paid
    ))
    info(f"Сотрудники с высокой ЗП: {output_info}")
class HotelApp(QWidget):
    def __init__(self, hotel: Hotel):
        super().__init__()
        self.hotel = hotel
        self.available_map = {}
        self.setWindowTitle("Grand Hotel Booking")
        self.setGeometry(100, 100, 450, 500)
        
        self.setup_ui()
        self.apply_styles()
        self.refresh_rooms()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        title_label = QLabel("Оформление бронирования")
        title_label.setObjectName("TitleLabel")
        main_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(10)
        
        self.entry_name = QLineEdit()
        self.entry_lastname = QLineEdit()
        self.entry_in = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.entry_out = QLineEdit((datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"))
        self.combobox_rooms = QComboBox()
        self.status_label = QLabel("Подготовка...")
        self.status_label.setObjectName("StatusLabel")

        fields = [
            ("Имя:", self.entry_name),
            ("Фамилия:", self.entry_lastname),
            ("Дата заезда:", self.entry_in),
            ("Дата выезда:", self.entry_out),
            ("Свободный номер:", self.combobox_rooms),
        ]
        
        for i, (label_text, widget) in enumerate(fields):
            label = QLabel(label_text)
            label.setObjectName("FormLabel")
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(widget, i, 1)

        main_layout.addLayout(form_layout)
        
        button_layout = QGridLayout()
        
        self.btn_refresh = QPushButton("Обновить номера")
        self.btn_book = QPushButton("Забронировать")
        self.btn_show_res = QPushButton("Показать брони")
        
        button_layout.addWidget(self.btn_refresh, 0, 0)
        button_layout.addWidget(self.btn_book, 0, 1)
        button_layout.addWidget(self.btn_show_res, 1, 0)
        
        main_layout.addLayout(button_layout)
        
        main_layout.addSpacing(15)
        main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        self.btn_refresh.clicked.connect(self.refresh_rooms)
        self.btn_book.clicked.connect(self.book_room)
        self.btn_show_res.clicked.connect(self.show_reservations)


    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #222; /* Светлый фон */
                color: #FFF;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 10pt;
            }
                           
            fields{
                color:#FFF;               
            }
            
            #TitleLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #FFF; /* Темно-синий заголовок */
                padding-bottom: 15px;
            }
            
            #FormLabel {
                font-weight: 500;
                color: #FFF;
            }

            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: white;
                selection-background-color: #353535;
                color: #222;
                font-weight: bold;
            }

            QPushButton {
                background-color: #353535;
                color: #FFF;
                border: none;
                padding: 10px;
                margin: 5px 0;
                border-radius: 6px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #656565;
            }
            
            QPushButton:pressed {
                background-color: #656565;
            }
            
            #StatusLabel {
                font-size: 10pt;
                color: #FFF;
                font-weight: 500;
                padding-top: 10px;
            }
        """)


    def refresh_rooms(self):
        available = self.hotel.available_rooms()
        self.available_map = {f"{r.room_number} — {r.room_type} ({r.price}₽)": r for r in available}
        choices = list(self.available_map.keys())
        
        self.combobox_rooms.clear()
        if choices:
            self.combobox_rooms.addItems(choices)
        
        info("Обновлён список свободных номеров")
        self.status_label.setText(f"Доступно номеров: {len(choices)}")

    def book_room(self):
        name = self.entry_name.text().strip()
        lastname = self.entry_lastname.text().strip()
        check_in = self.entry_in.text().strip()
        check_out = self.entry_out.text().strip()
        room_choice = self.combobox_rooms.currentText().strip()
        
        if not name or not lastname:
            QMessageBox.warning(self, "Ошибка", "Введите имя и фамилию.")
            return
        if not room_choice:
            QMessageBox.warning(self, "Ошибка", "Выберите свободный номер.")
            return

        try:
            validate_guest_data(name, lastname)
        except InvalidGuestDataError as e:
            QMessageBox.critical(self, "Ошибка данных", str(e))
            return
        
        room = self.available_map.get(room_choice)
        
        guest = self.hotel.find_guest(name, lastname)
        if guest is None:
            guest = Guest(name, lastname)
            self.hotel.add_guest(guest)

        reservation = self.hotel.make_reservation(guest, room, check_in, check_out)
        
        if reservation:
            nights = 1
            try:
                nights = max(1, (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days)
            except Exception:
                nights = 1
            
            total_with_tax = Room.calculate_total_price(room.price, nights)
            QMessageBox.information(
                self,
                "Успех бронирования!",
                f"Номер {room.room_number} успешно забронирован за {name} {lastname}.\n"
                f"Даты: {check_in} — {check_out}\n"
                f"Стоимость ({nights} ноч.): {total_with_tax}₽ (с налогом)"
            )
            self.refresh_rooms()
        else:
            warning("Неудачная попытка бронирования (через GUI)")

    def show_reservations(self):
        info("Пользователь запросил просмотр бронирований через GUI")
        if not self.hotel.reservations:
            QMessageBox.information(self, "Бронирования", "Бронирований нет.")
            return
            
        lines = []
        for idx, r in enumerate(self.hotel.reservations, start=1):
            lines.append(f"{idx}. {r.guest.name} {r.guest.lastName} — Номер {r.room.room_number} — {r.dates[0]} → {r.dates[1]}")
            
        text = "\n".join(lines)
        QMessageBox.information(self, "Существующие бронирования", text)
hotel = Hotel("Grand Hotel")
room1 = hotel.add_room(Room(101, "Single", 5000))
room2 = hotel.add_room(Room(102, "Double", 8000))
room3 = hotel.add_room(Room(201, "Suite", 15000))
room4 = hotel.add_room(Room(202, "Single", 5200))

info(f"Статистика по номерному фонду: {Room.get_room_statistics()}")

guest1 = hotel.add_guest(Guest("Alice", "Johnson", 30))
guest2 = hotel.add_guest(Guest("Bob", "Ross", 45))



room_mgr = RoomManager()
room_mgr.add_room_1d(room1)
room_mgr.add_room_1d(room3)
info(f"1D Массив (цены): {[r.price for r in room_mgr.rooms_1d]}")

rooms_2d_example = [
    [room4, room2], 
    [room3, hotel.add_room(Room(301, "Deluxe", 25000))]
]
room_mgr.set_rooms_2d(rooms_2d_example)


Sort_guests_and_employees(hotel)

app = QApplication(sys.argv)
ex = HotelApp(hotel)
ex.show()
sys.exit(app.exec_())