from chat_backend.database.crud import add_file_meta, FileMeta
from chat_backend.tests.common_fixtures import *


@pytest.fixture(scope="function")
def test_chunks_session(db_session):
    session, user_id = db_session

    db_file_meta = add_file_meta(
        session=session,
        user_id=user_id,
        filename="test.pdf"
    )

    file_meta = FileMeta(
        file_id=db_file_meta.file_id,
        filename=db_file_meta.filename
    )

    yield session, user_id, file_meta

    session.rollback()
    session.close()
