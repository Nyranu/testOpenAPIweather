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
    userId: Mapped[int] = mapped_column("user_id", ForeignKey("users.id"), unique=True, nullable=False)
    fullName: Mapped[str] = mapped_column("full_name", String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship()


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    userId: Mapped[int] = mapped_column("user_id", ForeignKey("users.id"), unique=True, nullable=False)
    fullName: Mapped[str] = mapped_column("full_name", String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped[User] = relationship()


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctorId: Mapped[int] = mapped_column("doctor_id", ForeignKey("doctors.id"), nullable=False)
    dateTime: Mapped[datetime] = mapped_column("date_time", DateTime, nullable=False)
    isBusy: Mapped[bool] = mapped_column("is_busy", Boolean, default=False, nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    clientId: Mapped[int] = mapped_column("client_id", ForeignKey("clients.id"), nullable=False)
    doctorId: Mapped[int] = mapped_column("doctor_id", ForeignKey("doctors.id"), nullable=False)
    slotId: Mapped[int] = mapped_column("slot_id", ForeignKey("appointment_slots.id"), unique=True, nullable=False)
    symptoms: Mapped[str] = mapped_column(String(500), nullable=False)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime, default=datetime.utcnow, nullable=False)


@dataclass
class ClientRegistrationData:
    fullName: str
    age: int
    username: str
    password: str


@dataclass
class DoctorRegistrationData:
    fullName: str
    specialization: str
    username: str
    password: str


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def initDb() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seedData(session)


def seedData(session: Session) -> None:
    admin = session.scalar(select(User).where(User.username == "admin"))
    if admin is None:
        session.add(User(username="admin", password="admin", role="admin"))

    defaults = [
        ("doctor1", "doctor1", "Иван Петров", "Терапевт"),
        ("doctor2", "doctor2", "Ольга Смирнова", "Хирург"),
        ("doctor3", "doctor3", "Сергей Иванов", "Невролог"),
    ]

    doctorsForSlots: list[Doctor] = []
    for username, password, fullName, specialization in defaults:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password=password, role="doctor")
            session.add(user)
            session.flush()

        doctor = session.scalar(select(Doctor).where(Doctor.userId == user.id))
        if doctor is None:
            doctor = Doctor(
                userId=user.id,
                fullName=fullName,
                specialization=specialization,
            )
            session.add(doctor)
            session.flush()
        doctorsForSlots.append(doctor)

    slotTimes = [
        datetime(2026, 5, 23, 10, 0),
        datetime(2026, 5, 23, 11, 0),
        datetime(2026, 5, 24, 10, 0),
        datetime(2026, 5, 24, 11, 0),
    ]
    for doctor in doctorsForSlots:
        for slotTime in slotTimes:
            exists = session.scalar(
                select(AppointmentSlot).where(
                    AppointmentSlot.doctorId == doctor.id,
                    AppointmentSlot.dateTime == slotTime,
                )
            )
            if exists is None:
                session.add(AppointmentSlot(doctorId=doctor.id, dateTime=slotTime, isBusy=False))

    session.commit()


def registerClient(data: ClientRegistrationData) -> tuple[bool, str, Optional[Client]]:
    if not data.fullName.strip():
        return False, "ФИО не может быть пустым.", None
    if data.age <= 0:
        return False, "Возраст должен быть положительным числом.", None
    if not data.username.strip():
        return False, "Логин не может быть пустым.", None
    if not data.password.strip():
        return False, "Пароль не может быть пустым.", None

    with SessionLocal() as session:
        existingUser = session.scalar(select(User).where(User.username == data.username))
        if existingUser:
            return False, "Логин уже занят.", None

        user = User(username=data.username.strip(), password=data.password.strip(), role="client")
        session.add(user)
        session.flush()

        client = Client(userId=user.id, fullName=data.fullName.strip(), age=data.age)
        session.add(client)
        session.commit()
        session.refresh(client)
        return True, "Регистрация завершена.", client


def authenticate(username: str, password: str) -> Optional[User]:
    with SessionLocal() as session:
        return session.scalar(
            select(User).where(User.username == username, User.password == password)
        )


def getClientByUserId(userId: int) -> Optional[Client]:
    with SessionLocal() as session:
        return session.scalar(select(Client).where(Client.userId == userId))


def getDoctorByUserId(userId: int) -> Optional[Doctor]:
    with SessionLocal() as session:
        return session.scalar(select(Doctor).where(Doctor.userId == userId))


def listDoctors() -> list[Doctor]:
    with SessionLocal() as session:
        return list(session.scalars(select(Doctor).order_by(Doctor.id)).all())


def listFreeSlotsByDoctor(doctorId: int) -> list[AppointmentSlot]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(AppointmentSlot)
                .where(AppointmentSlot.doctorId == doctorId, AppointmentSlot.isBusy.is_(False))
                .order_by(AppointmentSlot.dateTime)
            ).all()
        )


def createAppointment(clientId: int, doctorId: int, slotId: int, symptoms: str) -> tuple[bool, str]:
    if not symptoms.strip():
        return False, "Симптомы не могут быть пустыми."

    with SessionLocal() as session:
        doctor = session.get(Doctor, doctorId)
        if not doctor:
            return False, "Врач не найден."

        slot = session.get(AppointmentSlot, slotId)
        if not slot or slot.doctorId != doctorId:
            return False, "Слот не найден у выбранного врача."
        if slot.isBusy:
            return False, "Этот слот уже занят."

        appointment = Appointment(
            clientId=clientId,
            doctorId=doctorId,
            slotId=slotId,
            symptoms=symptoms.strip(),
        )
        slot.isBusy = True
        session.add(appointment)
        session.commit()
        return True, "Запись успешно создана."


def listClientAppointments(clientId: int) -> list[tuple[Appointment, Doctor, AppointmentSlot]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Appointment, Doctor, AppointmentSlot)
            .join(Doctor, Appointment.doctorId == Doctor.id)
            .join(AppointmentSlot, Appointment.slotId == AppointmentSlot.id)
            .where(Appointment.clientId == clientId)
            .order_by(AppointmentSlot.dateTime)
        ).all()
        return list(rows)


def listDoctorAppointments(doctorId: int) -> list[tuple[Appointment, Client, AppointmentSlot]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Appointment, Client, AppointmentSlot)
            .join(Client, Appointment.clientId == Client.id)
            .join(AppointmentSlot, Appointment.slotId == AppointmentSlot.id)
            .where(Appointment.doctorId == doctorId)
            .order_by(AppointmentSlot.dateTime)
        ).all()
        return list(rows)


def listAllClients() -> list[Client]:
    with SessionLocal() as session:
        return list(session.scalars(select(Client).order_by(Client.id)).all())


def listAllAppointments() -> list[tuple[Appointment, Client, Doctor, AppointmentSlot]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Appointment, Client, Doctor, AppointmentSlot)
            .join(Client, Appointment.clientId == Client.id)
            .join(Doctor, Appointment.doctorId == Doctor.id)
            .join(AppointmentSlot, Appointment.slotId == AppointmentSlot.id)
            .order_by(AppointmentSlot.dateTime)
        ).all()
        return list(rows)


def addDoctor(data: DoctorRegistrationData) -> tuple[bool, str, Optional[Doctor]]:
    if not data.fullName.strip():
        return False, "ФИО врача не может быть пустым.", None
    if not data.specialization.strip():
        return False, "Специализация не может быть пустой.", None
    if not data.username.strip():
        return False, "Логин не может быть пустым.", None
    if not data.password.strip():
        return False, "Пароль не может быть пустым.", None

    with SessionLocal() as session:
        if session.scalar(select(User).where(User.username == data.username.strip())):
            return False, "Логин уже занят.", None

        user = User(username=data.username.strip(), password=data.password.strip(), role="doctor")
        session.add(user)
        session.flush()

        doctor = Doctor(
            userId=user.id,
            fullName=data.fullName.strip(),
            specialization=data.specialization.strip(),
        )
        session.add(doctor)
        session.commit()
        session.refresh(doctor)
        return True, "Врач добавлен.", doctor


def addSlot(doctorId: int, dateTime: datetime) -> tuple[bool, str]:
    with SessionLocal() as session:
        doctor = session.get(Doctor, doctorId)
        if not doctor:
            return False, "Врач не найден."

        exists = session.scalar(
            select(AppointmentSlot).where(
                AppointmentSlot.doctorId == doctorId,
                AppointmentSlot.dateTime == dateTime,
            )
        )
        if exists is not None:
            return False, "Такой слот у этого врача уже существует."

        slot = AppointmentSlot(doctorId=doctorId, dateTime=dateTime, isBusy=False)
        session.add(slot)
        session.commit()
        return True, "Слот добавлен."
