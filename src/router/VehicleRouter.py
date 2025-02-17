from datetime import datetime
from flask import Blueprint, request, abort
from flask_cors import cross_origin
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import asc, desc, and_

from src.auth.Decorator import jwt_required_custom
from src.extensions import db

from src.db.model.VehicleModel import Vehicle
from src.db.schema.VehicleSchema import VehicleSchema
from src.router.VehicleValidationSchema import get_vehicle_validation_schema, create_vehicle_validation_schema, \
    update_vehicle_validation_schema
from src.util.RouterUtil import create_filters, create_pagination

vehicle_router_bp = Blueprint('vehicle_router', __name__)


@cross_origin()
@vehicle_router_bp.route('/api/v1/vehicle', methods=['GET'])
def get_vehicles():
    try:
        validate(request.args, get_vehicle_validation_schema)

        # Filter
        # TODO: refactor query parameters and filters to also work with lists
        # TODO: custom constraint validation for numeric query parameters (year, price) - currently regex is doing half the work
        query_params = request.args.to_dict()

        vehicle_query = Vehicle.query

        # Filters
        filters = create_filters(Vehicle, query_params)
        vehicle_query = vehicle_query.filter(and_(*filters))

        # Sort
        sort_by = query_params.get('sort_by', 'id').lower()
        sort_order = query_params.get('sort_order', 'asc').lower()
        if sort_order == 'desc':
            vehicle_query = vehicle_query.order_by(desc(getattr(Vehicle, sort_by)))
        else:
            vehicle_query = vehicle_query.order_by(asc(getattr(Vehicle, sort_by)))

        # Pagination
        pagination = create_pagination(Vehicle, query_params)

        # Query data
        vehicle_entities = vehicle_query.limit(pagination['page_size']).offset(pagination['offset']).all()

        # Response
        vehicle_schema = VehicleSchema(many=True)
        vehicle_json = vehicle_schema.dump(vehicle_entities)
        return {
            "vehicles": vehicle_json,
            "pageable": pagination
        }
    except ValidationError as e:
        abort(400, e.message)


@cross_origin()
@vehicle_router_bp.route('/api/v1/vehicle/<int:id>', methods=['GET'])
def get_vehicle(id: int):
    vehicle_entity = Vehicle.query.get(id)

    if vehicle_entity is None:
        abort(404, f"Vehicle with ID: {id} not found")

    vehicle_schema = VehicleSchema()
    vehicle_json = vehicle_schema.dump(vehicle_entity)

    return {
        "vehicle": vehicle_json
    }


@cross_origin()
@vehicle_router_bp.route('/api/v1/vehicle', methods=['POST'])
@jwt_required_custom()
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


@cross_origin()
@vehicle_router_bp.route('/api/v1/vehicle', methods=['PUT'])
@jwt_required_custom()
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


@cross_origin()
@vehicle_router_bp.route('/api/v1/vehicle/<int:id>', methods=['DELETE'])
@jwt_required_custom()
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
