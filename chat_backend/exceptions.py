from enum import Enum

from fastapi import HTTPException


class FileErrorMessages(Enum):
    DELETE_ERROR = "Failed to delete the file {filename} from storage."
    SQL_UPLOAD_ERROR = "SQLAlchemy: Error uploading file"
    SQL_DELETE_ERROR = "SQLAlchemy: Error deleting file"
    INVALID_FILE_TYPE = "Only PDF files are allowed. Invalid file: {filename}"
    ENCRYPTED = "Encrypted PDF files are not allowed: {filename}"
    INVALID_PDF = "Invalid PDF file: {filename}"
    TOO_BIG = "File size exceeds the maximum allowed size of {max_size} bytes"
    FILE_LIMIT_EXCEEDED = "File limit exceeded: maximum {max_files} files allowed"
    FILE_NOT_FOUND = "File not found"


class FileUploadException(HTTPException):
    """Base exception for file upload errors."""

    def __init__(self, error_message: FileErrorMessages, status_code: int, **kwargs):
        self.message = error_message.value.format(**kwargs)
        super().__init__(status_code=status_code, detail=self.message)


class FileDeletionError(FileUploadException):
    def __init__(self, filename: str):
        super().__init__(FileErrorMessages.DELETE_ERROR, 500, filename=filename)


class SQLAlchemyUploadException(FileUploadException):
    def __init__(self):
        super().__init__(FileErrorMessages.SQL_UPLOAD_ERROR, 500)


class SQLAlchemyDeletionException(FileUploadException):
    def __init__(self):
        super().__init__(FileErrorMessages.SQL_DELETE_ERROR, 500)


class InvalidFileTypeException(FileUploadException):
    """Exception for invalid file type (non-PDF)."""

    def __init__(self, filename: str):
        super().__init__(FileErrorMessages.INVALID_FILE_TYPE, 400, filename=filename)


class EncryptedPdfException(FileUploadException):
    """Exception for encrypted PDF files."""

    def __init__(self, filename: str):
        super().__init__(FileErrorMessages.ENCRYPTED, 400, filename=filename)


class InvalidPdfException(FileUploadException):
    """Exception for invalid PDF files."""

    def __init__(self, filename: str):
        super().__init__(FileErrorMessages.INVALID_PDF, 400, filename=filename)


class FileTooLargeException(FileUploadException):
    """Exception for files that exceed the maximum allowed size."""

    def __init__(self, max_size: int):
        super().__init__(FileErrorMessages.TOO_BIG, 413, max_size=max_size)


class FileLimitExceededException(FileUploadException):
    """Exception for when the file limit is exceeded."""

    def __init__(self, max_files: int):
        super().__init__(FileErrorMessages.FILE_LIMIT_EXCEEDED, 400, max_files=max_files)


class FileNotFoundException(FileUploadException):
    """Exception for when the requested file is not found."""

    def __init__(self):
        super().__init__(FileErrorMessages.FILE_NOT_FOUND, 404)
