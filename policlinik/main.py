from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bd import (
    ClientRegistrationData,
    DoctorRegistrationData,
    add_doctor,
    add_slot,
    authenticate,
    create_appointment,
    get_client_by_user_id,
    get_doctor_by_user_id,
    init_db,
    list_all_appointments,
    list_all_clients,
    list_client_appointments,
    list_doctor_appointments,
    list_doctors,
    list_free_slots_by_doctor,
    register_client,
)


@dataclass
class LoginData:
    username: str
    password: str


def safe_int_input(prompt: str) -> int | None:
    value = input(prompt).strip()
    try:
        return int(value)
    except ValueError:
        print("Ошибка: нужно ввести число.")
        return None


def show_doctors() -> None:
    doctors = list_doctors()
    if not doctors:
        print("Врачей пока нет.")
        return
    for doctor in doctors:
        print(f"{doctor.id}. {doctor.full_name} ({doctor.specialization})")


def registration_flow() -> None:
    print("\n=== Регистрация клиента ===")
    full_name = input("ФИО: ").strip()
    age = safe_int_input("Возраст: ")
    if age is None:
        return
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()

    data = ClientRegistrationData(full_name=full_name, age=age, username=username, password=password)
    success, message, client = register_client(data)
    print(message)
    if success and client:
        print(f"Ваш номер медицинской карты: {client.id}")


def login_flow() -> None:
    print("\n=== Вход ===")
    login_data = LoginData(
        username=input("Логин: ").strip(),
        password=input("Пароль: ").strip(),
    )
    user = authenticate(login_data.username, login_data.password)
    if not user:
        print("Неверный логин или пароль.")
        return

    if user.role == "client":
        client_menu(user.id)
    elif user.role == "admin":
        admin_menu()
    elif user.role == "doctor":
        doctor_menu(user.id)
    else:
        print("Неизвестная роль пользователя.")


def client_menu(user_id: int) -> None:
    client = get_client_by_user_id(user_id)
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
            print(f"Медкарта №{client.id}: {client.full_name}, возраст {client.age}")
        elif choice == "2":
            show_doctors()
            doctor_id = safe_int_input("Выберите ID врача: ")
            if doctor_id is None:
                continue

            free_slots = list_free_slots_by_doctor(doctor_id)
            if not free_slots:
                print("У выбранного врача нет свободных слотов.")
                continue

            print("Свободные слоты:")
            for slot in free_slots:
                print(f"{slot.id}. {slot.date_time.strftime('%Y-%m-%d %H:%M')}")

            slot_id = safe_int_input("Выберите ID слота: ")
            if slot_id is None:
                continue
            symptoms = input("Опишите симптомы: ").strip()
            success, message = create_appointment(client.id, doctor_id, slot_id, symptoms)
            print(message)
        elif choice == "3":
            appointments = list_client_appointments(client.id)
            if not appointments:
                print("У вас пока нет записей.")
                continue
            for appointment, doctor, slot in appointments:
                print(
                    f"Запись #{appointment.id}: {slot.date_time.strftime('%Y-%m-%d %H:%M')} | "
                    f"{doctor.full_name} ({doctor.specialization}) | Симптомы: {appointment.symptoms}"
                )
        elif choice == "0":
            break
        else:
            print("Некорректный выбор.")


def doctor_menu(user_id: int) -> None:
    doctor = get_doctor_by_user_id(user_id)
    if not doctor:
        print("Профиль врача не найден.")
        return

    while True:
        print("\n=== Меню врача ===")
        print(f"Вы вошли как: {doctor.full_name} ({doctor.specialization})")
        print("1. Посмотреть записи к себе")
        print("0. Выйти из аккаунта")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            appointments = list_doctor_appointments(doctor.id)
            if not appointments:
                print("Записей к вам пока нет.")
                continue
            for appointment, client, slot in appointments:
                print(
                    f"{slot.date_time.strftime('%Y-%m-%d %H:%M')} | "
                    f"Клиент: {client.full_name} (медкарта {client.id}) | "
                    f"Симптомы: {appointment.symptoms}"
                )
        elif choice == "0":
            break
        else:
            print("Некорректный выбор.")


def admin_menu() -> None:
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
            clients = list_all_clients()
            if not clients:
                print("Клиентов пока нет.")
                continue
            for client in clients:
                print(f"{client.id}. {client.full_name}, возраст {client.age}")
        elif choice == "2":
            appointments = list_all_appointments()
            if not appointments:
                print("Записей пока нет.")
                continue
            for appointment, client, doctor, slot in appointments:
                print(
                    f"#{appointment.id} | {slot.date_time.strftime('%Y-%m-%d %H:%M')} | "
                    f"Клиент: {client.full_name} | Врач: {doctor.full_name} ({doctor.specialization}) | "
                    f"Симптомы: {appointment.symptoms}"
                )
        elif choice == "3":
            show_doctors()
        elif choice == "4":
            full_name = input("ФИО врача: ").strip()
            specialization = input("Специализация: ").strip()
            username = input("Логин врача: ").strip()
            password = input("Пароль врача: ").strip()
            success, message, doctor = add_doctor(
                DoctorRegistrationData(
                    full_name=full_name,
                    specialization=specialization,
                    username=username,
                    password=password,
                )
            )
            print(message)
            if success and doctor:
                print(f"ID врача: {doctor.id}")
        elif choice == "5":
            show_doctors()
            doctor_id = safe_int_input("ID врача: ")
            if doctor_id is None:
                continue
            dt_raw = input("Дата и время (YYYY-MM-DD HH:MM): ").strip()
            try:
                dt_value = datetime.strptime(dt_raw, "%Y-%m-%d %H:%M")
            except ValueError:
                print("Некорректный формат даты.")
                continue
            success, message = add_slot(doctor_id, dt_value)
            print(message)
        elif choice == "0":
            break
        else:
            print("Некорректный выбор.")


def main() -> None:
    init_db()
    while True:
        print("\n=== Поликлиника ===")
        print("1. Войти в систему")
        print("2. Зарегистрироваться как клиент")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            login_flow()
        elif choice == "2":
            registration_flow()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Некорректный выбор.")


if __name__ == "__main__":
    main()
