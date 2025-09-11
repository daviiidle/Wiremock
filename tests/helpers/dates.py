"""Date utilities for test validation."""

import logging
from datetime import datetime, date
from typing import Union, Optional
from dateutil.relativedelta import relativedelta


logger = logging.getLogger(__name__)


def today_iso() -> str:
    """Get today's date in ISO format (YYYY-MM-DD)."""
    today = date.today().isoformat()
    logger.info(f"Today's date: {today}")
    return today


def parse_iso_date(date_string: str) -> date:
    """Parse ISO date string to date object."""
    try:
        return datetime.fromisoformat(date_string).date()
    except ValueError as e:
        logger.error(f"Failed to parse date '{date_string}': {e}")
        raise


def add_months_iso(base_date: Union[str, date], months: int) -> str:
    """Add months to base date and return ISO string."""
    if isinstance(base_date, str):
        base_date = parse_iso_date(base_date)
    
    result_date = base_date + relativedelta(months=months)
    result_iso = result_date.isoformat()
    
    logger.info(f"Added {months} months to {base_date} = {result_iso}")
    return result_iso


def date_difference_days(date1: Union[str, date], date2: Union[str, date]) -> int:
    """Calculate difference in days between two dates."""
    if isinstance(date1, str):
        date1 = parse_iso_date(date1)
    if isinstance(date2, str):
        date2 = parse_iso_date(date2)
    
    difference = (date2 - date1).days
    logger.info(f"Date difference: {date1} to {date2} = {difference} days")
    return difference


def is_valid_date_format(date_string: str) -> bool:
    """Check if string is valid ISO date format."""
    try:
        parse_iso_date(date_string)
        return True
    except ValueError:
        logger.warning(f"Invalid date format: {date_string}")
        return False


def validate_date_range(target_date: Union[str, date], 
                       expected_date: Union[str, date], 
                       tolerance_days: int = 2) -> bool:
    """Validate if target date is within tolerance of expected date."""
    if isinstance(target_date, str):
        target_date = parse_iso_date(target_date)
    if isinstance(expected_date, str):
        expected_date = parse_iso_date(expected_date)
    
    diff_days = abs((target_date - expected_date).days)
    is_valid = diff_days <= tolerance_days
    
    logger.info(f"Date validation: target={target_date}, expected={expected_date}, "
               f"diff={diff_days} days, tolerance={tolerance_days} days, valid={is_valid}")
    
    return is_valid