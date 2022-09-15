from ..models.main import Module


def get_module_with_id(module_id):
    return Module.query.get(module_id)


def get_all_modules():
    return Module.query.all()


def get_modules_with_ids(module_ids):
    return Module.query.filter(Module.id.in_(module_ids)).all()
