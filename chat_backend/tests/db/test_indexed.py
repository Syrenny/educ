from sqlalchemy.orm import Session

from chat_backend.database import add_file_meta, is_indexed, set_indexed


def test_is_indexed_and_set_indexed(db_session: Session):
    session, user_id = db_session
    file_id = None
    filename = "example.pdf"

    file_meta = add_file_meta(session, user_id=user_id, filename=filename)
    file_id = file_meta.file_id
    session.commit()

    assert is_indexed(session, user_id, file_id) is False or None

    updated = set_indexed(session, user_id, file_id)
    session.commit()

    assert updated is True
    assert is_indexed(session, user_id, file_id) is True
