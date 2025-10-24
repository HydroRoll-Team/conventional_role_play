from typing import Optional, Any, Dict
import traceback
import logging

logger = logging.getLogger(__name__)


class ConventionalRPError(Exception):
    """基础异常类"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def __str__(self) -> str:
        result = self.message
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            result += f" ({details_str})"
        if self.cause:
            result += f"\nCaused by: {str(self.cause)}"
        return result


class ParserError(ConventionalRPError):
    """解析错误"""
    pass


class RuleError(ConventionalRPError):
    """规则相关错误"""
    pass


class ProcessorError(ConventionalRPError):
    """处理器错误"""
    pass


class ValidationError(ConventionalRPError):
    """验证错误"""
    pass


class ConfigurationError(ConventionalRPError):
    """配置错误"""
    pass


def safe_execute(func, *args, default=None, error_msg="Operation failed", **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_msg}: {e}")
        return default


def format_error(error: Exception, include_traceback: bool = False) -> str:
    error_type = type(error).__name__
    error_msg = str(error)
    
    result = f"[{error_type}] {error_msg}"
    
    if include_traceback:
        tb = traceback.format_exc()
        result += f"\n\nTraceback:\n{tb}"
    
    return result


def validate_not_none(value: Any, name: str):
    if value is None:
        raise ValidationError(
            f"{name} cannot be None",
            details={"parameter": name}
        )


def validate_type(value: Any, expected_type: type, name: str):
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{name} must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}",
            details={
                "parameter": name,
                "expected_type": expected_type.__name__,
                "actual_type": type(value).__name__
            }
        )


def validate_not_empty(value: Any, name: str):
    if not value:
        raise ValidationError(
            f"{name} cannot be empty",
            details={"parameter": name, "value": value}
        )
