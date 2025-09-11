"""Unit tests for Loans API endpoints."""

import logging
import pytest

from tests.helpers.http import APIClient
from tests.helpers.dates import is_valid_date_format, add_months_iso, today_iso, validate_date_range
from tests.helpers.ids import is_valid_id_format


logger = logging.getLogger(__name__)


class TestLoansAPI:
    """Test cases for Loans API endpoints."""
    
    def test_get_loan_success(self, api_client: APIClient, request_headers: dict):
        """Test successful GET /loans/{id} with seeded data."""
        loan_id = "LOAN001"
        
        logging.info(f"Testing GET /loans/{loan_id}")
        response = api_client.get(f"/loans/{loan_id}", headers=request_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        logging.info(f"Loan data received: {data}")
        
        assert data["loanId"] == loan_id
        assert is_valid_id_format(data["loanId"])
        assert is_valid_id_format(data["customerId"])
        assert isinstance(data["principal"], (int, float, str))
        assert isinstance(data["interestRate"], (int, float, str))
        assert isinstance(data["termMonths"], (int, str))
        assert isinstance(data["repaymentFrequency"], str)
        assert is_valid_date_format(data["nextPaymentDate"])
        assert is_valid_date_format(data["createdAt"].split()[0])
        
        # Validate interest rate range
        rate = float(data["interestRate"])
        assert 0 < rate < 20, f"Interest rate {rate} should be between 0 and 20"
        
        # Validate principal amount
        principal = float(data["principal"])
        assert principal > 0, f"Principal {principal} should be positive"
    
    def test_get_loan_not_found(self, api_client: APIClient, request_headers: dict):
        """Test GET /loans/{id} with unknown ID returns 404."""
        loan_id = "unknown123"
        
        logging.info(f"Testing GET /loans/{loan_id} (not found)")
        response = api_client.get(f"/loans/{loan_id}", headers=request_headers)
        
        assert response.status_code == 404
        
        data = response.json()
        logging.info(f"Error response: {data}")
        
        assert data["error"] == "Loan not found"
        assert data["code"] == "LOAN_NOT_FOUND"
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_loan_success(self, api_client: APIClient, request_headers: dict):
        """Test successful POST /loans with valid payload."""
        payload = {
            "customerId": "CUST001",
            "principal": 150000.00,
            "termMonths": 240,
            "interestRate": 5.25,
            "repaymentFrequency": "monthly"
        }
        
        logging.info(f"Testing POST /loans with payload: {payload}")
        response = api_client.post("/loans", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created loan: {data}")
        
        assert is_valid_id_format(data["loanId"])
        assert data["customerId"] == payload["customerId"]
        assert float(data["principal"]) == payload["principal"]
        assert int(data["termMonths"]) == payload["termMonths"]
        assert float(data["interestRate"]) == payload["interestRate"]
        assert data["repaymentFrequency"] == payload["repaymentFrequency"]
        assert is_valid_date_format(data["nextPaymentDate"])
        assert is_valid_date_format(data["createdAt"].split()[0])
        
        # Validate next payment date is approximately 1 month from now
        expected_date = add_months_iso(today_iso(), 1)
        assert validate_date_range(data["nextPaymentDate"], expected_date, tolerance_days=2)
    
    def test_post_loan_minimal_payload(self, api_client: APIClient, request_headers: dict):
        """Test POST /loans with minimal required fields."""
        payload = {
            "customerId": "CUST002",
            "principal": 75000.00,
            "termMonths": 180
        }
        
        logging.info(f"Testing POST /loans with minimal payload: {payload}")
        response = api_client.post("/loans", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created loan (minimal): {data}")
        
        assert is_valid_id_format(data["loanId"])
        assert data["customerId"] == payload["customerId"]
        assert float(data["principal"]) == payload["principal"]
        assert int(data["termMonths"]) == payload["termMonths"]
        
        # Default values should be applied
        assert isinstance(data["interestRate"], (int, float, str))
        rate = float(data["interestRate"])
        assert 3.50 <= rate <= 15.99, f"Default interest rate {rate} should be in range 3.50-15.99"
        
        assert data["repaymentFrequency"] == "monthly"  # Default value
        assert is_valid_date_format(data["nextPaymentDate"])
    
    def test_post_loan_missing_fields(self, api_client: APIClient, request_headers: dict):
        """Test POST /loans with missing required fields returns 400."""
        payload = {
            "customerId": "CUST001",
            "principal": 50000.00
            # Missing termMonths
        }
        
        logging.info(f"Testing POST /loans with incomplete payload: {payload}")
        response = api_client.post("/loans", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "principal" in data["requiredFields"]
        assert "termMonths" in data["requiredFields"]
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_loan_weekly_repayment(self, api_client: APIClient, request_headers: dict):
        """Test POST /loans with weekly repayment frequency."""
        payload = {
            "customerId": "CUST003",
            "principal": 25000.00,
            "termMonths": 60,
            "repaymentFrequency": "weekly"
        }
        
        logging.info(f"Testing POST /loans with weekly repayment: {payload}")
        response = api_client.post("/loans", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created weekly loan: {data}")
        
        assert data["repaymentFrequency"] == "weekly"
        assert is_valid_id_format(data["loanId"])
        assert float(data["principal"]) == payload["principal"]