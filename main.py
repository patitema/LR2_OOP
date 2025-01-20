class Room:
    def __init__(self, room_number, room_type, price):
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.is_available = True

    def __str__(self):
        return (f"Room {self.room_number} ({self.room_type}), Price: {self.price} RUB, Available: {self.is_available}")

class Guest:
    def __init__(self, name):
        self.name = name
        self.reservations = []

    def add_reservation(self, reservation):
        self.reservations.append(reservation)

    def __str__(self):
        return f"Guest: {self.name}, Reservations: {len(self.reservations)}"

class Reservation:
    def __init__(self, guest, room, check_in_date, check_out_date):
        self.guest = guest
        self.room = room
        self.dates = (check_in_date, check_out_date)
        guest.add_reservation(self)
        room.is_available = False

    def __str__(self):
        return f"Reservation for {self.guest.name}, Room {self.room.room_number}, Dates: {self.dates[0]} to {self.dates[1]}"

class Payment:
    def __init__(self, reservation):
        self.reservation = reservation
        self.amount = reservation.room.price
        self.is_paid = False

    def pay(self):
        self.is_paid = True
        print(f"Payment of {self.amount} RUB for reservation {self.reservation} is completed.")

    def __str__(self):
        return f"Payment for {self.reservation.guest.name}, Amount: {self.amount} RUB, Paid: {self.is_paid}"

class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.guests = []
        self.reservations = []
        self.payments = []

    def add_room(self, room):
        self.rooms.append(room)

    def add_guest(self, guest):
        self.guests.append(guest)

    def make_reservation(self, guest, room, check_in_date, check_out_date):
        if room.is_available:
            reservation = Reservation(guest, room, check_in_date, check_out_date)
            self.reservations.append(reservation)
            print(f"Reservation made: {reservation}")
        else:
            print(f"Room {room.room_number} is not available.")

    def cancel_reservation(self, reservation):
        if reservation in self.reservations:
            reservation.room.is_available = True
            self.reservations.remove(reservation)
            print(f"Reservation canceled: {reservation}")
        else:
            print("Reservation not found.")

    def process_payment(self, reservation):
        payment = Payment(reservation)
        payment.pay()
        self.payments.append(payment)

    def __str__(self):
        return (f"Hotel: {self.name}, Rooms: {len(self.rooms)}, Guests: {len(self.guests)}, Reservations: {len(self.reservations)}")


# Работа кода

# Создаем отель
hotel = Hotel("Grand Hotel")

# Добавляем номера
room1 = Room(101, "Single", 5000)
room2 = Room(102, "Double", 9000)
hotel.add_room(room1)
hotel.add_room(room2)

# Регистрируем гостей
guest1 = Guest("Alice")
guest2 = Guest("Bob")
hotel.add_guest(guest1)
hotel.add_guest(guest2)

# Бронируем номера
print(hotel.make_reservation(guest1, room1, "2023-10-01", "2023-10-05"), "\n")
print(hotel.make_reservation(guest2, room2, "2023-10-02", "2023-10-06"), "\n")

# Обрабатываем оплату
for reservation in hotel.reservations:
    print(hotel.process_payment(reservation), "\n")

# Выводим информацию
print(hotel, "\n")

# Выводим все номера
print("All rooms:")
for room in hotel.rooms:
    print(room, "\n")

# Выводим всех гостей
print("All guests:")
for guest in hotel.guests:
    print(guest, "\n")

# Выводим все бронирования
print("All reservations:")
for reservation in hotel.reservations:
    print(reservation, "\n")

# Выводим все оплаты
print("All payments:")
for payment in hotel.payments:
    print(payment, "\n")

# Отменяем бронирование
print(hotel.cancel_reservation(hotel.reservations[0]), "\n")

# Выводим информацию после отмены
print(hotel, "\n")
print(room1, "\n")