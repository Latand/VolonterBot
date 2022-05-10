from sqlalchemy import Column, VARCHAR, BIGINT, Integer

from tgbot.infrastructure.database.models.base import TimeStampMixin, DatabaseModel


class Request(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)
    chat_id = Column(BIGINT, nullable=False)
    channel_id = Column(BIGINT, nullable=False)
    message_id = Column(Integer, nullable=False)
    status = Column(VARCHAR(255), nullable=False)
