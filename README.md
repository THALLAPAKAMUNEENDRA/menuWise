# MenuWise Python Backend Engineering Challenge

## Overview

Thank you for your interest in joining MenuWise.

This challenge is designed to evaluate how you think about backend engineering, data handling, APIs, architecture, and code quality in a real-world SaaS environment.

Please spend no more than **4 hours** on this challenge.


We are evaluating:
- Engineering judgment
- Backend architecture
- Data modelling
- API design
- Validation and error handling
- Code quality
- Performance awareness
- Communication

---

# Scenario

MenuWise aggregates ingredient and supplier pricing data from multiple sources.

Supplier datasets are often messy:
- inconsistent product naming
- duplicate SKUs
- missing pricing
- invalid pack sizes
- incorrect currencies
- inconsistent units

Your task is to build a small backend service that imports, validates, stores, and exposes supplier product pricing data.

---

# Technical Requirements

Use:
- Python 3.11+
- Django
- Django REST Framework

You may additionally use:
- Celery
- Pandas
- Requests
- BeautifulSoup
- Playwright
- pytest
- factory_boy
- Docker

Avoid excessive frameworks or unnecessary complexity.

---

# Core Tasks

## 1. Create the Data Model

Create models for:

### Supplier
Fields:
- name
- country_code
- active
- created_at

### Product
Fields:
- supplier
- supplier_sku
- product_name
- pack_size
- unit
- currency
- price
- imported_at

### Validation Rules
- supplier_sku must be unique per supplier
- price cannot be negative
- pack_size must be greater than zero
- unit must be normalized to:
  - g
  - kg
  - ml
  - l
  - each

If currency is missing:
- default to INR when supplier country_code = IN
- otherwise default to USD

---

## 2. CSV Import Endpoint

Create an endpoint to import CSV data.

Requirements:
- validate rows
- skip invalid rows safely
- return validation errors
- avoid duplicate inserts
- support importing at least 5,000 rows efficiently

Document your decisions.

---

## 3. Supplier API

Build REST endpoints for:

### GET /api/products
Features:
- pagination
- filtering by supplier
- filtering by currency
- filtering by active suppliers
- search by product_name

### GET /api/products/{id}

### GET /api/suppliers

Use efficient query handling.

---

## 4. Django Admin

Configure Django Admin for:
- Supplier
- Product

Requirements:
- searchable product list
- filtering
- useful list displays
- import visibility

---

## 5. Basic Scraping Task

Create a small importer that extracts supplier pricing data from:
- either a provided HTML table
- or a public webpage

Requirements:
- parse rows
- normalize units
- validate data
- store products

You may use:
- Requests + BeautifulSoup
- Playwright
- Scrapy

---

## 6. Tests

Add tests for:
- model validation
- CSV import
- API filtering/search
- duplicate handling

---

## 7. Documentation

Include:
- README.md
- DECISIONS.md

DECISIONS.md should explain:
- import strategy
- validation approach
- query optimization decisions
- scalability considerations
- what you would improve with more time

---

Provide:
- Git repository link
- README.md
- DECISIONS.md

---

# How to Run

### 1. Setup Environment (Local)
Ensure you have Python 3.11+ installed.
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> [!TIP]
> For a detailed terminal walkthrough with exact inputs and expected outputs, see **[RUN_PROCEDURES.md](file:///d:/MenuWise-Gavin/python-backend-challenge-main/RUN_PROCEDURES.md)**.

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Run Tests
```bash
pytest
```

### 4. Run the Server
```bash
python manage.py runserver
```

---

### Running with Docker

This project is fully Dockerized for ease of use. You can spin up the entire environment (App + Database) using Docker Compose.

**1. Build and Start:**
```bash
docker-compose up --build
```

**2. Access:**
- The app will be available at: `http://127.0.0.1:8000/`
- API Products: `http://127.0.0.1:8000/api/products/`

**3. Run Migrations & Create Superuser (Inside Container):**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 5. Access the Application
- **Admin**: Create a superuser (`python manage.py createsuperuser`) and visit `http://127.0.0.1:8000/admin/`.
- **API - Products**: `GET http://127.0.0.1:8000/api/products/`
- **API - Suppliers**: `GET http://127.0.0.1:8000/api/suppliers/`
- **CSV Import**: `POST http://127.0.0.1:8000/api/products/import/`
  - Body: form-data, key `file` (type File).

### 6. HTML Scraper
To run the scraper manually, you can open a Django shell (`python manage.py shell`) and run:
```python
from app.services.scraper import scrape_supplier_html
import os
from django.conf import settings
file_path = os.path.join(settings.BASE_DIR, 'samples', 'supplier_price_table.html')
print(scrape_supplier_html(file_path))
```

---

# Evaluation Criteria

| Area | Weight |
|---|---:|
| Django/API implementation | 25% |
| Import/ETL correctness | 20% |
| Query performance | 15% |
| Tests | 20% |
| Code quality | 10% |
| Documentation & communication | 10% |