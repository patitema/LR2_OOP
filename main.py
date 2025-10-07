import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from abc import ABC, abstractmethod
from collections import defaultdict

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
        info(f"Создан Person (База): {self.name} {self.lastName}")

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

class HotelGUI:
    def __init__(self, hotel: Hotel):
        self.hotel = hotel
        self.root = tk.Tk()
        self.root.title("Hotel Booking — Быстрое бронирование")
        frm = ttk.Frame(self.root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")
        
        ttk.Label(frm, text="Имя:").grid(row=0, column=0, sticky="w")
        self.entry_name = ttk.Entry(frm, width=30)
        self.entry_name.grid(row=0, column=1, pady=4, sticky="ew")
        
        ttk.Label(frm, text="Фамилия:").grid(row=1, column=0, sticky="w")
        self.entry_lastname = ttk.Entry(frm, width=30)
        self.entry_lastname.grid(row=1, column=1, pady=4, sticky="ew")
        
        ttk.Label(frm, text="Дата заезда (опц.):").grid(row=2, column=0, sticky="w")
        self.entry_in = ttk.Entry(frm, width=30)
        self.entry_in.grid(row=2, column=1, pady=4, sticky="ew")
        self.entry_in.insert(0, "2025-09-10")
        
        ttk.Label(frm, text="Дата выезда (опц.):").grid(row=3, column=0, sticky="w")
        self.entry_out = ttk.Entry(frm, width=30)
        self.entry_out.grid(row=3, column=1, pady=4, sticky="ew")
        self.entry_out.insert(0, "2025-09-12")
        
        ttk.Label(frm, text="Свободный номер:").grid(row=4, column=0, sticky="w")
        self.room_var = tk.StringVar()
        self.combobox_rooms = ttk.Combobox(frm, textvariable=self.room_var, state="readonly", width=28)
        self.combobox_rooms.grid(row=4, column=1, pady=6, sticky="ew")
        
        self.btn_refresh = ttk.Button(frm, text="Обновить список свободных номеров", command=self.refresh_rooms)
        self.btn_refresh.grid(row=5, column=0, columnspan=2, pady=(6, 2), sticky="ew")
        
        self.btn_book = ttk.Button(frm, text="Забронировать", command=self.book_room)
        self.btn_book.grid(row=6, column=0, columnspan=2, pady=(4, 0), sticky="ew")
        
        self.btn_show_res = ttk.Button(frm, text="Показать бронирования", command=self.show_reservations)
        self.btn_show_res.grid(row=7, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        self.btn_demo = ttk.Button(frm, text="Демо. Наследование/Защищ.", command=self.run_inheritance_demo)
        self.btn_demo.grid(row=8, column=0, columnspan=2, pady=(8, 0), sticky="ew")
        
        self.status_label = ttk.Label(frm, text="")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(8,0), sticky="w")
        
        self.refresh_rooms()

    def run_inheritance_demo(self):
        try:
            employee = Employee("Peter", "Jackson", "Manager", _salary=120000)
            
            info(f"__str__ Employee: {employee}")
            info(f"__repr__ Employee: {repr(employee)}")

            base_first_msg = employee.display_info(use_base_first=True)
            derived_first_msg = employee.display_info(use_base_first=False)

            messagebox.showinfo(
                "Демонстрация Наследования и Атрибутов",
                f"Сотрудник создан (Employee):\n{repr(employee)}\n\n"
                f"--- Демонстрация Защищенного Атрибута (_salary) ---\n"
                f"(См. лог: Доступ к _salary: 120000₽)\n\n"
                f"--- Вызов Переопределенных Методов ---\n"
                f"Сначала Базовый:\n{base_first_msg}\n\n"
                f"Сначала Производный:\n{derived_first_msg}"
            )
        except Exception as e:
            messagebox.showerror("Ошибка Демо", f"Ошибка при демонстрации: {e}")

    def refresh_rooms(self):
        available = self.hotel.available_rooms()
        self.available_map = {f"{r.room_number} — {r.room_type} ({r.price}₽)": r for r in available}
        choices = list(self.available_map.keys())
        self.combobox_rooms['values'] = choices
        self.room_var.set(choices[0] if choices else "")
        info("Обновлён список свободных номеров")
        self.status_label.config(text=f"Доступно номеров: {len(choices)}")

    def book_room(self):
        name = self.entry_name.get().strip()
        lastname = self.entry_lastname.get().strip()
        check_in = self.entry_in.get().strip() or "N/A"
        check_out = self.entry_out.get().strip() or "N/A"
        room_choice = self.room_var.get().strip()
        
        if not name or not lastname:
            messagebox.showwarning("Ошибка", "Введите имя и фамилию.")
            return
        if not room_choice:
            messagebox.showwarning("Ошибка", "Выберите свободный номер.")
            return

        try:
            validate_guest_data(name, lastname)
        except InvalidGuestDataError as e:
            messagebox.showerror("Ошибка данных", str(e))
            return
        
        room = self.available_map.get(room_choice)
        if room is None:
            messagebox.showerror("Ошибка", "Выбранный номер недоступен. Обновите список.")
            self.refresh_rooms()
            return

        guest = self.hotel.find_guest(name, lastname)
        if guest is None:
            guest = Guest(name, lastname)
            self.hotel.add_guest(guest)

        reservation = self.hotel.make_reservation(guest, room, check_in, check_out)
        
        if reservation:
            nights = 1
            try:
                nights = max(1, (datetime.fromisoformat(check_out) - datetime.fromisoformat(check_in)).days)
            except Exception:
                nights = 1
            total_with_tax = Room.calculate_total_price(room.price, nights)
            messagebox.showinfo(
                "Успех",
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
            messagebox.showinfo("Бронирования", "Бронирований нет.")
            info("Бронирований нет")
            return
        lines = []
        for idx, r in enumerate(self.hotel.reservations, start=1):
            lines.append(f"{idx}. {r.guest.name} {r.guest.lastName} — Номер {r.room.room_number} — {r.dates[0]} → {r.dates[1]}")
        text = "\n".join(lines)
        messagebox.showinfo("Существующие бронирования", text)
        info(f"Бронирования: {len(lines)}")
        
    def run(self):
        self.root.mainloop()

hotel = Hotel("Grand Hotel")
room1 = hotel.add_room(Room(101, "Single", 5000))
room2 = hotel.add_room(Room(102, "Double", 8000))
room3 = hotel.add_room(Room(201, "Suite", 15000))
room4 = hotel.add_room(Room(202, "Single", 5200))

info(f"Статистика по номерному фонду: {Room.get_room_statistics()}")

guest1 = hotel.add_guest(Guest("Alice", "Johnson", 30))
guest2 = hotel.add_guest(Guest("Bob", "Ross", 45))

info("\n--- Демонстрация Задания 1: Обработка исключений ---")
hotel.make_reservation(guest1, room1, "2025-10-10", "2025-10-12") 
hotel.make_reservation(guest2, room1, "2025-10-13", "2025-10-15") 
hotel.make_reservation(None, room2, "2025-10-13", "2025-10-15") 
hotel.make_reservation(guest2, "НеКомната", "2025-10-13", "2025-10-15") 


info("\n--- Демонстрация Задания 2: Массивы объектов ---")
room_mgr = RoomManager()
room_mgr.add_room_1d(room1)
room_mgr.add_room_1d(room3)
info(f"1D Массив (цены): {[r.price for r in room_mgr.rooms_1d]}")

rooms_2d_example = [
    [room4, room2], 
    [room3, hotel.add_room(Room(301, "Deluxe", 25000))]
]
room_mgr.set_rooms_2d(rooms_2d_example)

try:
    max_room = room_mgr.find_room_with_max_price()
    info(f"Номер с максимальной ценой в 2D массиве: {max_room.room_number} ({max_room.price}₽)")
except BaseHotelError as e:
    error(f"Ошибка в RoomManager: {e}")

empty_mgr = RoomManager()
try:
    empty_mgr.find_room_with_max_price()
except EmptyRoomListError as e:
    info(f"Успешно поймана ошибка: {e}")


gui = HotelGUI(hotel)
gui.run()