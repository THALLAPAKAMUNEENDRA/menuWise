# Project Run Procedures (Inputs & Outputs)

This document outlines the exact inputs you need to provide and the expected outputs you will see when running and testing the MenuWise Python Backend Challenge.

---

## Procedure 1: Starting the Server

**INPUT (Terminal):**
```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

**EXPECTED OUTPUT (Terminal):**
```text
System check identified no issues (0 silenced).
May 15, 2026 - 16:10:00
Django version 5.2.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## Procedure 1.1: Starting the Server (Docker)

**INPUT (Terminal):**
```bash
docker-compose up --build
```

**EXPECTED OUTPUT (Terminal):**
```text
web-1  | Operations to perform:
web-1  |   Apply all migrations: admin, app, auth, contenttypes, sessions
web-1  | Running migrations:
web-1  |   No migrations to apply.
web-1  | Starting development server at http://0.0.0.0:8000/
```

---

## Procedure 2: HTML Scraper Test

**INPUT (Terminal - *Open a separate terminal*):**
```powershell
.\.venv\Scripts\Activate.ps1
python manage.py shell
```

Inside the Python shell, type:
```python
from app.services.scraper import scrape_supplier_html
import os
from django.conf import settings
file_path = os.path.join(settings.BASE_DIR, 'samples', 'supplier_price_table.html')
print(scrape_supplier_html(file_path))
```

**EXPECTED OUTPUT (Terminal):**
```python
{'success': True, 'imported_count': 3, 'errors': []}
```
*(This confirms 3 valid products were successfully scraped and inserted).*

---

## Procedure 3: CSV Import API Test

**INPUT (Terminal):**
Ensure the server is running, then in a separate terminal:
```powershell
curl.exe -X POST http://127.0.0.1:8000/api/products/import/ -F "file=@samples/sample_products.csv"
```

**EXPECTED OUTPUT (Terminal JSON Response):**
```json
{
  "success": true,
  "imported_count": 4,
  "errors": [
    {
      "row": 6,
      "error": "Price cannot be negative"
    }
  ],
  "total_rows": 5
}
```
*(This confirms it successfully imported the 4 valid rows and correctly identified the 1 broken row with the negative price).*

---

## Procedure 4: Fetch All Products API

**INPUT (Browser or Terminal):**
Visit `http://127.0.0.1:8000/api/products/` or run:
```powershell
curl.exe http://127.0.0.1:8000/api/products/
```

**EXPECTED OUTPUT (JSON):**
A paginated JSON response listing all products scraped from the HTML and imported from the CSV:
```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "supplier": 1,
      "supplier_details": { "name": "Fresh Foods", "country_code": "US" },
      "supplier_sku": "MLK-001",
      "product_name": "Whole Milk Duplicate",
      "price": "4.50"
    },
    ... (other products) ...
  ]
}
```

---

## Procedure 5: Test API Search Filter

**INPUT (Browser):**
Visit `http://127.0.0.1:8000/api/products/?search=Milk`

**EXPECTED OUTPUT (JSON):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
       "product_name": "Whole Milk Duplicate",
       ...
    }
  ]
}
```

---

## Procedure 6: Django Admin Interface

**INPUT (Browser):**
1. Visit `http://127.0.0.1:8000/admin/`
2. Username: `admin`
3. Password: `admin`

**EXPECTED OUTPUT (Browser Interface):**
You will be logged into the administration dashboard. You will see a clean UI listing **Products** and **Suppliers**. Clicking on "Products" will display a formatted table of all 7 items we imported, with sidebar filters allowing you to filter by `Supplier`, `Currency`, and `Unit`.
