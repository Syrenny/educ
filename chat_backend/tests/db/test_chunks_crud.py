import pytest

from chat_backend.database.crud import (
    save_file_chunks,
    find_file_chunks,
    delete_file_chunks,
    DBChunk,
    select
)


@pytest.mark.asyncio
async def test_save_file_chunks(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    assert user_id is not None

    chunks = ["first", "second", "third"]
    await save_file_chunks(session, user_id, file_meta, chunks)

    await session.commit()

    stmt = select(DBChunk).filter_by(user_id=user_id)
    result = await session.execute(stmt)
    results = result.scalars().all()
    assert len(results) == 3
    assert all(r.file_id == file_meta.file_id for r in results)


@pytest.mark.asyncio
async def test_find_file_chunks(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    assert user_id is not None

    chunks = ["find me please", "just noise", "also find me"]
    await save_file_chunks(session, user_id, file_meta, chunks)
    await session.commit()

    results = await find_file_chunks(session, "find", user_id, file_meta.file_id)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_delete_file_chunks(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    assert user_id is not None

    chunks = ["to be deleted", "also gone"]
    await save_file_chunks(session, user_id, file_meta, chunks)
    await session.commit()

    await delete_file_chunks(session, user_id,
                             file_meta.filename, file_meta.file_id)
    await session.commit()

    stmt = select(DBChunk).filter_by(user_id=user_id)
    result = await session.execute(stmt)
    results = result.scalars().all()

    assert len(results) == 0
