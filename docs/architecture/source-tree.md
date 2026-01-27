# Source Tree & Project Structure

## Root Directory
*   `app.py`: Main entry point for Taipy application (migrated from Streamlit)
*   `settings.toml`: Main Dynaconf configuration file
*   `.secrets.toml`: Local secrets (gitignored)
*   `Dockerfile`: Container definition for HF Spaces
*   `requirements.txt`: Python dependencies

## Source Code (`src/` or Root - Decision: Root for simplicity unless complex)
*   `auth.py`: Authentication strategies (EntraID, Supabase, Local)
*   `database.py`: Database Access Layer (Facade)
*   `config.py`: Dynaconf setup
*   `pages/`: Directory for Taipy page definitions
    *   `dashboard.py`: General Farm View
    *   `wizard.py`: "Add Farm" Wizard Logic
    *   `admin.py`: Admin tools (Delete, Schema View)
    *   `...`: Other tabs

## Data & Resources
*   `DATA/`: Local SQLite database storage
*   `RESOURCES/`: Static assets, images, schemas
*   `docs/`: Documentation (PRD, Architecture, Stories)

## Tests
*   `tests/`: Unit and Integration tests
