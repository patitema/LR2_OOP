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
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"{ts} - ERROR - Не удалось записать в лог-файл: {e}")

def info(msg: str): log("INFO", msg)
def warning(msg: str): log("WARNING", msg)
def error(msg: str): log("ERROR", msg)

class HotelBookingError(Exception): pass
class RoomNotAvailableError(HotelBookingError): pass
class InvalidGuestDataError(HotelBookingError): pass

def validate_guest_data(name: str, lastname: str):
    if not isinstance(name, str) or not name.strip():
        raise InvalidGuestDataError("Имя не должно быть пустой строкой")
    if not isinstance(lastname, str) or not lastname.strip():
        raise InvalidGuestDataError("Фамилия не должна быть пустой строкой")
    
    if name.strip().isdigit():
        raise InvalidGuestDataError("Имя не может быть числом")
    if lastname.strip().isdigit():
        raise InvalidGuestDataError("Фамилия не может быть числом")
    
    try:
        float(name.strip())
        raise InvalidGuestDataError("Имя не может быть числом")
    except ValueError:
        pass
    
    try:
        float(lastname.strip())
        raise InvalidGuestDataError("Фамилия не может быть числом")
    except ValueError:
        pass
    
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

    def __str__(self):
        return self.info()

class Guest(Person):
    def __init__(self, name, lastName, age=None):
        self.reservations = []
        super().__init__(name, lastName, age)
        info(f"Создан Guest: {self.name} {self.lastName}")

    def add_reservation(self, reservation):
        self.reservations.append(reservation)

    def info(self):
        return f"Гость {self.name} {self.lastName}, бронирований: {len(self.reservations)}"

    def get_role(self):
        return "guest"

class Room:
    total_rooms = 0
    ROOM_TYPES = {"Single", "Double", "Suite", "Deluxe"}
    TAX_RATE = 0.18

    def __init__(self, room_number, room_type, price):
        if not Room.is_valid_room_type(room_type):
            raise ValueError(f"Неизвестный тип номера: {room_type}")
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.is_available = True
        Room.total_rooms += 1

    def __str__(self):
        return f"комната {self.room_number} ({self.room_type}), {self.price}₽, {'доступна' if self.is_available else 'недоступна'}"

    # Перегрузки операторов
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
        return f"{self.guest.name} {self.guest.lastName}, Room {self.room.room_number}, {self.dates[0]} - {self.dates[1]}"

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

    def find_room_by_number(self, room_number):
        return self.rooms_by_number.get(room_number)

    def get_rooms_by_type(self, room_type):
        return list(self.rooms_by_type.get(room_type, []))

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
        try:
            if guest is None:
                raise InvalidGuestDataError("guest = None")
            if room is None or not isinstance(room, Room):
                raise HotelBookingError("Комната отсутствует или неверного типа")
            if not room.is_available:
                raise RoomNotAvailableError(f"Номер {room.room_number} недоступен")

            reservation = Reservation(guest, room, check_in_date, check_out_date)
            self.reservations.append(reservation)
            return reservation
        except HotelBookingError as e:
            error(f"Ошибка бронирования: {e}")
            return None
        except Exception as e:
            error(f"Неожиданная ошибка: {e}")
            return None

    def cancel_reservation(self, reservation):
        if reservation in self.reservations:
            reservation.room.is_available = True
            self.reservations.remove(reservation)
            if reservation in reservation.guest.reservations:
                reservation.guest.reservations.remove(reservation)
            info(f"Бронирование отменено: {reservation}")
            return True
        warning("Попытка отменить несуществующее бронирование")
        return False

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

        self.status_label = ttk.Label(frm, text="")
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(8,0), sticky="w")

        self.refresh_rooms()

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
            info(f"Бронирование создано: {reservation}")
            self.refresh_rooms()
        else:
            messagebox.showerror("Ошибка", "Не удалось забронировать номер. Попробуйте обновить список.")
            warning("Неудачная попытка бронирования")

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

# sorted_by_price = sorted([room1, room2, room3, room4])
# info(f"Самый дешевый номер: {sorted_by_price[0]}")
# total_two = room1 + room2
# info(f"Суммарная цена room1 + room2: {total_two}")
# info(f"room1 'in' Single? {'Single' in room1}")

info(f"Статистика по номерному фонду: {Room.get_room_statistics()}")

# guest1 = hotel.add_guest(Guest("Alice", "Johnson"))
# guest2 = hotel.add_guest(Guest("Bob", "Ross"))

# hotel.make_reservation(guest1, room1, "2023-10-01", "2023-10-05")
# hotel.make_reservation(guest2, room2, "2023-10-02", "2023-10-06")

gui = HotelGUI(hotel)
gui.run()
