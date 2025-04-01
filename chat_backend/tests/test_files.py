from io import BytesIO
from pathlib import Path

import fitz

from chat_backend.settings import settings


def test_upload_txt_file(client, upload_files_headers):
    """Test uploading a file."""
    files = [('files', ('test.txt', BytesIO(b"test-text"), 'text/plain'))]
    response = client.post(
        "/files",
        files=files,
        headers=upload_files_headers
    )
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]
    
    
def test_upload_pdf_file(client, upload_files_headers, valid_pdf):
    """Test uploading a valid PDF file."""
    files = [('files', ('test.pdf', valid_pdf, 'application/pdf'))]
    response = client.post(
        "/files", 
        files=files, 
        headers=upload_files_headers
    )
    
    assert response.status_code == 200
    assert response.json()[0]["filename"] == "test.pdf"
    
    
def test_upload_image_file(client, upload_files_headers):
    """Test uploading an invalid non-PDF file (PNG)."""
    files = {'files': ('image.png', b"PNG data", 'image/png')}
    response = client.post(
        "/files", 
        files=files, 
        headers=upload_files_headers
    )

    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


def test_upload_multiple_invalid_files(client, upload_files_headers, valid_pdf):
    """Test uploading multiple files where one is invalid."""
    files = [
        ('files', ('valid.pdf', valid_pdf, 'application/pdf')),
        ('files', ('invalid.txt', b"some text", 'text/plain')),
    ]
    response = client.post("/files", files=files, headers=upload_files_headers)

    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]
    
    
def test_upload_multiple_files(client, upload_files_headers, valid_pdf):
    """Test uploading multiple files."""
    files = [
        ('files', ('valid.pdf', valid_pdf, 'application/pdf')),
        ('files', ('other.pdf', valid_pdf, 'application/pdf')),
    ]
    response = client.post("/files", files=files, headers=upload_files_headers)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "valid.pdf"
    assert response.json()[1]["filename"] == "other.pdf"
    
    
def test_upload_many_pdfs(client, upload_files_headers, valid_pdf):
    """Test uploading many pdfs."""
    
    files = [
        ("files", (f"valid{i}.pdf", valid_pdf, "application/pdf"))
        for i in range(settings.max_files_per_user + 1)
    ]

    response = client.post(
        "/files",
        files=files,
        headers=upload_files_headers
    )

    assert response.status_code == 400
    assert response.json()[
        'detail'] == f"File limit exceeded: maximum {settings.max_files_per_user} files allowed"


def test_upload_too_big_pdf(client, upload_files_headers):
    pass
    

def test_upload_encrypted_files(client, upload_files_headers):
    """Test uploading encrypted pdf file."""

    pdf_path = Path("./chat_backend/tests/files/encrypted.pdf")

    doc = fitz.open()
    doc.new_page(width=612, height=792)
    doc.save(pdf_path, encryption=fitz.PDF_ENCRYPT_AES_256,
             owner_pw="password", user_pw="password")

    with open(pdf_path, "rb") as f:
        files = {"files": ("encrypted.pdf", f, "application/pdf")}
        response = client.post(
            "/files",
            files=files,
            headers=upload_files_headers
        )

    assert response.status_code == 400
    assert "Encrypted PDF" in response.json()["detail"]


def test_list_file(client, valid_pdf, upload_files_headers):
    """Test listing uploaded file."""
    files = [
        ('files', ('valid.pdf', valid_pdf, 'application/pdf')),
    ]
    response = client.post(
        "/files", 
        files=files, 
        headers=upload_files_headers
    )

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "valid.pdf"

    response = client.get(
        "/files",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert "valid.pdf" == response.json()[0]["filename"]

    
    
def test_list_multiple_files(client, upload_files_headers, valid_pdf):
    """Test listing multiple uploaded files"""
    files = [
        ('files', ('valid.pdf', valid_pdf, 'application/pdf')),
        ('files', ('other.pdf', valid_pdf, 'application/pdf')),
    ]
    response = client.post("/files", files=files, headers=upload_files_headers)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "valid.pdf"
    assert response.json()[1]["filename"] == "other.pdf"
    
    response = client.get(
        "/files",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    response_files = [f["filename"] for f in response.json()]
    
    assert len(response_files) == 2
    assert "valid.pdf" in response_files
    assert "other.pdf" in response_files
    

def test_download_file(client, upload_files_headers, valid_pdf):
    """Test downloading a file."""
    files = {'files': ('test.pdf', valid_pdf, 'application/pdf')}
    response = client.post(
        "/files", 
        files=files, 
        headers=upload_files_headers
    )

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "test.pdf"

    response = client.get(
        f"/files/{response.json()[0]['file_id']}", headers=upload_files_headers
    )
 
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert response.headers["content-disposition"] == 'attachment; filename="test.pdf"'
    assert response.content == valid_pdf
    

def test_download_nonexistent_file(client, upload_files_headers):
    """Test downloading a nonexistent file returns 404."""
    response = client.get(
        "/files/nonexistent.txt",
        headers=upload_files_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


def test_delete_file(client, upload_files_headers, valid_pdf):
    """Test deleting a file."""
    files = {'files': ('test.pdf', valid_pdf, 'application/pdf')}
    response = client.post("/files", files=files, headers=upload_files_headers)

    assert response.status_code == 200
    assert response.json()[0]["filename"] == "test.pdf"
    
    file_id = response.json()[0]['file_id']
    
    response = client.delete(
        f"/files/{file_id}",
        headers=upload_files_headers
    )
    assert response.status_code == 200
    assert response.json() is True
    
    response = client.get(
        f"/files/{file_id}",
        headers=upload_files_headers
    )
    assert response.status_code == 404


def test_delete_nonexistent_file(client, upload_files_headers):
    """Test deleting a nonexistent file returns False."""
    file_id = 12345
    response = client.delete(
        f"/files/{file_id}",
        headers=upload_files_headers
    )
    assert response.status_code == 500
    assert response.json()["detail"] == f"Failed to delete the file {file_id} from storage."
