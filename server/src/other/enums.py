from django.db import models
from enum import Enum


class TimeInterval(Enum):
    one_min = "1 min"
    five_mins = "5 mins"
    half_hour = "30 mins"
    one_hour = "1 hour"
    five_hours = "5 hours"
    twelve_hours = "12 hours"
    one_day = "1 day"


class TaskStatus(Enum):
    active = "Active"
    disabled = "Disabled"


class UnloadServiceType(Enum):
    empty = None
    empty_str = ""
    fortochki = "FORTOCHKI"
    starco = "STARCO"


class CallRequestStatus(str, Enum):
    PRODUCT = "Продукты"
    # рассрочка
    INSTALLMENT = "Рассрочка"


class FormApplicationStatus(str, Enum):
    NEW = "Новый"
    PROGRESS = "В прогрессе"
    COMPLETED = "Завершен"


class OrderStatus(str, Enum):
    NEW = "new"
    PAID = "paid"
    AWAITING = "awaiting"
    CANCELED = "canceled"
    ACCEPTED = "accepted"


class DocumentType(str, Enum):
    INVOICE = "invoice"


class DayOfWeek(models.IntegerChoices):
    MONDAY = 1, "Понедельник"
    TUESDAY = 2, "Вторник"
    WEDNESDAY = 3, "Среда"
    THURSDAY = 4, "Четверг"
    FRIDAY = 5, "Пятница"
    SATURDAY = 6, "Суббота"
    SUNDAY = 7, "Воскресенье"


class ProductType(str, Enum):
    RIMS = "Диски"
    TIRES = "Шины"
    ACCESSORY = "Аксессуары"


class ProductColor(str, Enum):
    GRAY = "gray"
    BLACK = "black"
    WHITE = "white"


class RimType(models.TextChoices):
    ALLOY = '0', 'Литые'
    STAMP = '4', 'Штампованые'
    FORGED = '2', 'Кованые'
    TRUCK = '5', 'Грузовые'


class TireSeason(models.TextChoices):
    summer = 'summer', 'Летние'
    winter = 'winter', 'Зимние'
    universal = 'univ', 'Всесезонные'