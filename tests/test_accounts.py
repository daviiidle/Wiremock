"""Unit tests for Accounts API endpoints."""

import logging
import pytest

from tests.helpers.http import APIClient
from tests.helpers.dates import is_valid_date_format
from tests.helpers.ids import is_valid_id_format, is_valid_bsb, is_valid_account_number


logger = logging.getLogger(__name__)


class TestAccountsAPI:
    """Test cases for Accounts API endpoints."""
    
    def test_get_account_success(self, api_client: APIClient, request_headers: dict):
        """Test successful GET /accounts/{id} with seeded data."""
        account_id = "ACC001"
        
        logging.info(f"Testing GET /accounts/{account_id}")
        response = api_client.get(f"/accounts/{account_id}", headers=request_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        logging.info(f"Account data received: {data}")
        
        assert data["accountId"] == account_id
        assert is_valid_id_format(data["accountId"])
        assert is_valid_id_format(data["customerId"])
        assert is_valid_bsb(data["bsb"])
        assert is_valid_account_number(data["accountNumber"])
        assert isinstance(data["accountType"], str) and len(data["accountType"]) > 0
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_get_account_not_found(self, api_client: APIClient, request_headers: dict):
        """Test GET /accounts/{id} with unknown ID returns 404."""
        account_id = "unknown123"
        
        logging.info(f"Testing GET /accounts/{account_id} (not found)")
        response = api_client.get(f"/accounts/{account_id}", headers=request_headers)
        
        assert response.status_code == 404
        
        data = response.json()
        logging.info(f"Error response: {data}")
        
        assert data["error"] == "Account not found"
        assert data["code"] == "ACCOUNT_NOT_FOUND"
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_account_success(self, api_client: APIClient, request_headers: dict):
        """Test successful POST /accounts with valid payload."""
        payload = {
            "customerId": "CUST001",
            "accountType": "savings"
        }
        
        logging.info(f"Testing POST /accounts with payload: {payload}")
        response = api_client.post("/accounts", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created account: {data}")
        
        assert is_valid_id_format(data["accountId"])
        assert data["customerId"] == payload["customerId"]
        assert is_valid_bsb(data["bsb"])
        assert is_valid_account_number(data["accountNumber"])
        assert data["accountType"] == payload["accountType"]
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_post_account_business_type(self, api_client: APIClient, request_headers: dict):
        """Test POST /accounts with business account type."""
        payload = {
            "customerId": "CUST002",
            "accountType": "business"
        }
        
        logging.info(f"Testing POST /accounts with business type: {payload}")
        response = api_client.post("/accounts", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created business account: {data}")
        
        assert is_valid_id_format(data["accountId"])
        assert data["customerId"] == payload["customerId"]
        assert data["accountType"] == payload["accountType"]
        assert is_valid_bsb(data["bsb"])
        assert is_valid_account_number(data["accountNumber"])
    
    def test_post_account_missing_fields(self, api_client: APIClient, request_headers: dict):
        """Test POST /accounts with missing required fields returns 400."""
        payload = {
            "customerId": "CUST001"
            # Missing accountType
        }
        
        logging.info(f"Testing POST /accounts with incomplete payload: {payload}")
        response = api_client.post("/accounts", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "accountType" in data["requiredFields"]
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_account_empty_payload(self, api_client: APIClient, request_headers: dict):
        """Test POST /accounts with empty payload returns 400."""
        payload = {}
        
        logging.info(f"Testing POST /accounts with empty payload: {payload}")
        response = api_client.post("/accounts", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "accountType" in data["requiredFields"]