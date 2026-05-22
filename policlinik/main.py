from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bd import (
    ClientRegistrationData,
    DoctorRegistrationData,
    addDoctor,
    addSlot,
    authenticate,
    createAppointment,
    getClientByUserId,
    getDoctorByUserId,
    initDb,
    listAllAppointments,
    listAllClients,
    listClientAppointments,
    listDoctorAppointments,
    listDoctors,
    listFreeSlotsByDoctor,
    registerClient,
)


@dataclass
class LoginData:
    username: str
    password: str


def safeIntInput(prompt: str) -> int | None:
    value = input(prompt).strip()
    try:
        return int(value)
    except ValueError:
        print("Ошибка: нужно ввести число.")
        return None


def showDoctors() -> None:
    doctors = listDoctors()
    if not doctors:
        print("Врачей пока нет.")
        return
    for doctor in doctors:
        print(f"{doctor.id}. {doctor.fullName} ({doctor.specialization})")


def registrationFlow() -> None:
    print("\n=== Регистрация клиента ===")
    fullName = input("ФИО: ").strip()
    age = safeIntInput("Возраст: ")
    if age is None:
        return
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()

    data = ClientRegistrationData(fullName=fullName, age=age, username=username, password=password)
    success, message, client = registerClient(data)
    print(message)
    if success and client:
        print(f"Ваш номер медицинской карты: {client.id}")


def loginFlow() -> None:
    print("\n=== Вход ===")
    loginData = LoginData(
        username=input("Логин: ").strip(),
        password=input("Пароль: ").strip(),
    )
    user = authenticate(loginData.username, loginData.password)
    if not user:
        print("Неверный логин или пароль.")
        return

    if user.role == "client":
        clientMenu(user.id)
    elif user.role == "admin":
        adminMenu()
    elif user.role == "doctor":
        doctorMenu(user.id)
    else:
        print("Неизвестная роль пользователя.")


def clientMenu(userId: int) -> None:
    client = getClientByUserId(userId)
    if not client:
        print("Профиль клиента не найден.")
        return

    while True:
        print("\n=== Меню клиента ===")
        print("1. Посмотреть свой профиль")
        print("2. Записаться к врачу")
        print("3. Посмотреть свои записи")
        print("0. Выйти из аккаунта")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            print(f"Медкарта №{client.id}: {client.fullName}, возраст {client.age}")
        elif choice == "2":
            showDoctors()
            doctorId = safeIntInput("Выберите ID врача: ")
            if doctorId is None:
                continue

            freeSlots = listFreeSlotsByDoctor(doctorId)
            if not freeSlots:
                print("У выбранного врача нет свободных слотов.")
                continue

            print("Свободные слоты:")
            for slot in freeSlots:
                print(f"{slot.id}. {slot.dateTime.strftime('%Y-%m-%d %H:%M')}")

            slotId = safeIntInput("Выберите ID слота: ")
            if slotId is None:
                continue
            symptoms = input("Опишите симптомы: ").strip()
            success, message = createAppointment(client.id, doctorId, slotId, symptoms)
            print(message)
        elif choice == "3":
            appointments = listClientAppointments(client.id)
            if not appointments:
                print("У вас пока нет записей.")
                continue
            for appointment, doctor, slot in appointments:
                print(
                    f"Запись #{appointment.id}: {slot.dateTime.strftime('%Y-%m-%d %H:%M')} | "
                    f"{doctor.fullName} ({doctor.specialization}) | Симптомы: {appointment.symptoms}"
                )
        elif choice == "0":
            break
        else:
            print("Некорректный выбор.")


def doctorMenu(userId: int) -> None:
    doctor = getDoctorByUserId(userId)
    if not doctor:
        print("Профиль врача не найден.")
        return

    while True:
        print("\n=== Меню врача ===")
        print(f"Вы вошли как: {doctor.fullName} ({doctor.specialization})")
        print("1. Посмотреть записи к себе")
        print("0. Выйти из аккаунта")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            appointments = listDoctorAppointments(doctor.id)
            if not appointments:
                print("Записей к вам пока нет.")
                continue
            for appointment, client, slot in appointments:
                print(
                    f"{slot.dateTime.strftime('%Y-%m-%d %H:%M')} | "
                    f"Клиент: {client.fullName} (медкарта {client.id}) | "
                    f"Симптомы: {appointment.symptoms}"
                )
        elif choice == "0":
            break
        else:
            print("Некорректный выбор.")


def adminMenu() -> None:
    while True:
        print("\n=== Меню администратора ===")
        print("1. Посмотреть всех клиентов")
        print("2. Посмотреть все записи")
        print("3. Посмотреть всех врачей")
        print("4. Добавить врача")
        print("5. Добавить слот приема")
        print("0. Выйти из аккаунта")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            clients = listAllClients()
            if not clients:
                print("Клиентов пока нет.")
                continue
            for client in clients:
                print(f"{client.id}. {client.fullName}, возраст {client.age}")
        elif choice == "2":
            appointments = listAllAppointments()
            if not appointments:
                print("Записей пока нет.")
                continue
            for appointment, client, doctor, slot in appointments:
                print(
                    f"#{appointment.id} | {slot.dateTime.strftime('%Y-%m-%d %H:%M')} | "
                    f"Клиент: {client.fullName} | Врач: {doctor.fullName} ({doctor.specialization}) | "
                    f"Симптомы: {appointment.symptoms}"
                )
        elif choice == "3":
            showDoctors()
        elif choice == "4":
            fullName = input("ФИО врача: ").strip()
            specialization = input("Специализация: ").strip()
            username = input("Логин врача: ").strip()
            password = input("Пароль врача: ").strip()
            success, message, doctor = addDoctor(
                DoctorRegistrationData(
                    fullName=fullName,
                    specialization=specialization,
                    username=username,
                    password=password,
                )
            )
            print(message)
            if success and doctor:
                print(f"ID врача: {doctor.id}")
        elif choice == "5":
            showDoctors()
            doctorId = safeIntInput("ID врача: ")
            if doctorId is None:
                continue
            dtRaw = input("Дата и время (YYYY-MM-DD HH:MM): ").strip()
            try:
                dtValue = datetime.strptime(dtRaw, "%Y-%m-%d %H:%M")
            except ValueError:
                print("Некорректный формат даты.")
                continue
            success, message = addSlot(doctorId, dtValue)
            print(message)
        elif choice == "0":
            break
        else:
            print("Некорректный выбор.")


def main() -> None:
    initDb()
    while True:
        print("\n=== Поликлиника ===")
        print("1. Войти в систему")
        print("2. Зарегистрироваться как клиент")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            loginFlow()
        elif choice == "2":
            registrationFlow()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Некорректный выбор.")


if __name__ == "__main__":
    main()
