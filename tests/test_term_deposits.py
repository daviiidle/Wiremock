"""Unit tests for Term Deposits API endpoints."""

import logging
import pytest

from tests.helpers.http import APIClient
from tests.helpers.dates import is_valid_date_format, add_months_iso, today_iso, validate_date_range
from tests.helpers.ids import is_valid_id_format


logger = logging.getLogger(__name__)


class TestTermDepositsAPI:
    """Test cases for Term Deposits API endpoints."""
    
    def test_get_term_deposit_success(self, api_client: APIClient, request_headers: dict):
        """Test successful GET /term-deposits/{id} with seeded data."""
        deposit_id = "TD001"
        
        logging.info(f"Testing GET /term-deposits/{deposit_id}")
        response = api_client.get(f"/term-deposits/{deposit_id}", headers=request_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        logging.info(f"Term deposit data received: {data}")
        
        assert data["depositId"] == deposit_id
        assert is_valid_id_format(data["depositId"])
        assert is_valid_id_format(data["customerId"])
        assert isinstance(data["principal"], (int, float, str))
        assert isinstance(data["interestRate"], (int, float, str))
        assert isinstance(data["termMonths"], (int, str))
        assert is_valid_date_format(data["startDate"])
        assert is_valid_date_format(data["maturityDate"])
        assert is_valid_date_format(data["createdAt"].split()[0])
        
        # Validate interest rate range for term deposits
        rate = float(data["interestRate"])
        assert 0 < rate < 20, f"Interest rate {rate} should be between 0 and 20"
        
        # Validate principal amount
        principal = float(data["principal"])
        assert principal > 0, f"Principal {principal} should be positive"
        
        # Start date should be today or recent
        expected_start = today_iso()
        assert validate_date_range(data["startDate"], expected_start, tolerance_days=1)
    
    def test_get_term_deposit_not_found(self, api_client: APIClient, request_headers: dict):
        """Test GET /term-deposits/{id} with unknown ID returns 404."""
        deposit_id = "unknown123"
        
        logging.info(f"Testing GET /term-deposits/{deposit_id} (not found)")
        response = api_client.get(f"/term-deposits/{deposit_id}", headers=request_headers)
        
        assert response.status_code == 404
        
        data = response.json()
        logging.info(f"Error response: {data}")
        
        assert data["error"] == "Term deposit not found"
        assert data["code"] == "TERM_DEPOSIT_NOT_FOUND"
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_term_deposit_success(self, api_client: APIClient, request_headers: dict):
        """Test successful POST /term-deposits with valid payload."""
        payload = {
            "customerId": "CUST001",
            "principal": 100000.00,
            "termMonths": 24,
            "interestRate": 4.75
        }
        
        logging.info(f"Testing POST /term-deposits with payload: {payload}")
        response = api_client.post("/term-deposits", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created term deposit: {data}")
        
        assert is_valid_id_format(data["depositId"])
        assert data["customerId"] == payload["customerId"]
        assert float(data["principal"]) == payload["principal"]
        assert int(data["termMonths"]) == payload["termMonths"]
        assert float(data["interestRate"]) == payload["interestRate"]
        assert is_valid_date_format(data["startDate"])
        assert is_valid_date_format(data["maturityDate"])
        assert is_valid_date_format(data["createdAt"].split()[0])
        
        # Validate start date is today
        expected_start = today_iso()
        assert validate_date_range(data["startDate"], expected_start, tolerance_days=1)
        
        # Validate maturity date is term months from start date
        expected_maturity = add_months_iso(data["startDate"], payload["termMonths"])
        assert validate_date_range(data["maturityDate"], expected_maturity, tolerance_days=2)
    
    def test_post_term_deposit_minimal_payload(self, api_client: APIClient, request_headers: dict):
        """Test POST /term-deposits with minimal required fields."""
        payload = {
            "customerId": "CUST002",
            "principal": 50000.00,
            "termMonths": 12
        }
        
        logging.info(f"Testing POST /term-deposits with minimal payload: {payload}")
        response = api_client.post("/term-deposits", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created term deposit (minimal): {data}")
        
        assert is_valid_id_format(data["depositId"])
        assert data["customerId"] == payload["customerId"]
        assert float(data["principal"]) == payload["principal"]
        assert int(data["termMonths"]) == payload["termMonths"]
        
        # Default interest rate should be applied
        assert isinstance(data["interestRate"], (int, float, str))
        rate = float(data["interestRate"])
        assert 2.50 <= rate <= 8.99, f"Default interest rate {rate} should be in range 2.50-8.99"
        
        # Validate dates
        expected_start = today_iso()
        assert validate_date_range(data["startDate"], expected_start, tolerance_days=1)
        
        expected_maturity = add_months_iso(data["startDate"], payload["termMonths"])
        assert validate_date_range(data["maturityDate"], expected_maturity, tolerance_days=2)
    
    def test_post_term_deposit_short_term(self, api_client: APIClient, request_headers: dict):
        """Test POST /term-deposits with 3-month term."""
        payload = {
            "customerId": "CUST003",
            "principal": 25000.00,
            "termMonths": 3,
            "interestRate": 3.25
        }
        
        logging.info(f"Testing POST /term-deposits with short term: {payload}")
        response = api_client.post("/term-deposits", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created short-term deposit: {data}")
        
        assert int(data["termMonths"]) == 3
        assert float(data["interestRate"]) == 3.25
        
        # Validate 3-month maturity calculation
        expected_maturity = add_months_iso(data["startDate"], 3)
        assert validate_date_range(data["maturityDate"], expected_maturity, tolerance_days=2)
    
    def test_post_term_deposit_long_term(self, api_client: APIClient, request_headers: dict):
        """Test POST /term-deposits with 60-month term."""
        payload = {
            "customerId": "CUST001",
            "principal": 200000.00,
            "termMonths": 60
        }
        
        logging.info(f"Testing POST /term-deposits with long term: {payload}")
        response = api_client.post("/term-deposits", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created long-term deposit: {data}")
        
        assert int(data["termMonths"]) == 60
        assert float(data["principal"]) == 200000.00
        
        # Validate 60-month maturity calculation
        expected_maturity = add_months_iso(data["startDate"], 60)
        assert validate_date_range(data["maturityDate"], expected_maturity, tolerance_days=3)
    
    def test_post_term_deposit_missing_fields(self, api_client: APIClient, request_headers: dict):
        """Test POST /term-deposits with missing required fields returns 400."""
        payload = {
            "customerId": "CUST001",
            "principal": 75000.00
            # Missing termMonths
        }
        
        logging.info(f"Testing POST /term-deposits with incomplete payload: {payload}")
        response = api_client.post("/term-deposits", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "principal" in data["requiredFields"]
        assert "termMonths" in data["requiredFields"]
        assert is_valid_date_format(data["timestamp"].split()[0])