"""Unit tests for Bookings API endpoints."""

import logging
import pytest

from tests.helpers.http import APIClient
from tests.helpers.dates import is_valid_date_format
from tests.helpers.ids import is_valid_id_format


logger = logging.getLogger(__name__)


class TestBookingsAPI:
    """Test cases for Bookings API endpoints."""
    
    def test_get_booking_success(self, api_client: APIClient, request_headers: dict):
        """Test successful GET /bookings/{id} with seeded data."""
        booking_id = "BOOK001"
        
        logging.info(f"Testing GET /bookings/{booking_id}")
        response = api_client.get(f"/bookings/{booking_id}", headers=request_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        logging.info(f"Booking data received: {data}")
        
        assert data["bookingId"] == booking_id
        assert is_valid_id_format(data["bookingId"])
        assert is_valid_id_format(data["customerId"])
        assert isinstance(data["productType"], str) and len(data["productType"]) > 0
        assert data["productType"] in ["loan", "termDeposit"]
        assert is_valid_id_format(data["productId"])
        assert isinstance(data["status"], str) and len(data["status"]) > 0
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_get_booking_not_found(self, api_client: APIClient, request_headers: dict):
        """Test GET /bookings/{id} with unknown ID returns 404."""
        booking_id = "unknown123"
        
        logging.info(f"Testing GET /bookings/{booking_id} (not found)")
        response = api_client.get(f"/bookings/{booking_id}", headers=request_headers)
        
        assert response.status_code == 404
        
        data = response.json()
        logging.info(f"Error response: {data}")
        
        assert data["error"] == "Booking not found"
        assert data["code"] == "BOOKING_NOT_FOUND"
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_booking_loan_success(self, api_client: APIClient, request_headers: dict):
        """Test successful POST /bookings with loan product."""
        payload = {
            "customerId": "CUST002",
            "productType": "loan",
            "productId": "LOAN123"
        }
        
        logging.info(f"Testing POST /bookings with loan: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created booking: {data}")
        
        assert is_valid_id_format(data["bookingId"])
        assert data["customerId"] == payload["customerId"]
        assert data["productType"] == payload["productType"]
        assert data["productId"] == payload["productId"]
        assert data["status"] == "active"
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_post_booking_term_deposit_success(self, api_client: APIClient, request_headers: dict):
        """Test successful POST /bookings with term deposit product."""
        payload = {
            "customerId": "CUST003",
            "productType": "termDeposit",
            "productId": "TD456"
        }
        
        logging.info(f"Testing POST /bookings with term deposit: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 201
        
        data = response.json()
        logging.info(f"Created booking: {data}")
        
        assert is_valid_id_format(data["bookingId"])
        assert data["customerId"] == payload["customerId"]
        assert data["productType"] == payload["productType"]
        assert data["productId"] == payload["productId"]
        assert data["status"] == "active"
        assert is_valid_date_format(data["createdAt"].split()[0])
    
    def test_post_booking_duplicate_returns_409(self, api_client: APIClient, request_headers: dict):
        """Test POST /bookings with duplicate booking returns 409."""
        payload = {
            "customerId": "CUST001",
            "productType": "loan",
            "productId": "LOAN001"
        }
        
        logging.info(f"Testing POST /bookings with duplicate: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 409
        
        data = response.json()
        logging.info(f"Conflict response: {data}")
        
        assert data["error"] == "Booking already exists"
        assert data["code"] == "DUPLICATE_BOOKING"
        assert is_valid_id_format(data["existingBookingId"])
        assert is_valid_date_format(data["timestamp"].split()[0])
    
    def test_post_booking_missing_customer_id(self, api_client: APIClient, request_headers: dict):
        """Test POST /bookings with missing customerId returns 400."""
        payload = {
            "productType": "loan",
            "productId": "LOAN789"
            # Missing customerId
        }
        
        logging.info(f"Testing POST /bookings missing customerId: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "productType" in data["requiredFields"]
        assert "productId" in data["requiredFields"]
    
    def test_post_booking_missing_product_type(self, api_client: APIClient, request_headers: dict):
        """Test POST /bookings with missing productType returns 400."""
        payload = {
            "customerId": "CUST001",
            "productId": "LOAN789"
            # Missing productType
        }
        
        logging.info(f"Testing POST /bookings missing productType: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "productType" in data["requiredFields"]
        assert "productId" in data["requiredFields"]
    
    def test_post_booking_missing_product_id(self, api_client: APIClient, request_headers: dict):
        """Test POST /bookings with missing productId returns 400."""
        payload = {
            "customerId": "CUST001",
            "productType": "termDeposit"
            # Missing productId
        }
        
        logging.info(f"Testing POST /bookings missing productId: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "productType" in data["requiredFields"]
        assert "productId" in data["requiredFields"]
    
    def test_post_booking_empty_payload(self, api_client: APIClient, request_headers: dict):
        """Test POST /bookings with empty payload returns 400."""
        payload = {}
        
        logging.info(f"Testing POST /bookings with empty payload: {payload}")
        response = api_client.post("/bookings", payload, headers=request_headers)
        
        assert response.status_code == 400
        
        data = response.json()
        logging.info(f"Validation error response: {data}")
        
        assert data["error"] == "Missing required fields"
        assert data["code"] == "VALIDATION_ERROR"
        assert "customerId" in data["requiredFields"]
        assert "productType" in data["requiredFields"]
        assert "productId" in data["requiredFields"]