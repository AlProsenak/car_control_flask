from src.db.model.VehicleModel import Vehicle

from src.extensions import ma

class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        ordered = True
