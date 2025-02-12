from datetime import datetime, timezone
from enum import Enum
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import asc, desc, func, and_, BigInteger, SmallInteger, DECIMAL, String
from sqlalchemy.types import Enum as SQLEnum

import os

# APPLICATION SPECIFIC IMPORTS
from src import config

app = Flask(__name__)

environment = os.environ.get('FLASK_ENV', 'local')
print(f"Starting application with environment: {environment}")

if environment == 'local':
    app.config.from_object(config.LocalConfig)
elif environment == 'development':
    app.config.from_object(config.DevelopmentConfig)
else:
    raise ValueError('Invalid environment value: ' + environment)

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


# REGEX
regex_decimal_from_0_to_infinity = "^[0-9]+(\\.[0-9]+)?$"
regex_integer_from_1_to_infinity = "^[1-9][0-9]*$"
# Adjust `2` after `|` operator if higher top limit is desired. Example: `[2-9][0-9]{3}$` -> from 2000 to 9999
regex_integer_from_1900_to_2999 = "^(19[0-9]{2}|2[0-9]{3})$"

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

# Workaround attributes due to query parameters being considered as strings which as a result fails jsonschema validation.
year_query_param_attribute = {
    "type": "string",
    "pattern": regex_integer_from_1900_to_2999,
    # Documentation parameters
    "format": "yyyy",
    "minimum": year_db_min,
    "maximum": datetime.now().year
}

price_query_param_attribute = {
    "type": "string",
    "pattern": regex_decimal_from_0_to_infinity,
    # Documentation parameters
    "minimum": 0
}

page_size_query_param_attribute = {
    "type": "string",
    "pattern": regex_integer_from_1_to_infinity,
    # Documentation parameters
    "minimum": 1
}

page_number_query_param_attribute = {
    "type": "string",
    "pattern": regex_integer_from_1_to_infinity,
    # Documentation parameters
    "minimum": 1
}

# VALIDATION SCHEMAS
get_vehicle_validation_schema = {
    "type": "object",
    "properties": {
        # FILTER
        "make": make_attribute,
        "make_like": make_attribute,
        "model": model_attribute,
        "model_like": model_attribute,
        "year_min": year_query_param_attribute,
        "year_max": year_query_param_attribute,
        "price_min": price_query_param_attribute,
        "price_max": price_query_param_attribute,
        "currency_code": currency_code_attribute,

        # SORT
        "sort_by": {
            "type": "string",
            "enum": ["make", "model", "year", "price", "MAKE", "MODEL", "YEAR", "PRICE"]
        },
        "sort_order": {
            "type": "string",
            "enum": ["asc", "desc", "ASC", "DESC"],
            # Possible case-insensitive alternative approach to an enum
            # "pattern": "^[Aa][Ss][Cc]|[Dd][Ee][Ss][Cc]$"
        },

        # PAGINATION
        "page_size": page_size_query_param_attribute,
        "page_number": page_number_query_param_attribute
    },
    # Disallows query parameters that are not listed in properties
    "additionalProperties": False
}

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
    try:
        validate(request.args, get_vehicle_validation_schema)

        vehicle_query = Vehicle.query

        # Filter
        # TODO: refactor query parameters and filters to also work with lists
        # TODO: custom constraint validation for numeric query parameters (year, price)
        filters = []
        query_params = request.args.to_dict()
        if 'make' in query_params:
            filters.append(Vehicle.make == query_params['make'])
        if 'make_like' in query_params:
            filters.append(Vehicle.make.ilike(f"%{query_params['make_like']}%"))
        if 'model' in query_params:
            filters.append(Vehicle.model == query_params['model'])
        if 'model_like' in query_params:
            filters.append(Vehicle.model.ilike(f"%{query_params['model_like']}%"))
        if 'year_min' in query_params:
            filters.append(Vehicle.year >= query_params['year_min'])
        if 'year_max' in query_params:
            filters.append(Vehicle.year <= query_params['year_max'])
        if 'price_min' in query_params:
            filters.append(Vehicle.price >= query_params['price_min'])
        if 'price_max' in query_params:
            filters.append(Vehicle.price <= query_params['price_max'])
        if 'currency_code' in query_params:
            filters.append(Vehicle.currency_code == query_params['currency_code'])

        if filters:
            vehicle_query = vehicle_query.filter(and_(*filters))

        # Sort
        sort_by = query_params.get('sort_by', 'id').lower()
        sort_order = query_params.get('sort_order', 'asc').lower()
        if sort_order == 'desc':
            vehicle_query = vehicle_query.order_by(desc(getattr(Vehicle, sort_by)))
        else:
            vehicle_query = vehicle_query.order_by(asc(getattr(Vehicle, sort_by)))

        # Pagination
        page_number = int(request.args.get('page_number', 1))
        page_size = int(request.args.get('page_size', 10))

        total_count = vehicle_query.count()
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page_number - 1) * page_size

        first_page = page_number == 1
        last_page = page_number == total_pages
        empty_page = page_number > total_pages or page_number < 1

        # Query data
        vehicle_entities = vehicle_query.limit(page_size).offset(offset).all()

        # Response
        vehicle_schema = VehicleSchema(many=True)
        vehicle_json = vehicle_schema.dump(vehicle_entities)

        pagination = {
            "offset": offset,
            "page_number": page_number,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_elements": total_count,
            "first_page": first_page,
            "last_page": last_page,
            "empty_page": empty_page
        }

        return {
            "vehicles": vehicle_json,
            "pageable": pagination
        }
    except ValidationError as e:
        abort(400, e.message)


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
        vehicle_entity.description = vehicle_data.get('description', None)

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
