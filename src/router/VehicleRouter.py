from datetime import datetime
from flask import Blueprint, request, abort
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import asc, desc, and_

from src.extensions import db

from src.db.model.VehicleModel import Vehicle
from src.db.schema.VehicleSchema import VehicleSchema
from src.router.VehicleValidationSchema import get_vehicle_validation_schema, create_vehicle_validation_schema, \
    update_vehicle_validation_schema

vehicle_router_bp = Blueprint('vehicle_router', __name__)


@vehicle_router_bp.route('/api/v1/vehicle', methods=['GET'])
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


@vehicle_router_bp.route('/api/v1/vehicle', methods=['POST'])
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


@vehicle_router_bp.route('/api/v1/vehicle', methods=['PUT'])
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


@vehicle_router_bp.route('/api/v1/vehicle/<int:id>', methods=['DELETE'])
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
