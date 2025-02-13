from datetime import datetime

from src.db.model.VehicleModel import (
    CurrencyCode, FuelType,
    make_db_min_len, make_db_max_len, model_db_min_len, model_db_max_len, year_db_min,
    door_count_db_max, door_count_db_min, price_db_min, description_db_max_len, description_db_min_len
)

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
