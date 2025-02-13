from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import func, BigInteger, SmallInteger, DECIMAL, String
from sqlalchemy.types import Enum as SQLEnum

from src.extensions import db

make_db_min_len = 1
make_db_max_len = 20
model_db_min_len = 1
model_db_max_len = 50
year_db_min = 1900
price_db_min = 0
door_count_db_min = 0
door_count_db_max = 256
description_db_min_len = 1
description_db_max_len = 1024


class FuelType(Enum):
    DIESEL = "DIESEL"
    ELECTRIC = "ELECTRIC"
    GASOLINE = "GASOLINE"


class CurrencyCode(Enum):
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    USD = "USD"


class Vehicle(db.Model):
    __tablename__ = 'vehicle'

    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    make = db.Column(String(make_db_max_len), nullable=False)
    model = db.Column(String(model_db_max_len), nullable=False)
    year = db.Column(SmallInteger, nullable=False)
    fuel_type = db.Column(SQLEnum(FuelType), nullable=False)
    door_count = db.Column(SmallInteger, nullable=False)
    price = db.Column(DECIMAL(32, 8), nullable=False)
    currency_code = db.Column(SQLEnum(CurrencyCode), nullable=False)
    description = db.Column(String(description_db_max_len), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    db.Index('idx_vehicle_make', make, unique=False)
    db.Index('idx_vehicle_model', model, unique=False)
    db.Index('idx_vehicle_year', year, unique=False)
    db.Index('idx_vehicle_price', price, unique=False)
    db.Index('idx_vehicle_currency_code', currency_code, unique=False)

    db.CheckConstraint(func.length(make) >= make_db_min_len, 'ck_vehicle_make_min_length')
    db.CheckConstraint(func.length(model) >= model_db_min_len, 'ck_vehicle_model_min_length')
    db.CheckConstraint(year >= year_db_min, 'ck_vehicle_year_min')
    # TODO: figure out how to implement current year constraint - MySQL has limitation for non-static constraints
    db.CheckConstraint(door_count >= door_count_db_min, 'ck_vehicle_door_count_min')
    db.CheckConstraint(door_count <= door_count_db_max, 'ck_vehicle_door_count_max')
    db.CheckConstraint(price >= price_db_min, 'ck_vehicle_price_min')
    db.CheckConstraint(func.length(description) >= description_db_min_len, 'ck_vehicle_description_db_len')

    # TODO: adjust to a better format
    def __repr__(self) -> str:
        return (f"<Vehicle(id={self.id}, make='{self.make}', model='{self.model}', year={self.year}, "
                f"fuel_type='{self.fuel_type}', door_count={self.door_count}, "
                f"price={self.price}), currency_code={self.currency_code}), description='{self.description}'>")

    def __init__(self, make, model, year, fuel_type, door_count, price, currency_code, id=None, description=None):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.fuel_type = fuel_type
        self.door_count = door_count
        self.price = price
        self.currency_code = currency_code
        self.description = description

    @classmethod
    def with_id(cls, make, model, year, fuel_type, door_count, price, currency_code, id):
        vehicle = cls(make, model, year, fuel_type, door_count, price, currency_code)
        vehicle.id = id
        return vehicle
