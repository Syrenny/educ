from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from server.database import add_message, get_messages
from server.models import Action


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
        is_user=is_user,
        action=Action.default,
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
    await add_message(
        session, user_id, file_meta.file_id, "Message 1", True, action=Action.default
    )
    await add_message(
        session, user_id, file_meta.file_id, "Message 2", False, action=Action.default
    )
    await add_message(
        session, user_id, file_meta.file_id, "Message 3", True, action=Action.default
    )

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

    with pytest.raises(IntegrityError):
        await add_message(
            session=session,
            user_id=user_id,
            file_id=fake_file_id,
            content=content,
            is_user=is_user,
            action=Action.default,
        )


@pytest.mark.asyncio
async def test_get_messages_with_no_messages(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    messages = await get_messages(session, user_id, file_meta.file_id)

    assert messages == []


@pytest.mark.asyncio
async def test_add_message_with_shortcut(test_chunks_session):
    session, user_id, file_meta = test_chunks_session
    content = "Message with shortcut"
    is_user = True

    snippet = "This is a snippet"
    action = Action.explain

    message = await add_message(
        session=session,
        user_id=user_id,
        file_id=file_meta.file_id,
        content=content,
        is_user=is_user,
        action=action,
        snippet=snippet,
    )

    assert message.snippet == snippet
    assert message.action == action.value


@pytest.mark.asyncio
async def test_get_messages_with_shortcut(test_chunks_session):
    session, user_id, file_meta = test_chunks_session

    snippet = "Test snippet"
    action = Action.translate

    await add_message(
        session=session,
        user_id=user_id,
        file_id=file_meta.file_id,
        content="Msg with shortcut",
        is_user=True,
        action=action,
        snippet=snippet,
    )

    messages = await get_messages(session, user_id, file_meta.file_id)

    assert len(messages) == 1
    assert messages[0].snippet == snippet
    assert messages[0].action == action
