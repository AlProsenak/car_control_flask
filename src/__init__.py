from datetime import datetime
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import BigInteger, SmallInteger, DECIMAL

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://dbuser:dbpasswd@localhost:3306/carctrl"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Initialize Flask-Migrate extension, which allows for `flask db` migration commands to be run
migrate = Migrate(app, db, directory='src/db/migrations')


# MODELS
class Vehicle(db.Model):
    __tablename__ = 'vehicle'

    id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    make = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(SmallInteger, nullable=False)
    fuel_type = db.Column(db.String(50), nullable=False)
    door_count = db.Column(SmallInteger, nullable=False)
    price = db.Column(DECIMAL(32, 8), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)

    def __repr__(self) -> str:
        return (f"<Vehicle(id={self.id}, make='{self.make}', model='{self.model}', year={self.year}, "
                f"fuel_type='{self.fuel_type}', door_count={self.door_count}, "
                f"price={self.price}), currency_code={self.currency_code})>")

    def __init__(self, make, model, year, fuel_type, door_count, price, currency_code, id=None):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.fuel_type = fuel_type
        self.door_count = door_count
        self.price = price
        self.currency_code = currency_code

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
    "min_length": 1,
    "max_length": 20
}

model_attribute = {
    "type": "string",
    "min_length": 1,
    "max_length": 20
}

year_attribute = {
    "type": "integer",
    "format": "yyyy",
    "minimum": 1900,
    "maximum": datetime.now().year
}

fuel_type_attribute = {
    "type": "string",
    "enum": ["Diesel", "Electric", "Gasoline"]
}

door_count_attribute = {
    "type": "integer",
    "minimum": 1,
    "maximum": 256
}

price_attribute = {
    "type": "number",
    "minimum": 0
}

currency_code_attribute = {
    "type": "string",
    "enum": ["AUD", "CAD", "CHF", "CNY", "EUR", "GBP", "INR", "JPY", "NZD", "SGD", "USD", "ZAR"]
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
                "currency_code": currency_code_attribute
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
