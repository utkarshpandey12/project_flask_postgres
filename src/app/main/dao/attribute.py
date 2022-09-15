from ..models.main import Attribute


def get_attribute_with_id(attribute_id):
    return Attribute.query.get(attribute_id)


def get_all_attributes():
    return Attribute.query.all()


def get_attributes_with_ids(attribute_ids):
    return Attribute.query.filter(Attribute.id.in_(attribute_ids)).all()
