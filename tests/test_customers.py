"""Unit tests for Customers API endpoints."""

import logging
import pytest

from tests.helpers.http import APIClient
from tests.helpers.dates import today_iso, is_valid_date_format
from tests.helpers.ids import is_valid_id_format, is_valid_email, is_valid_phone_number


logger = logging.getLogger(__name__)


class TestCustomersAPI:
    """Test cases for Customers API endpoints."""
    
    def test_get_customer_success(self, api_client: APIClient, request_headers: dict):
        """Test successful GET /customers/{id} with seeded data."""
        customer_id = "CUST001"
        
        logging.info(f"Testing GET /customers/{customer_id}")
        response = api_client.get(f"/customers/{customer_id}", headers=request_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        logging.info(f"Customer data received: {data}")
        
        assert data["customerId"] == customer_id
        assert is_valid_id_format(data["customerId"])
        assert isinstance(data["firstName"], str) and len(data["firstName"]) > 0
        assert isinstance(data["lastName"], str) and len(data["lastName"]) > 0
        assert is_valid_date_format(data["dob"])
        assert is_valid_email(data["email"])
        assert is_valid_phone_number(data["phone"])
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_get_customer_not_found(self, api_client: APIClient, request_headers: dict):
        """Test GET /customers/{id} with unknown ID returns 404."""
        customer_id = "unknown123"
        
        logging.info(f"Testing GET /customers/{customer_id} (not found)")
        response = api_client.get(f"/customers/{customer_id}", headers=request_headers)
        
        assert response.status_code == 404
        
        data = response.json()
        logging.info(f"Error response: {data}")
        
        assert data["error"] == "Customer not found"
        assert data["code"] == "CUSTOMER_NOT_FOUND"
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_customer_success(self, api_client: APIClient, request_headers: dict):
        """Test successful POST /customers with valid payload."""
        payload = {
            "firstName": "Jane",
            "lastName": "Doe",
            "dob": "1992-05-15",
            "email": "jane.doe@test.com",
            "phone": "+61412987654"
        }
        
        logging.info(f"Testing POST /customers with payload: {payload}")
        response = api_client.post("/customers", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created customer: {data}")
        
        assert is_valid_id_format(data["customerId"])
        assert data["firstName"] == payload["firstName"]
        assert data["lastName"] == payload["lastName"]
        assert data["dob"] == payload["dob"]
        assert data["email"] == payload["email"]
        assert data["phone"] == payload["phone"]
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_post_customer_missing_fields(self, api_client: APIClient, request_headers: dict):
        """Test POST /customers with missing required fields returns 400."""
        payload = {
            "firstName": "John"
            # Missing lastName and email
        }
        
        logging.info(f"Testing POST /customers with incomplete payload: {payload}")
        response = api_client.post("/customers", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "firstName" in data["requiredFields"]
        assert "lastName" in data["requiredFields"]
        assert "email" in data["requiredFields"]
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_customer_optional_fields(self, api_client: APIClient, request_headers: dict):
        """Test POST /customers with only required fields works."""
        payload = {
            "firstName": "Bob",
            "lastName": "Wilson",
            "email": "bob.wilson@test.com"
        }
        
        logging.info(f"Testing POST /customers with minimal payload: {payload}")
        response = api_client.post("/customers", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created customer (minimal): {data}")
        
        assert is_valid_id_format(data["customerId"])
        assert data["firstName"] == payload["firstName"]
        assert data["lastName"] == payload["lastName"]
        assert data["email"] == payload["email"]
        assert is_valid_date_format(data["createdAt"].split()[0])
        
        # Optional fields should be None or empty string
        if "dob" in data:
            assert data["dob"] is None or data["dob"] == ""
        if "phone" in data:
            assert data["phone"] is None or data["phone"] == ""