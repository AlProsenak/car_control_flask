from datetime import datetime
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import BigInteger, SmallInteger, DECIMAL

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://dbuser:dbpasswd@localhost:3306/carctrl"

db = SQLAlchemy(app)

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


# DUMMY VEHICLE DATABASE
vehicles = [
    {
        "id": 1,
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "fuel_type": "Gasoline",
        "door_count": 4,
        "price": 20000.00,
        "currency_code": "USD"
    },
    {
        "id": 2,
        "make": "Honda",
        "model": "Civic",
        "year": 2019,
        "fuel_type": "Gasoline",
        "door_count": 4,
        "price": 18000.00,
        "currency_code": "USD"
    },
    {
        "id": 3,
        "make": "Ford",
        "model": "Mustang",
        "year": 2021,
        "fuel_type": "Gasoline",
        "door_count": 2,
        "price": 45000.00,
        "currency_code": "USD"
    },
    {
        "id": 4,
        "make": "Tesla",
        "model": "Model S",
        "year": 2022,
        "fuel_type": "Electric",
        "door_count": 4,
        "price": 80000.00,
        "currency_code": "USD"
    },
    {
        "id": 5,
        "make": "Chevrolet",
        "model": "Silverado",
        "year": 2020,
        "fuel_type": "Diesel",
        "door_count": 4,
        "price": 25000.00,
        "currency_code": "USD"
    }
]
next_id = len(vehicles) + 1


# ERROR HANDLERS
@app.errorhandler(400)
def bad_request(error):
    response = {
        "status": 400,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }
    return response, 400


@app.errorhandler(404)
def not_found(error):
    response = {
        "status": 404,
        "message": error.description,
        "timestamp": datetime.now().isoformat()
    }
    return response, 404


# VALIDATION SCHEMAS
create_vehicle_schema = {
    "type": "object",
    "properties": {
        "vehicle": {
            "type": "object",
            "properties": {
                "make": {
                    "type": "string",
                    "min_length": 1,
                    "max_length": 20
                },
                "model": {
                    "type": "string",
                    "min_length": 1,
                    "max_length": 20
                },
                "year": {
                    "type": "integer",
                    "maximum": datetime.now().year,
                },
                "fuel_type": {
                    "type": "string",
                    "enum": ["Gasoline", "Electric", "Diesel"]
                },
                "door_count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 256
                },
                "price": {
                    "type": "number",
                    "minimum": 0
                },
                "currency_code": {
                    "type": "string",
                    "enum": ["AUD", "CAD", "CHF", "CNY", "EUR", "GBP", "INR", "JPY", "NZD", "SGD", "USD", "ZAR"]
                }
            },
            "required": ["make", "model", "year", "fuel_type", "door_count", "price", "currency_code"]
        }
    },
    "required": ["vehicle"]
}

update_vehicle_schema = {
    "allOf": [
        create_vehicle_schema,
        {
            "type": "object",
            "properties": {
                "vehicle": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "minimum": 1
                        }
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
    return {
        "vehicles": vehicles
    }


@app.route('/api/v1/vehicle/<int:id>', methods=['GET'])
def get_vehicle(id: int):
    for vehicle in vehicles:
        if vehicle["id"] == id:
            return {
                "vehicle": vehicle
            }
        else:
            abort(404, f"Vehicle with ID: {id} not found")


@app.route('/api/v1/vehicle', methods=['POST'])
def create_vehicle():
    global next_id
    try:
        request_data = request.get_json()
        validate(instance=request_data, schema=create_vehicle_schema)

        new_vehicle = request_data['vehicle']
        new_vehicle['id'] = next_id

        vehicles.append(new_vehicle)
        next_id = len(vehicles) + 1

        return {
            "status": 201,
            "message": "success",
            "timestamp": datetime.now().isoformat(),
            "created_vehicle": new_vehicle
        }
    except ValidationError as e:
        abort(400, e.message)


@app.route('/api/v1/vehicle', methods=['PUT'])
def update_vehicle():
    try:
        request_data = request.get_json()
        validate(instance=request_data, schema=update_vehicle_schema)

        search_id = request_data['vehicle']['id']
        updated_vehicle = request_data['vehicle']
        for i, vehicle in enumerate(vehicles):
            if vehicle['id'] == search_id:
                vehicles[i] = updated_vehicle

                return {
                    "status": 200,
                    "message": "success",
                    "timestamp": datetime.now().isoformat(),
                    "updated_vehicle": vehicles[i]
                }
            else:
                abort(404, f"Vehicle with ID: {search_id} not found")
    except ValidationError as e:
        abort(400, e.message)


@app.route('/api/v1/vehicle/<int:id>', methods=['DELETE'])
def delete_vehicle(id: int):
    global next_id

    vehicle_index = -1
    for i, vehicle in enumerate(vehicles):
        if vehicle['id'] == id:
            vehicle_index = i

    if vehicle_index == -1:
        abort(404, f"Vehicle with ID: {id} not found")

    deleted_vehicle = vehicles.pop(vehicle_index)
    next_id = len(vehicles) + 1

    return {
        "status": 200,
        "message": "success",
        "timestamp": datetime.now().isoformat(),
        "deleted_vehicle": deleted_vehicle
    }


if __name__ == '__main__':
    app.run()
