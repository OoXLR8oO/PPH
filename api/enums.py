# api/enums.py
import enum


class FilmType(str, enum.Enum):
    COLOUR = "colour"
    BW = "bw"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
