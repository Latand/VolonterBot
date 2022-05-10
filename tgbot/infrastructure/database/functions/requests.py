from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult

from tgbot.infrastructure.database.models import Request


async def add_request(session, chat_id, channel_id, message_id, status='new'):
    insert_stmt = insert(
        Request
    ).values(
        chat_id=chat_id,
        channel_id=channel_id,
        message_id=message_id,
        status=status
    ).on_conflict_do_nothing().returning(Request.id)
    result = await session.execute(insert_stmt)
    await session.commit()
    return result.scalars().first()


async def get_one_request(session, *clauses) -> Request:
    statement = select(Request).where(*clauses)
    result: AsyncResult = await session.execute(statement)
    return result.scalars().first()


async def update_request(session, *clauses, **values):
    statement = update(
        Request
    ).where(
        *clauses
    ).values(
        **values
    )

    await session.execute(statement)
    await session.commit()


async def delete_request_by_id(session, *clauses):
    statement = delete(
        Request
    ).where(
        *clauses
    )

    await session.execute(statement)
    await session.commit()
