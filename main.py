class Room:
    def __init__(self, room_number, room_type, price):
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.is_available = True

    def __str__(self):
        return (f"Room {self.room_number} ({self.room_type}), Price: {self.price} RUB, Available: {self.is_available}")

class Person:
    def __init__(self, name, lastName, age):
        self.name = name
        self.lastName = lastName
        self.age = age

    def __str__(self):
        return f"Person: {self.name} {self.lastName}, age: {self.age}"

class Guest(Person):
    def __init__(self, name, lastName, age):
        super().__init__(name, lastName, age)
        self.reservations = []

    def add_reservation(self, reservation):
        self.reservations.append(reservation)

    def __str__(self):
        return f"Guest: {self.name} {self.lastName}, Reservations: {len(self.reservations)}"

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
        print(f"Payment of {self.amount} RUB for reservation {self.reservation} is completed.", "\n")

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
            print(f"Reservation made: {reservation}", "\n")
        else:
            print(f"Room {room.room_number} is not available.", "\n")

    def cancel_reservation(self, reservation):
        if reservation in self.reservations:
            reservation.room.is_available = True
            self.reservations.remove(reservation)
            print(f"Reservation canceled: {reservation}", "\n")
        else:
            print("Reservation not found.", "\n")

    def process_payment(self, reservation):
        payment = Payment(reservation)
        payment.pay()
        self.payments.append(payment)

    def __str__(self):
        return (f"Hotel: {self.name}, Rooms: {len(self.rooms)}, Guests: {len(self.guests)}, Reservations: {len(self.reservations)}")
    
    def show_guests(self):
        print("Guests:")
        for guest in self.guests:
            print(guest, "\n")

    def show_rooms(self):
        print("Rooms:")
        for room in self.rooms:
            print(room, "\n")

    def show_reservations(self):
        print("Reservations:")
        for reservation in self.reservations:
            print(reservation, "\n")

    def show_payments(self):
        print("Payments:")
        for payment in self.payments:
            print(payment, "\n")

# Создаем отель
hotel = Hotel("Grand Hotel")

# Добавляем номер
room1 = Room(101, "Single", 5000)
room2 = Room(102, "Double", 9000)
hotel.add_room(room1)
hotel.add_room(room2)

# Регистрируем гостей
person1 = Person("Alice", "Niggerson", 20)
person2 = Person("Bob", "Ross", 35)
guest1 = Guest(person1.name, person1.lastName, person1.age)
guest2 = Guest(person2.name, person2.lastName, person2.age)
hotel.add_guest(guest1)
hotel.add_guest(guest2)

# Бронируем номера
hotel.make_reservation(guest1, room1, "2023-10-01", "2023-10-05")
hotel.make_reservation(guest2, room2, "2023-10-02", "2023-10-06")

# Обрабатываем оплату
for reservation in hotel.reservations:
    hotel.process_payment(reservation)

# Выводим информацию
hotel.show_guests()
hotel.show_rooms()
hotel.show_reservations()
hotel.show_payments()

# Отменям бронирование
hotel.cancel_reservation(hotel.reservations[0])
print()

# Выводим информацию после отмены
print(hotel, "\n")
print(room1, "\n")