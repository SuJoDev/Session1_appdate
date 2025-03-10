from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, selectinload
from sqlalchemy import select, ForeignKey, DateTime

from datetime import date, datetime


class Base(DeclarativeBase):
    pass

class UsersModel(Base):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    name: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    
class DepartModel(Base):
    __tablename__ = "Departs"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    depart_name: Mapped[str] = mapped_column()
    discription: Mapped[str] = mapped_column()
    
    stuff: Mapped[list["StuffModel"]] = relationship("StuffModel", back_populates="depart")
    
class PostModel(Base):
    __tablename__ = "Posts"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    post_name: Mapped[str] = mapped_column()
    
    stuff: Mapped[list["StuffModel"]] = relationship("StuffModel", back_populates="post")
    
class RoomModel(Base):
    __tablename__ = "Rooms"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    room_name: Mapped[str] = mapped_column()
    
    stuff: Mapped[list["StuffModel"]] = relationship("StuffModel", back_populates="room")
    
class CalendarEventsModel(Base):
    __tablename__ = "EventsCalendar"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    event_id: Mapped[int] = mapped_column(ForeignKey("Events.id"))
    training_id: Mapped[int] = mapped_column(ForeignKey("Trainings.id"))
    date_start: Mapped[date] = mapped_column()
    date_end: Mapped[date] = mapped_column()
    stuff_id: Mapped[int] = mapped_column(ForeignKey("Stuff.id"))
    
class TrainingTypeModel(Base):
    __tablename__ = "TrainingTypes"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    training_type_name: Mapped[str] = mapped_column()    
    
class TrainingModel(Base):
    __tablename__ = "Trainings"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    name: Mapped[str] = mapped_column()
    training_type_id: Mapped[int] = mapped_column(ForeignKey("TrainingTypes.id"))
    
class EventTypeModel(Base):
    __tablename__ = "EventTypes"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    event_type_name: Mapped[str] = mapped_column()
    
class EventModel(Base):
    __tablename__ = "Events"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    event_name: Mapped[str] = mapped_column()
    event_type_id: Mapped[int] = mapped_column(ForeignKey("EventTypes.id"))
    status: Mapped[str] = mapped_column()
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    event_admin: Mapped[int] = mapped_column(ForeignKey("Stuff.id"))
    event_discription: Mapped[str] = mapped_column()
        
class StuffModel(Base):
    __tablename__ = "Stuffs"
    
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement= True)
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    birthday: Mapped[date] = mapped_column()
    depart_id: Mapped[int] = mapped_column(ForeignKey("Departs.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("Posts.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("Rooms.id"))
    email: Mapped[str] = mapped_column()
    other_info: Mapped[str] = mapped_column()
    
    depart: Mapped["DepartModel"] = relationship("DepartModel", back_populates="stuff")
    post: Mapped["PostModel"] = relationship("PostModel", back_populates="stuff")
    room: Mapped["RoomModel"] = relationship("RoomModel", back_populates="stuff")