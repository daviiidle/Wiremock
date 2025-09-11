"""HTTP client helper for API testing."""

import logging
import time
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .env import get_base_url


class APIClient:
    """HTTP client for API testing with retry logic and logging."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """Initialize API client with base URL and timeout."""
        self.base_url = base_url or get_base_url()
        self.timeout = timeout
        self.session = self._create_session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _log_request(self, method: str, url: str, headers: Dict[str, Any], 
                    payload: Optional[Dict[str, Any]] = None) -> None:
        """Log HTTP request details."""
        self.logger.info(f"Request: {method} {url}")
        self.logger.info(f"Request headers: {headers}")
        if payload:
            self.logger.info(f"Request payload: {payload}")
    
    def _log_response(self, response: requests.Response) -> None:
        """Log HTTP response details."""
        self.logger.info(f"Response code: {response.status_code}")
        self.logger.info(f"Response headers: {dict(response.headers)}")
        try:
            self.logger.info(f"Response body: {response.json()}")
        except ValueError:
            self.logger.info(f"Response body (text): {response.text}")
    
    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        
        self._log_request("GET", url, headers)
        response = self.session.get(url, headers=headers, timeout=self.timeout)
        self._log_response(response)
        
        return response
    
    def post(self, endpoint: str, payload: Dict[str, Any], 
             headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make POST request."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/json')
        
        self._log_request("POST", url, headers, payload)
        response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        self._log_response(response)
        
        return response
    
    def health_check(self, retries: int = 5, delay: float = 2.0) -> bool:
        """Check if WireMock server is healthy."""
        for attempt in range(retries):
            try:
                response = self.get("/__admin/mappings")
                if response.status_code == 200:
                    self.logger.info("WireMock health check passed")
                    return True
            except requests.RequestException as e:
                self.logger.warning(f"Health check attempt {attempt + 1} failed: {e}")
            
            if attempt < retries - 1:
                time.sleep(delay)
        
        self.logger.error("WireMock health check failed after all retries")
        return False