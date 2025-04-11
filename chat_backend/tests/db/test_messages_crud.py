from uuid import uuid4

import pytest

from chat_backend.database import add_message, get_messages


@pytest.mark.asyncio
async def test_add_message(test_chunks_session):
    session, user_id, file_meta = test_chunks_session
    content = "Test message"
    is_user = True

    message = await add_message(
        session=session, 
        user_id=user_id, 
        file_id=file_meta.file_id, 
        content=content, 
        is_user=is_user
    )

    assert message.id is not None
    assert message.user_id == user_id
    assert message.file_id == file_meta.file_id
    assert message.content == content
    assert message.is_user_message is True


@pytest.mark.asyncio
async def test_get_messages(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    # Add multiple messages
    await add_message(session, user_id, file_meta.file_id, "Message 1", True)
    await add_message(session, user_id, file_meta.file_id, "Message 2", False)
    await add_message(session, user_id, file_meta.file_id, "Message 3", True)

    messages = await get_messages(session, user_id, file_meta.file_id)

    assert len(messages) == 3
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 2"
    assert messages[2].content == "Message 3"


@pytest.mark.asyncio
async def test_add_message_invalid_file_id(test_chunks_session):
    session, user_id, _ = test_chunks_session
    content = "Orphan message"
    is_user = False
    fake_file_id = uuid4()

    with pytest.raises(Exception):
        await add_message(
            session=session,
            user_id=user_id,
            file_id=fake_file_id,
            content=content,
            is_user=is_user
        )


@pytest.mark.asyncio
async def test_get_messages_with_no_messages(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    messages = await get_messages(session, user_id, file_meta.file_id)

    assert messages == []
