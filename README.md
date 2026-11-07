# Blog app: FastAPI, SQLAlchemy, PostgreSQL, and Streamlit

This project includes the FastAPI blog API, its SQLAlchemy `Blog` model, a
PostgreSQL database, and a Streamlit interface. The API and UI communicate over
HTTP. `render.yaml` deploys all three resources together.

## Run locally on Windows

Create a `.env` file in the project root (never commit it):

```env
DB_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/blog
SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-strong-password
```

The database URL above assumes you already have PostgreSQL running locally and
have created the `blog` database. For a hosted database, use its connection URL.

Open two PowerShell terminals:

**Terminal 1 — install and run the API**

```powershell
cd C:\Users\DELL\Desktop\FastApi_Project
.\venv\Scripts\python.exe -m pip install -r requirements-api.txt
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

**Terminal 2 — install and run the UI**

```powershell
cd C:\Users\DELL\Desktop\FastApi_Project
.\venv\Scripts\python.exe -m pip install -r requirements-ui.txt
$env:API_BASE_URL = "http://127.0.0.1:8000"
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open `http://localhost:8501`. Sign in with the `ADMIN_USERNAME` and
`ADMIN_PASSWORD` values from `.env`. The UI supports listing, searching,
pagination, creating, editing, and deleting blog posts.

## Deploy the complete app to Render

The Blueprint creates a PostgreSQL database, a FastAPI API service, and a
Streamlit UI service. The database and paid web-service plans may incur charges;
review the current Render pricing before applying the Blueprint.

1. Push the project to a GitHub repository. Do not commit `.env`, your virtual
   environment, or secrets.
2. In Render, select **New → Blueprint** and connect this repository.
3. Review the resources from `render.yaml` and the associated prices, then
   apply the Blueprint.
4. In the Render dashboard, open the **blog-api** service's environment
   settings and set `ADMIN_USERNAME` and `ADMIN_PASSWORD` to your own strong
   credentials. These are intentionally not stored in Git.
5. Wait for the database and both services to finish deploying. The UI gets
   the API's private host and port from the Blueprint automatically.
6. Open the public URL shown for **blog-streamlit-ui**, sign in with the admin
   credentials, and test creating and editing a post. The API is also available
   at its own Render URL; `/docs` shows its OpenAPI documentation.

The API uses the existing SQLAlchemy `Blog` model and creates its table when
the API starts. Render supplies the database connection and a generated JWT
secret. For production schema changes beyond this initial model, use a database
migration tool rather than relying on `create_all`.

## Configuration and security

- `DB_URL`: PostgreSQL connection URL. The app accepts Render's `postgres://`
  and `postgresql://` URLs and configures the `psycopg` SQLAlchemy driver.
- `SECRET_KEY`: signing secret for short-lived JWT access tokens.
- `ADMIN_USERNAME` and `ADMIN_PASSWORD`: required API login credentials.
- `API_BASE_URL`: API host and port used by Streamlit; configured from the API
  service automatically in the Render Blueprint.

The API's `/login` endpoint uses OAuth2 form fields (`username` and `password`).
Do not expose the API without setting unique admin credentials and keeping the
JWT secret private. Use HTTPS for public access.
