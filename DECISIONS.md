# Engineering Decisions

## Import Strategy

- Used `pandas` to read the CSV file. It handles various CSV formats and missing data gracefully and is highly optimized.
- Iterated over the dataframe to validate data using standard Python validation. Errors are collected and returned without failing the entire batch, ensuring partial imports are successful.
- Missing suppliers are created dynamically based on `supplier_name` and `country_code`.
- For efficiency, used `bulk_create(..., update_conflicts=True)` (upsert) to handle inserts and updates in a single query. This safely handles duplicate `supplier_sku`s by updating existing records, satisfying the requirement to avoid duplicate inserts and supporting large batch imports gracefully.

---

## Query Optimization

- Used `select_related('supplier')` on the `ProductViewSet` queryset to avoid N+1 query problems when fetching products along with their supplier details.
- Used Django REST Framework's built-in pagination `PageNumberPagination` to ensure memory efficiency when responding with large datasets.
- Utilized `django-filter` to provide optimized database-level filtering (`supplier`, `currency`, `supplier__active`).
- Used DRF's `SearchFilter` to allow efficient database-level `LIKE` queries for `product_name`.

---

## Scraping Strategy

- Used `BeautifulSoup` for the structured extraction of product data from the provided HTML table.
- **Normalisation**: Units are lowercased and validated against the system's allowed units to ensure data consistency.
- **Deduplication**: Used a similar `bulk_create` with conflict resolution approach as the CSV import to ensure that running the scraper multiple times does not result in duplicate records.
- **Future Considerations**: For production-scale crawling (as mentioned in the JD), I would implement:
    - **Anti-bot handling**: Use Playwright with stealth plugins or residential proxies.
    - **Rate Limiting**: Implement delays and retries using a task queue like Celery.
    - **Pagination**: Implement recursive crawling logic to navigate through multi-page supplier lists.

---

## Scalability Considerations

- The current `bulk_create` approach can easily handle 5,000+ rows within seconds. However, for files significantly larger (e.g., 100k+ rows), memory might become a bottleneck.
- **Larger Imports**: To support massive files, the CSV processing could be chunked (e.g., processing 10,000 rows at a time using `pandas.read_csv(chunksize=...)`).
- **Async/Background Jobs**: For production, the import process should be offloaded to a background task queue like Celery to prevent blocking the HTTP request. The API would return an import job ID, and the client could poll for the status.
- **Retry Handling**: By moving to Celery, we get built-in retry mechanisms for transient database or network failures during the import process.

---

## Deployment & CI/CD (Bonus Implementations)

- **Dockerization**: The application has been fully Dockerized using `python:3.11-slim`. A `Dockerfile` and `docker-compose.yml` are provided so the application can be run seamlessly in any environment without managing local Python dependencies.
- **CI/CD Pipeline**: A GitHub Actions workflow (`.github/workflows/django.yml`) has been implemented to automatically install dependencies, run the `pytest` suite, and **verify the Docker build process** on every push and pull request to the `main` branch. This ensures code quality and artifact readiness for deployment.

## Improvements With More Time

- **Additional validation**: Add Pydantic or DRF serializers for the CSV row validation instead of manual checks. This would provide cleaner error messages and better maintainability.
- **Monitoring/logging**: Integrate standard logging, Sentry for error tracking, and Prometheus/Datadog for tracking import times, error rates, and API performance.
- **Testing improvements**: Add integration tests with the actual database instead of SQLite (e.g., PostgreSQL using `pytest-postgresql` or Docker) to ensure the `bulk_create` with conflict resolution behaves exactly as it will in production. Add more edge cases to the scraper tests.