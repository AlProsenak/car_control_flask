from typing import Any

from src.extensions import db


def create_filters(model: db.Model, query_params: dict[str, str]) -> list[bool]:
    filters = []
    for param, value in query_params.items():
        parts = param.split('_')
        attr_name = parts[0]
        # None prevents failing when there are passed query parameters such as `sort_by` or `page_size`.
        # TODO: perhaps filter out such query parameters and raise exception instead (fail-fast principle)?
        attr = getattr(model, attr_name, None)
        if attr is None:
            continue

        operator = parts[-1] if len(parts) > 1 and parts[-1] in ('min', 'max', 'like') else None

        if operator == 'min':
            filters.append(attr >= value)
        elif operator == 'max':
            filters.append(attr <= value)
        elif operator == 'like':
            filters.append(attr.ilike(f"%{value}%"))
        else:
            filters.append(attr == value)

    return filters


def create_pagination(model: db.Model, query_params: dict[str, str], default_page_number=1, default_page_size=10) \
        -> dict[str, int | bool | Any]:
    page_number = int(query_params.get('page_number', default_page_number))
    page_size = int(query_params.get('page_size', default_page_size))

    total_count = model.query.count()
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page_number - 1) * page_size

    first_page = page_number == 1
    last_page = page_number == total_pages
    empty_page = page_number > total_pages or page_number < 1

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
    return pagination
