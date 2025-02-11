from datetime import datetime
from enum import Enum
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import func, Column, Index, CheckConstraint, BigInteger, SmallInteger, DECIMAL
from sqlalchemy.types import Enum as SQLEnum

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://dbuser:dbpasswd@localhost:3306/carctrl"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Initialize Flask-Migrate extension, which allows for `flask db` migration commands to be run
migrate = Migrate(app, db, directory='src/db/migrations')

# MODEL TYPES AND CONSTANTS
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


# MODELS
class Vehicle(db.Model):
    __tablename__ = 'vehicle'

    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    make = db.Column(db.String(make_db_max_len), nullable=False)
    model = db.Column(db.String(model_db_max_len), nullable=False)
    year = db.Column(SmallInteger, nullable=False)
    fuel_type = Column(SQLEnum(FuelType), nullable=False)
    door_count = db.Column(SmallInteger, nullable=False)
    price = db.Column(DECIMAL(32, 8), nullable=False)
    currency_code = Column(SQLEnum(CurrencyCode), nullable=False)
    description = db.Column(db.String(description_db_max_len), nullable=True)

    Index('idx_vehicle_make', make, unique=False)
    Index('idx_vehicle_model', model, unique=False)
    Index('idx_vehicle_year', year, unique=False)
    Index('idx_vehicle_price', price, unique=False)
    Index('idx_vehicle_currency_code', currency_code, unique=False)

    CheckConstraint(func.length(make) >= make_db_min_len, 'ck_vehicle_make_min_length')
    CheckConstraint(func.length(model) >= model_db_min_len, 'ck_vehicle_model_min_length')
    CheckConstraint(year >= year_db_min, 'ck_vehicle_year_min')
    # TODO: figure out how to implement current year constraint - MySQL has limitation for non-static constraints
    CheckConstraint(door_count >= door_count_db_min, 'ck_vehicle_door_count_min')
    CheckConstraint(door_count <= door_count_db_max, 'ck_vehicle_door_count_max')
    CheckConstraint(price >= price_db_min, 'ck_vehicle_price_min')
    CheckConstraint(func.length(description) >= description_db_min_len, 'ck_vehicle_description_db_len')

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


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        ordered = True


# ERROR HANDLERS
@app.errorhandler(400)
def bad_request(error):
    response = jsonify({
        "status": 400,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }), 400
    return response


@app.errorhandler(404)
def not_found(error):
    response = jsonify({
        "status": 404,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }), 404
    return response


# VALIDATION SCHEMA ATTRIBUTES
id_attribute = {
    "type": "integer",
    "minimum": 0
}

make_attribute = {
    "type": "string",
    "minLength": make_db_min_len,
    "maxLength": make_db_max_len,
    # Disallows strings that have white space at start, end, or are blank.
    # TODO: test and enable later if it works
    # "pattern": "^\\S.*\\S$|^\\S+$"
}

model_attribute = {
    "type": "string",
    "minLength": model_db_min_len,
    "maxLength": model_db_max_len
}

year_attribute = {
    "type": "integer",
    "format": "yyyy",
    "minimum": year_db_min,
    "maximum": datetime.now().year
}

fuel_type_attribute = {
    "type": "string",
    "enum": [member.value for member in FuelType]
}

door_count_attribute = {
    "type": "integer",
    "minimum": door_count_db_min,
    "maximum": door_count_db_max
}

price_attribute = {
    "type": "number",
    "minimum": price_db_min
}

currency_code_attribute = {
    "type": "string",
    "enum": [member.value for member in CurrencyCode]
}

description_attribute = {
    "type": "string",
    "minLength": description_db_min_len,
    "maxLength": description_db_max_len
}

# VALIDATION SCHEMAS
create_vehicle_validation_schema = {
    "type": "object",
    "properties": {
        "vehicle": {
            "type": "object",
            "properties": {
                "make": make_attribute,
                "model": model_attribute,
                "year": year_attribute,
                "fuel_type": fuel_type_attribute,
                "door_count": door_count_attribute,
                "price": price_attribute,
                "currency_code": currency_code_attribute,
                "description": description_attribute
            },
            "required": ["make", "model", "year", "fuel_type", "door_count", "price", "currency_code"]
        }
    },
    "required": ["vehicle"]
}

update_vehicle_validation_schema = {
    "allOf": [
        create_vehicle_validation_schema,
        {
            "type": "object",
            "properties": {
                "vehicle": {
                    "type": "object",
                    "properties": {
                        "id": id_attribute
                    },
                    "required": ["id"]
                }
            }
        }
    ]
}


# API
@app.route('/api/v1/vehicle', methods=['GET'])
def get_vehicles():
    vehicle_entities = Vehicle.query.all()

    vehicle_schema = VehicleSchema(many=True)
    vehicle_json = vehicle_schema.dump(vehicle_entities)

    return {
        "vehicles": vehicle_json
    }


@app.route('/api/v1/vehicle/<int:id>', methods=['GET'])
def get_vehicle(id: int):
    vehicle_entity = Vehicle.query.get(id)

    if vehicle_entity is None:
        abort(404, f"Vehicle with ID: {id} not found")

    vehicle_schema = VehicleSchema()
    vehicle_json = vehicle_schema.dump(vehicle_entity)

    return {
        "vehicle": vehicle_json
    }


@app.route('/api/v1/vehicle', methods=['POST'])
def create_vehicle():
    try:
        request_data = request.get_json()
        validate(instance=request_data, schema=create_vehicle_validation_schema)

        new_vehicle_data = request_data['vehicle']
        new_vehicle_entity = Vehicle(**new_vehicle_data)

        db.session.add(new_vehicle_entity)
        db.session.commit()

        vehicle_schema = VehicleSchema()
        vehicle_json = vehicle_schema.dump(new_vehicle_entity)

        return {
            "status": 201,
            "message": "success",
            "timestamp": datetime.now().isoformat(),
            "created_vehicle": vehicle_json
        }
    except ValidationError as e:
        abort(400, e.message)


@app.route('/api/v1/vehicle', methods=['PUT'])
def update_vehicle():
    try:
        request_data = request.get_json()
        validate(instance=request_data, schema=update_vehicle_validation_schema)

        search_id = request_data['vehicle']['id']
        vehicle_entity = Vehicle.query.get(search_id)

        if vehicle_entity is None:
            abort(404, f"Vehicle with ID: {search_id} not found")

        vehicle_data = request_data['vehicle']

        # TODO: mapper function
        vehicle_entity.make = vehicle_data['make']
        vehicle_entity.model = vehicle_data['model']
        vehicle_entity.year = vehicle_data['year']
        vehicle_entity.fuel_type = vehicle_data['fuel_type']
        vehicle_entity.door_count = vehicle_data['door_count']
        vehicle_entity.price = vehicle_data['price']
        vehicle_entity.currency_code = vehicle_data['currency_code']
        vehicle_entity.description = vehicle_data['description']

        db.session.commit()

        vehicle_schema = VehicleSchema()
        updated_vehicle_json = vehicle_schema.dump(vehicle_entity)

        return {
            "status": 200,
            "message": "success",
            "timestamp": datetime.now().isoformat(),
            "updated_vehicle": updated_vehicle_json
        }
    except ValidationError as e:
        abort(400, e.message)


@app.route('/api/v1/vehicle/<int:id>', methods=['DELETE'])
def delete_vehicle(id: int):
    vehicle_entity = Vehicle.query.get(id)

    if vehicle_entity is None:
        abort(404, f"Vehicle with ID: {id} not found")

    db.session.delete(vehicle_entity)
    db.session.commit()

    vehicle_schema = VehicleSchema()
    deleted_vehicle_json = vehicle_schema.dump(vehicle_entity)

    return {
        "status": 200,
        "message": "success",
        "timestamp": datetime.now().isoformat(),
        "deleted_vehicle": deleted_vehicle_json
    }


if __name__ == '__main__':
    app.run()
