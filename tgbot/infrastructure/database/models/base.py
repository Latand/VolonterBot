from __future__ import annotations

import re
from typing import Optional, Type, cast, Any, Dict, Pattern, Final

from sqlalchemy import inspect, Column, TIMESTAMP, func
from sqlalchemy.orm import has_inherited_table, declared_attr, declarative_base
from sqlalchemy.orm.decl_api import declarative_mixin
from sqlalchemy.util import ImmutableProperties

# Регулярное выражение, которое разделяет строку по заглавным буквам
TABLE_NAME_REGEX: Pattern[str] = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z])")
PLURAL: Final[str] = "s"

Base = declarative_base()


class DatabaseModel(Base):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    @declared_attr
    def __tablename__(self) -> Optional[str]:
        """
        Автоматически генерирует имя таблицы из названия модели, примеры:

        OrderItem -> order_items
        Order -> orders
        """
        if has_inherited_table(cast(Type[DatabaseModel], self)):
            return None
        cls_name = cast(Type[DatabaseModel], self).__qualname__
        table_name_parts = re.split(TABLE_NAME_REGEX, cls_name)
        formatted_table_name = "".join(
            table_name_part.lower() + "_" for i, table_name_part in enumerate(table_name_parts)
        )
        last_underscore = formatted_table_name.rfind("_")
        return formatted_table_name[:last_underscore] + PLURAL

    def _get_attributes(self) -> Dict[Any, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __str__(self) -> str:
        attributes = " | ".join(f'{k} = {v}' for k, v in self._get_attributes().items())
        return f"{self.__class__.__qualname__}({attributes})"

    def __repr__(self) -> str:
        table_attrs = cast(ImmutableProperties, inspect(self).attrs)
        primary_keys = " ".join(
            f"{key.name}={table_attrs[key.name].value}"
            for key in inspect(self.__class__).primary_key
        )
        return f"{self.__class__.__qualname__}->{primary_keys}"


@declarative_mixin
class TimeStampMixin:
    __abstract__ = True

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_onupdate=func.now(), server_default=func.now())
