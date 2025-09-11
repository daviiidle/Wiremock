"""ID generation and validation utilities."""

import logging
import re
import uuid
from typing import Optional


logger = logging.getLogger(__name__)


def new_correlation_id() -> str:
    """Generate new correlation ID for request tracing."""
    correlation_id = str(uuid.uuid4())
    logger.info(f"Generated correlation ID: {correlation_id}")
    return correlation_id


def is_valid_id_format(id_value: str, expected_length: Optional[int] = None) -> bool:
    """Validate ID format (alphanumeric)."""
    if not id_value:
        logger.warning("ID is empty or None")
        return False
    
    # Check alphanumeric pattern
    if not re.match(r'^[a-zA-Z0-9]+$', id_value):
        logger.warning(f"ID contains invalid characters: {id_value}")
        return False
    
    # Check length if specified
    if expected_length and len(id_value) != expected_length:
        logger.warning(f"ID length mismatch: expected {expected_length}, got {len(id_value)}")
        return False
    
    logger.info(f"ID validation passed: {id_value}")
    return True


def is_valid_bsb(bsb: str) -> bool:
    """Validate BSB format (Australian Bank State Branch)."""
    pattern = r'^0\d{5}$'
    is_valid = bool(re.match(pattern, bsb))
    
    if is_valid:
        logger.info(f"BSB validation passed: {bsb}")
    else:
        logger.warning(f"BSB validation failed: {bsb} (expected format: 0XXXXX)")
    
    return is_valid


def is_valid_account_number(account_number: str) -> bool:
    """Validate account number format (8-9 digits)."""
    if not account_number.isdigit():
        logger.warning(f"Account number contains non-digits: {account_number}")
        return False
    
    length = len(account_number)
    is_valid = 8 <= length <= 9
    
    if is_valid:
        logger.info(f"Account number validation passed: {account_number}")
    else:
        logger.warning(f"Account number length invalid: {account_number} (expected 8-9 digits)")
    
    return is_valid


def is_valid_phone_number(phone: str) -> bool:
    """Validate Australian phone number format."""
    pattern = r'^\+614\d{8}$'
    is_valid = bool(re.match(pattern, phone))
    
    if is_valid:
        logger.info(f"Phone number validation passed: {phone}")
    else:
        logger.warning(f"Phone number validation failed: {phone} (expected format: +614XXXXXXXX)")
    
    return is_valid


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    
    if is_valid:
        logger.info(f"Email validation passed: {email}")
    else:
        logger.warning(f"Email validation failed: {email}")
    
    return is_valid