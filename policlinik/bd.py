from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///policlinik.db")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship()


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_busy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("appointment_slots.id"), unique=True, nullable=False)
    symptoms: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


@dataclass
class ClientRegistrationData:
    full_name: str
    age: int
    username: str
    password: str


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed_data(session)


def seed_data(session: Session) -> None:
    admin = session.scalar(select(User).where(User.username == "admin"))
    if admin is None:
        session.add(User(username="admin", password="admin", role="admin"))

    if session.scalar(select(Doctor.id).limit(1)) is None:
        doctors = [
            Doctor(full_name="Иван Петров", specialization="Терапевт"),
            Doctor(full_name="Ольга Смирнова", specialization="Хирург"),
            Doctor(full_name="Сергей Иванов", specialization="Невролог"),
        ]
        session.add_all(doctors)
        session.flush()

        slot_times = [
            datetime(2026, 5, 23, 10, 0),
            datetime(2026, 5, 23, 11, 0),
            datetime(2026, 5, 24, 10, 0),
            datetime(2026, 5, 24, 11, 0),
        ]
        for doctor in doctors:
            for slot_time in slot_times:
                session.add(AppointmentSlot(doctor_id=doctor.id, date_time=slot_time, is_busy=False))

    session.commit()


def register_client(data: ClientRegistrationData) -> tuple[bool, str, Optional[Client]]:
    with SessionLocal() as session:
        existing_user = session.scalar(select(User).where(User.username == data.username))
        if existing_user:
            return False, "Логин уже занят.", None

        user = User(username=data.username, password=data.password, role="client")
        session.add(user)
        session.flush()

        client = Client(user_id=user.id, full_name=data.full_name, age=data.age)
        session.add(client)
        session.commit()
        session.refresh(client)
        return True, "Регистрация завершена.", client


def authenticate(username: str, password: str) -> Optional[User]:
    with SessionLocal() as session:
        return session.scalar(
            select(User).where(User.username == username, User.password == password)
        )


def get_client_by_user_id(user_id: int) -> Optional[Client]:
    with SessionLocal() as session:
        return session.scalar(select(Client).where(Client.user_id == user_id))


def list_doctors() -> list[Doctor]:
    with SessionLocal() as session:
        return list(session.scalars(select(Doctor).order_by(Doctor.id)).all())


def list_free_slots_by_doctor(doctor_id: int) -> list[AppointmentSlot]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(AppointmentSlot)
                .where(AppointmentSlot.doctor_id == doctor_id, AppointmentSlot.is_busy.is_(False))
                .order_by(AppointmentSlot.date_time)
            ).all()
        )


def create_appointment(client_id: int, doctor_id: int, slot_id: int, symptoms: str) -> tuple[bool, str]:
    with SessionLocal() as session:
        doctor = session.get(Doctor, doctor_id)
        if not doctor:
            return False, "Врач не найден."

        slot = session.get(AppointmentSlot, slot_id)
        if not slot or slot.doctor_id != doctor_id:
            return False, "Слот не найден у выбранного врача."
        if slot.is_busy:
            return False, "Этот слот уже занят."

        appointment = Appointment(
            client_id=client_id,
            doctor_id=doctor_id,
            slot_id=slot_id,
            symptoms=symptoms,
        )
        slot.is_busy = True
        session.add(appointment)
        session.commit()
        return True, "Запись успешно создана."


def list_client_appointments(client_id: int) -> list[tuple[Appointment, Doctor, AppointmentSlot]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Appointment, Doctor, AppointmentSlot)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
            .where(Appointment.client_id == client_id)
            .order_by(AppointmentSlot.date_time)
        ).all()
        return list(rows)


def list_doctor_appointments(doctor_id: int) -> list[tuple[Appointment, Client, AppointmentSlot]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Appointment, Client, AppointmentSlot)
            .join(Client, Appointment.client_id == Client.id)
            .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
            .where(Appointment.doctor_id == doctor_id)
            .order_by(AppointmentSlot.date_time)
        ).all()
        return list(rows)


def list_all_clients() -> list[Client]:
    with SessionLocal() as session:
        return list(session.scalars(select(Client).order_by(Client.id)).all())


def list_all_appointments() -> list[tuple[Appointment, Client, Doctor, AppointmentSlot]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Appointment, Client, Doctor, AppointmentSlot)
            .join(Client, Appointment.client_id == Client.id)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .join(AppointmentSlot, Appointment.slot_id == AppointmentSlot.id)
            .order_by(AppointmentSlot.date_time)
        ).all()
        return list(rows)


def add_doctor(full_name: str, specialization: str) -> Doctor:
    with SessionLocal() as session:
        doctor = Doctor(full_name=full_name, specialization=specialization)
        session.add(doctor)
        session.commit()
        session.refresh(doctor)
        return doctor


def add_slot(doctor_id: int, date_time: datetime) -> tuple[bool, str]:
    with SessionLocal() as session:
        doctor = session.get(Doctor, doctor_id)
        if not doctor:
            return False, "Врач не найден."

        slot = AppointmentSlot(doctor_id=doctor_id, date_time=date_time, is_busy=False)
        session.add(slot)
        session.commit()
        return True, "Слот добавлен."
