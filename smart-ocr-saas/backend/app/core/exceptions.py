"""
Custom exceptions for the application.
"""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "認證失敗"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(AppException):
    """Authorization failed."""

    def __init__(self, message: str = "無權限存取"):
        super().__init__(message, code="AUTHORIZATION_ERROR")


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "資源不存在"):
        super().__init__(message, code="NOT_FOUND")


class ValidationError(AppException):
    """Validation failed."""

    def __init__(self, message: str = "驗證失敗"):
        super().__init__(message, code="VALIDATION_ERROR")


class FileUploadError(AppException):
    """File upload failed."""

    def __init__(self, message: str = "檔案上傳失敗"):
        super().__init__(message, code="FILE_UPLOAD_ERROR")


class OCRProcessingError(AppException):
    """OCR processing failed."""

    def __init__(self, message: str = "OCR 處理失敗"):
        super().__init__(message, code="OCR_PROCESSING_ERROR")


class LDAPConnectionError(AppException):
    """LDAP connection failed."""

    def __init__(self, message: str = "LDAP 連線失敗"):
        super().__init__(message, code="LDAP_CONNECTION_ERROR")


class ServiceUnavailableError(AppException):
    """External service unavailable."""

    def __init__(self, message: str = "服務暫時無法使用"):
        super().__init__(message, code="SERVICE_UNAVAILABLE")
