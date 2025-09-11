# WireMock Banking API Stub Service

A lightweight WireMock-based banking API stub service for Windows with comprehensive Python pytest unit tests. This service simulates a realistic banking backend for development, testing, and demo purposes.

## 🏛️ Banking Domain APIs

This stub service implements 5 core banking REST endpoints:

### 1. Customers API
- **GET** `/customers/{id}` - Retrieve customer details
- **POST** `/customers` - Create new customer

### 2. Accounts API  
- **GET** `/accounts/{id}` - Retrieve account details
- **POST** `/accounts` - Create new account

### 3. Loans API
- **GET** `/loans/{id}` - Retrieve loan details
- **POST** `/loans` - Create new loan

### 4. Term Deposits API
- **GET** `/term-deposits/{id}` - Retrieve term deposit details
- **POST** `/term-deposits` - Create new term deposit

### 5. Bookings API
- **GET** `/bookings/{id}` - Retrieve booking details
- **POST** `/bookings` - Link customer to product (loan/term deposit)

## 📋 Prerequisites

- **Java 8+** (for running WireMock standalone JAR)
- **Python 3.8-3.12** (for running tests)
- **Windows 10/11** (batch scripts optimized for Windows)

## 🚀 Quick Start

### 1. Download WireMock

Download the WireMock standalone JAR:
```
https://github.com/wiremock/wiremock/releases/latest
```

Place `wiremock-standalone.jar` in the project root directory.

### 2. Start WireMock Server

```bat
scripts\start_wiremock.bat
```

The server will start on `http://localhost:8080` with:
- ✅ Response templating enabled
- ✅ Dynamic data generation
- ✅ Realistic banking scenarios
- ✅ Admin UI at `http://localhost:8080/__admin`

### 3. Run Tests

```bat
scripts\run_tests.bat
```

This will:
- Create Python virtual environment
- Install dependencies
- Start WireMock (if not running)
- Execute all pytest unit tests

### 4. Stop WireMock Server

```bat
scripts\stop_wiremock.bat
```

## 🧪 Testing

### Test Coverage

Comprehensive pytest unit tests covering:

- ✅ **Happy Path Tests**: Valid requests return correct responses
- ✅ **Error Handling**: Invalid requests return proper error codes
- ✅ **Data Validation**: Response fields match expected formats
- ✅ **Dynamic Data**: No hard-coded assertions, tests adapt to generated data
- ✅ **Date Calculations**: Term deposit maturity, loan payment dates
- ✅ **Australian Banking**: BSB codes, account numbers, phone formats

### Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── helpers/                 # Utility modules
│   ├── env.py              # Environment configuration
│   ├── http.py             # HTTP client with retry logic
│   ├── dates.py            # Date utilities and validation
│   └── ids.py              # ID generation and validation
├── test_customers.py        # Customer API tests
├── test_accounts.py         # Account API tests
├── test_loans.py           # Loan API tests
├── test_term_deposits.py   # Term deposit API tests
└── test_bookings.py        # Booking API tests
```

### Running Specific Tests

```bat
# Activate virtual environment first
venv\Scripts\activate

# Run specific test file
pytest tests\test_customers.py -v

# Run specific test method
pytest tests\test_loans.py::TestLoansAPI::test_post_loan_success -v

# Run with detailed logging
pytest tests\ -v -s --log-cli-level=INFO
```

## 🔧 Configuration

### Environment Variables

Create `.env` file (copied from `.env.example`):

```env
BASE_URL=http://localhost:8080
PORT=8080
```

### WireMock Settings

- **Port**: 8080 (configurable via `PORT` environment variable)
- **Response Templating**: Enabled for dynamic data generation
- **Mappings**: Located in `mappings/` directory
- **Static Files**: Located in `__files/` directory

## 📊 Dynamic Data Features

### Realistic Data Generation

WireMock's response templating generates realistic banking data:

```json
{
  "customerId": "{{randomValue length=12 type='ALPHANUMERIC'}}",
  "firstName": "{{randomValue type='ALPHA' length=8 capitalizeFirst=true}}",
  "accountNumber": "{{randomValue type='NUMBER' min=10000000 max=99999999}}",
  "bsb": "0{{randomValue type='NUMBER' min=10000 max=99999}}",
  "interestRate": "{{randomValue type='DECIMAL' min=3.50 max=15.99}}",
  "nextPaymentDate": "{{now offset='P1M' format='yyyy-MM-dd'}}",
  "maturityDate": "{{now offset='P{{jsonPath request.body '$.termMonths'}}M' format='yyyy-MM-dd'}}"
}
```

### Date Calculations

- **Current Date**: `{{now format='yyyy-MM-dd'}}`
- **Next Payment**: `{{now offset='P1M' format='yyyy-MM-dd'}}` (1 month from now)
- **Term Deposit Maturity**: `{{now offset='P{{jsonPath request.body '$.termMonths'}}M' format='yyyy-MM-dd'}}` (request term + today)

### Request Echo

Fields from POST requests are echoed back:
```json
{
  "principal": "{{jsonPath request.body '$.principal'}}",
  "customerId": "{{jsonPath request.body '$.customerId'}}"
}
```

## 📈 API Examples

### Create Customer

```bash
curl -X POST http://localhost:8080/customers \
  -H "Content-Type: application/json" \
  -H "X-Correlation-Id: test-123" \
  -d '{
    "firstName": "John",
    "lastName": "Smith", 
    "dob": "1985-03-15",
    "email": "john.smith@example.com",
    "phone": "+61412345678"
  }'
```

**Response:**
```json
{
  "customerId": "ABC123DEF456",
  "firstName": "John",
  "lastName": "Smith",
  "dob": "1985-03-15", 
  "email": "john.smith@example.com",
  "phone": "+61412345678",
  "createdAt": "2024-01-15 10:30:45"
}
```

### Create Term Deposit

```bash
curl -X POST http://localhost:8080/term-deposits \
  -H "Content-Type: application/json" \
  -H "X-Correlation-Id: test-456" \
  -d '{
    "customerId": "CUST001",
    "principal": 50000.00,
    "termMonths": 12,
    "interestRate": 4.25
  }'
```

**Response:**
```json
{
  "depositId": "XYZ789ABC123",
  "customerId": "CUST001", 
  "principal": 50000.00,
  "interestRate": 4.25,
  "termMonths": 12,
  "startDate": "2024-01-15",
  "maturityDate": "2025-01-15",
  "createdAt": "2024-01-15 10:32:12"
}
```

### Get Seeded Data

```bash
# Get pre-seeded customer
curl http://localhost:8080/customers/CUST001 \
  -H "X-Correlation-Id: test-789"

# Get pre-seeded account  
curl http://localhost:8080/accounts/ACC001 \
  -H "X-Correlation-Id: test-789"

# Get pre-seeded loan
curl http://localhost:8080/loans/LOAN001 \
  -H "X-Correlation-Id: test-789"
```

## 🚨 Error Scenarios

### Validation Errors (400)

Missing required fields:
```json
{
  "error": "Missing required fields",
  "code": "VALIDATION_ERROR", 
  "requiredFields": ["firstName", "lastName", "email"],
  "timestamp": "2024-01-15 10:35:20"
}
```

### Not Found Errors (404)

```json
{
  "error": "Customer not found",
  "code": "CUSTOMER_NOT_FOUND",
  "timestamp": "2024-01-15 10:36:45"
}
```

### Conflict Errors (409)

Duplicate booking attempt:
```json
{
  "error": "Booking already exists", 
  "code": "DUPLICATE_BOOKING",
  "existingBookingId": "BOOK001",
  "timestamp": "2024-01-15 10:38:10"
}
```

## 📁 Project Structure

```
WireMock API/
├── mappings/                    # WireMock stub mappings
│   ├── customers-get.json
│   ├── customers-post.json
│   ├── accounts-get.json
│   ├── loans-post.json
│   └── ... (all endpoint mappings)
├── __files/                     # Response template files
│   ├── customer-CUST001.json
│   ├── account-ACC001.json
│   └── ... (seeded demo data)
├── scripts/                     # Windows batch scripts
│   ├── start_wiremock.bat
│   ├── stop_wiremock.bat
│   └── run_tests.bat
├── tests/                       # Python unit tests
│   ├── helpers/                 # Test utilities
│   ├── conftest.py              # Pytest configuration
│   ├── test_customers.py
│   └── ... (test modules)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🔄 Extending with BDD Frameworks

This WireMock stub service provides a solid foundation for extending with BDD frameworks:

### Cucumber/SpecFlow Integration
- Use the existing WireMock stubs as the backend
- Write Gherkin scenarios that call the same endpoints
- Reuse the validation helpers from `tests/helpers/`

### Behave (Python BDD)
- Import `tests.helpers` modules in step definitions
- Use `APIClient` class for HTTP requests
- Leverage existing date and ID validation functions

### Example BDD Extension
```gherkin
Scenario: Customer creates a term deposit
  Given customer "John Smith" exists with ID "CUST001" 
  When they create a term deposit with:
    | principal   | 25000.00 |
    | termMonths  | 12       |
    | interestRate| 3.75     |
  Then the term deposit should be created successfully
  And the maturity date should be 12 months from today
  And the interest rate should be 3.75%
```

## 🤝 Contributing

1. Add new endpoints by creating mapping files in `mappings/`
2. Add corresponding test files in `tests/`  
3. Update this README with new endpoint documentation
4. Ensure all tests pass with `scripts\run_tests.bat`

## 📝 License

This project is provided as-is for development and testing purposes.