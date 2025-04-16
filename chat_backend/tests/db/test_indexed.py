import pytest 

from chat_backend.database import add_file_meta, is_indexed, set_indexed, AsyncSession


@pytest.mark.asyncio
async def test_is_indexed_and_set_indexed(db_session: AsyncSession):
    session, user_id = db_session
    file_id = None
    filename = "example.pdf"

    file_meta = await add_file_meta(session, user_id=user_id, filename=filename)
    file_id = file_meta.file_id
    await session.commit()

    assert await is_indexed(session, user_id, file_id) is False or None

    updated = await set_indexed(session, user_id, file_id)
    await session.commit()

    assert updated is True
    assert await is_indexed(session, user_id, file_id) is True
