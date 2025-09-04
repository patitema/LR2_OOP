import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

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

def info(msg: str):
    log("INFO", msg)

def warning(msg: str):
    log("WARNING", msg)

def error(msg: str):
    log("ERROR", msg)


class Person:
    def __init__(self, name, lastName, age=None):
        self.name = name
        self.lastName = lastName
        self.age = age
        info(f"Создан Person: {self.name} {self.lastName}")

    def info(self):
        return f"{self.name} {self.lastName}" if self.age is None else f"{self.name} {self.lastName}, {self.age} лет"

    def __str__(self):
        return self.info()


class Guest(Person):
    def __init__(self, name, lastName, age=None):
        self.reservations = []
        super().__init__(name, lastName, age)
        info(f"Создан Guest: {self.name} {self.lastName}")

    def add_reservation(self, reservation):
        self.reservations.append(reservation)
        info(f"Гостю {self.name} добавлено бронирование: {reservation}")

    def info(self):
        return f"Гость {self.name} {self.lastName}, бронирований: {len(self.reservations)}"


class Staff(Person):
    def __init__(self, name, lastName, age=None, position=""):
        self.position = position
        super().__init__(name, lastName, age)
        info(f"Создан Staff: {self.name} {self.lastName}, должность: {self.position}")

    def info(self):
        return f"Сотрудник {self.name} {self.lastName}, должность: {self.position}"


class Room:
    def __init__(self, room_number, room_type, price):
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.is_available = True
        info(f"Создан Room: {self.room_number} ({self.room_type}), цена: {self.price}")

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type}), {self.price}₽, Доступен: {self.is_available}"


class Reservation:
    def __init__(self, guest, room, check_in_date="N/A", check_out_date="N/A"):
        self.guest = guest
        self.room = room
        self.dates = (check_in_date, check_out_date)
        guest.add_reservation(self)
        room.is_available = False
        info(f"Создан Reservation: {self}")

    def __str__(self):
        return f"{self.guest.name} {self.guest.lastName}, Room {self.room.room_number}, {self.dates[0]} - {self.dates[1]}"


class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.guests = []
        self.reservations = []
        info(f"Создан Hotel: {self.name}")

    def add_room(self, room):
        """Добавляет комнату и возвращает её (вариант B)."""
        self.rooms.append(room)
        info(f"Добавлен {room}")
        return room

    def find_guest(self, name, lastName):
        for g in self.guests:
            if g.name == name and g.lastName == lastName:
                return g
        return None

    def add_guest(self, guest):
        """Добавляет гостя (если не существует) и возвращает объект гостя (вариант B)."""
        existing = self.find_guest(guest.name, guest.lastName)
        if existing is None:
            self.guests.append(guest)
            info(f"Добавлен {guest}")
            return guest
        info(f"Гость уже существует: {existing}")
        return existing

    def make_reservation(self, guest, room, check_in_date="N/A", check_out_date="N/A"):
        """Создаёт бронирование с базовой валидацией."""
        if guest is None:
            error("Попытка забронировать: передан guest = None")
            return None
        if room is None:
            error("Попытка забронировать: передан room = None")
            return None
        if not isinstance(room, Room):
            error("Попытка забронировать: объект room не является Room")
            return None
        if not room.is_available:
            warning(f"Номер {room.room_number} недоступен")
            return None

        reservation = Reservation(guest, room, check_in_date, check_out_date)
        self.reservations.append(reservation)
        info(f"Бронирование сделано: {reservation}")
        return reservation

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
        return list(filter(lambda r: r.is_available, self.rooms))


class HotelGUI:
    def __init__(self, hotel: Hotel):
        self.hotel = hotel
        self.root = tk.Tk()
        self.root.title("Hotel Booking — Быстрое бронирование")

        frm = ttk.Frame(self.root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # Поля ввода
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

        # Кнопки
        self.btn_refresh = ttk.Button(frm, text="Обновить список свободных номеров", command=self.refresh_rooms)
        self.btn_refresh.grid(row=5, column=0, columnspan=2, pady=(6, 2), sticky="ew")

        self.btn_book = ttk.Button(frm, text="Забронировать", command=self.book_room)
        self.btn_book.grid(row=6, column=0, columnspan=2, pady=(4, 0), sticky="ew")

        self.btn_show_res = ttk.Button(frm, text="Показать бронирования", command=self.show_reservations)
        self.btn_show_res.grid(row=7, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        # Статус
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

        room = self.available_map.get(room_choice)
        if room is None:
            messagebox.showerror("Ошибка", "Выбранный номер недоступен. Обновите список.")
            self.refresh_rooms()
            return

        guest = self.hotel.find_guest(name, lastname)
        if guest is None:
            guest = Guest(name, lastname)
            self.hotel.add_guest(guest)
            info(f"Новый гость создан через GUI: {guest}")

        reservation = self.hotel.make_reservation(guest, room, check_in, check_out)
        if reservation:
            messagebox.showinfo("Успех", f"Номер {room.room_number} успешно забронирован за {name} {lastname}.\nДаты: {check_in} — {check_out}")
            info(f"Бронирование через GUI: {reservation}")
            self.refresh_rooms()
        else:
            messagebox.showerror("Ошибка", "Не удалось забронировать номер. Попробуйте обновить список.")
            warning("Неудачная попытка бронирования через GUI")

    def show_reservations(self):
        info("Пользователь запросил просмотр бронирований через GUI")
        if not self.hotel.reservations:
            messagebox.showinfo("Бронирования", "Бронирований нет.")
            info("Отображено: бронирований нет")
            return
        lines = []
        for idx, r in enumerate(self.hotel.reservations, start=1):
            lines.append(f"{idx}. {r.guest.name} {r.guest.lastName} — Номер {r.room.room_number} — {r.dates[0]} → {r.dates[1]}")
        text = "\n".join(lines)
        messagebox.showinfo("Существующие бронирования", text)
        info(f"Отображено {len(lines)} бронирований через GUI")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    hotel = Hotel("Grand Hotel")

    room1 = hotel.add_room(Room(101, "Single", 5000))
    room2 = hotel.add_room(Room(102, "Double", 8000))
    room3 = hotel.add_room(Room(201, "Suite", 15000))
    room4 = hotel.add_room(Room(202, "Single", 5200))

    guest1 = hotel.add_guest(Guest("Alice", "Johnson"))
    guest2 = hotel.add_guest(Guest("Bob", "Ross"))

    hotel.make_reservation(guest1, room1, "2023-10-01", "2023-10-05")
    hotel.make_reservation(guest2, room2, "2023-10-02", "2023-10-06")

    gui = HotelGUI(hotel)
    gui.run()
