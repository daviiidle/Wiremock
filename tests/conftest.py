"""Pytest configuration and fixtures."""

import logging
import subprocess
import time
import pytest
from typing import Generator

from tests.helpers.env import load_env_config, get_base_url, get_port
from tests.helpers.http import APIClient
from tests.helpers.ids import new_correlation_id


# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(scope="session")
def load_env() -> None:
    """Load environment configuration at test session start."""
    load_env_config()


@pytest.fixture(scope="session")
def wiremock_server(load_env) -> Generator[None, None, None]:
    """Start WireMock server for test session if not already running."""
    client = APIClient()
    
    # Check if WireMock is already running
    if client.health_check(retries=1, delay=0):
        logging.info("WireMock server is already running")
        yield
        return
    
    # Start WireMock server
    logging.info("Starting WireMock server for tests...")
    port = get_port()
    
    try:
        process = subprocess.Popen([
            'java', '-jar', 'wiremock-standalone.jar',
            '--port', str(port),
            '--root-dir', '.',
            '--global-response-templating',
            '--verbose'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        time.sleep(3)
        
        if not client.health_check():
            raise RuntimeError("Failed to start WireMock server")
        
        logging.info(f"WireMock server started successfully on port {port}")
        yield
        
        # Cleanup
        logging.info("Stopping WireMock server...")
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        logging.error(f"Failed to start WireMock server: {e}")
        pytest.skip("WireMock server not available")


@pytest.fixture
def api_client(wiremock_server) -> APIClient:
    """Create API client for testing."""
    return APIClient()


@pytest.fixture
def correlation_id() -> str:
    """Generate unique correlation ID for each test."""
    return new_correlation_id()


@pytest.fixture
def request_headers(correlation_id: str) -> dict:
    """Generate request headers with correlation ID."""
    return {
        'X-Correlation-Id': correlation_id,
        'Content-Type': 'application/json'
    }