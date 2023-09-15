from typing import Type

from gazebo.db.models import Base


def record_to_orm(record: dict, model_class: Type[Base]) -> Base:
    return model_class(**record)
