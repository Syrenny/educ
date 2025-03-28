from io import BytesIO


def test_upload_file(client, upload_files_headers):
    """Test uploading a file."""
    files = [('files', ('test.txt', BytesIO(b"test-text"), 'text/plain'))]
    response = client.post(
        "/files",
        files=files,
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert response.json()[0]["meta"]["filename"] == "test.txt"


def test_list_files(client, upload_files_headers):
    """Test listing uploaded files."""
    response = client.get(
        "/files",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_download_file(client, upload_files_headers):
    """Test downloading an uploaded file."""
    response = client.get(
        "/files/test.txt",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert response.content == b"test-text"


def test_delete_file(client, upload_files_headers):
    """Test deleting a file."""
    response = client.delete(
        "/files/test.txt",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert response.json() is True


def test_download_nonexistent_file(client, upload_files_headers):
    """Test downloading a nonexistent file returns 404."""
    response = client.get(
        "/files/nonexistent.txt",
        headers=upload_files_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_file(client, upload_files_headers):
    """Test deleting a nonexistent file returns False."""
    response = client.delete(
        "/files/nonexistent.txt",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert response.json() is False
