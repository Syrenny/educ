import time
import uuid
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import fitz
import pytest

from server.config import config


@pytest.mark.asyncio
async def test_upload_txt_file(client):
    """Test uploading a file."""
    files = [("files", ("test.txt", BytesIO(b"test-text"), "text/plain"))]
    response = await client.post("/api/files", files=files)
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_pdf_file(client, valid_pdf):
    """Test uploading a valid PDF file."""
    files = [("files", ("test.pdf", valid_pdf, "application/pdf"))]
    response = await client.post("/api/files", files=files)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "test.pdf"


@pytest.mark.asyncio
async def test_upload_image_file(client):
    """Test uploading an invalid non-PDF file (PNG)."""
    files = {"files": ("image.png", b"PNG data", "image/png")}
    response = await client.post("/api/files", files=files)

    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_multiple_invalid_files(client, valid_pdf):
    """Test uploading multiple files where one is invalid."""
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
        ("files", ("invalid.txt", b"some text", "text/plain")),
    ]
    response = await client.post("/api/files", files=files)

    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_multiple_files(client, valid_pdf):
    """Test uploading multiple files."""
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
        ("files", ("other.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "valid.pdf"
    assert response.json()[1]["filename"] == "other.pdf"


@pytest.mark.asyncio
async def test_upload_many_pdfs(client, valid_pdf):
    """Test uploading many pdfs."""

    files = [
        ("files", (f"valid{i}.pdf", valid_pdf, "application/pdf"))
        for i in range(config.max_files_per_user + 1)
    ]

    response = await client.post("/api/files", files=files)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == f"File limit exceeded: maximum {config.max_files_per_user} files allowed"
    )


@pytest.mark.asyncio
async def test_upload_too_big_pdf(client):
    pass


@pytest.mark.asyncio
async def test_upload_encrypted_files(client):
    """Test uploading encrypted pdf file."""

    pdf_path = Path("./server/tests/files/encrypted.pdf")

    doc = fitz.open()
    doc.new_page(width=612, height=792)
    doc.save(
        pdf_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="password",
        user_pw="password",
    )

    with open(pdf_path, "rb") as f:
        files = {"files": ("encrypted.pdf", f, "application/pdf")}
        response = await client.post("/api/files", files=files)

    assert response.status_code == 400
    assert "Encrypted PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_file(client, valid_pdf):
    """Test listing uploaded file."""
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "valid.pdf"

    response = await client.get("/api/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert "valid.pdf" == response.json()[0]["filename"]


@pytest.mark.asyncio
async def test_list_multiple_files(client, valid_pdf):
    """Test listing multiple uploaded files"""
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
        ("files", ("other.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "valid.pdf"
    assert response.json()[1]["filename"] == "other.pdf"

    response = await client.get("/api/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    response_files = [f["filename"] for f in response.json()]

    assert len(response_files) == 2
    assert "valid.pdf" in response_files
    assert "other.pdf" in response_files


@pytest.mark.asyncio
async def test_delete_file(client, valid_pdf):
    """Test deleting a file."""
    files = {"files": ("test.pdf", valid_pdf, "application/pdf")}
    response = await client.post("/api/files", files=files)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "test.pdf"

    file_id = response.json()[0]["file_id"]

    response = await client.delete(f"/api/files/{file_id}")
    assert response.status_code == 200
    assert response.json() is True

    response = await client.get(f"/api/files/{file_id}/signed-url")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_file(client):
    """Test deleting a nonexistent file returns False."""
    non_existent_uuid = str(uuid.uuid4())
    response = await client.delete(f"/api/files/{non_existent_uuid}")
    assert response.status_code == 500
    assert (
        response.json()["detail"]
        == f"Failed to delete the file {non_existent_uuid} from storage."
    )


@pytest.mark.asyncio
async def test_get_signed_url(client, valid_pdf):
    """Test generating a signed URL for a file."""

    # Сначала загрузим файл
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)
    assert response.status_code == 200
    file_id = response.json()[0]["file_id"]

    # Получим временную ссылку
    response = await client.get(f"/api/files/{file_id}/signed-url")
    signed_url = response.json()
    assert response.status_code == 200
    assert "expires" in signed_url
    assert "signature" in signed_url
    assert file_id in signed_url
    # Проверим, что возвращенная ссылка корректна

    assert signed_url.startswith(f"/files/{file_id}/download?expires=")
    assert "&signature=" in signed_url


@pytest.mark.asyncio
async def test_download_file_using_link(client, valid_pdf):
    """Test downloading a file using the generated signed URL."""

    # Сначала загрузим файл
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)
    assert response.status_code == 200
    file_id = response.json()[0]["file_id"]

    # Получим временную ссылку
    signed_url_response = await client.get(f"/api/files/{file_id}/signed-url")
    assert signed_url_response.status_code == 200
    signed_url = signed_url_response.json()

    # Пройдем по ссылке для скачивания файла
    response = await client.get("/api" + signed_url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert (
        response.headers["Content-Disposition"]
        == f"attachment; filename=\"download.bin\"; filename*=UTF-8''{quote('valid.pdf')}"
    )
    assert len(response.content) > 0  # Проверим, что файл не пустой


@pytest.mark.asyncio
async def test_download_file_link_expired(client, valid_pdf):
    """Test downloading file with expired signed URL."""

    # Сначала загрузим файл
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)
    assert response.status_code == 200
    file_id = response.json()[0]["file_id"]

    # Получим временную ссылку
    signed_url_response = await client.get(f"/api/files/{file_id}/signed-url")
    assert signed_url_response.status_code == 200
    signed_url = signed_url_response.json()

    # Подождем, чтобы ссылка истекла
    time.sleep(6 * 60)  # 6 минут

    # Попробуем скачать файл
    response = await client.get(signed_url)
    assert response.status_code == 403
    assert response.json()["detail"] == "Link expired"


@pytest.mark.asyncio
async def test_download_file_invalid_signature(client, valid_pdf):
    """Test downloading file with an invalid signature in the signed URL."""

    # Сначала загрузим файл
    files = [
        ("files", ("valid.pdf", valid_pdf, "application/pdf")),
    ]
    response = await client.post("/api/files", files=files)
    assert response.status_code == 200
    file_id = response.json()[0]["file_id"]

    # Получим временную ссылку
    signed_url_response = await client.get(f"/api/files/{file_id}/signed-url")
    assert signed_url_response.status_code == 200
    signed_url = signed_url_response.text

    # Изменим подпись в URL, чтобы она стала неправильной
    invalid_signed_url = signed_url.replace(
        signed_url.split("&signature=")[-1], "invalid_signature"
    )

    # Попробуем скачать файл с измененной подписью
    response = await client.get(invalid_signed_url)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid signature"
