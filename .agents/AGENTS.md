# RetainAI Project Rules

## Project Overview

This project is an AI-powered Customer Lifetime Value (CLV) and Churn Prediction System.

Tech Stack:

- Frontend: Streamlit
- Backend: FastAPI
- Database: SQLite
- Machine Learning: Scikit-learn
- Visualization: Plotly

Always preserve this architecture unless explicitly instructed.

---

## Project Structure

Never modify the folder structure unless explicitly instructed.

The project structure is considered frozen.

Whenever files or folders are created, moved, renamed or deleted:

- Automatically update `project_structure.txt`.
- Preserve the existing folder hierarchy.

---

## Existing Components

The following should never be modified unless explicitly instructed:

- notebooks/
- models/
- processed datasets
- UI theme and visual design

Never rewrite existing working functionality.

---

## Code Quality

Always write modular code.

Keep files focused on a single responsibility.

Avoid duplicated logic.

Prefer reusable functions over copy-paste.

Use clear variable and function names.

Use type hints where appropriate.

---

## Backend

Follow FastAPI best practices.

Separate:

- API
- Services
- Database
- ML
- Schemas

Never place business logic directly inside API routes.

---

## Database

SQLite is the only database used.

Never hardcode database paths.

Use the project database located at:

database/retail.db

---

## Frontend

Preserve the existing dashboard design.

Do not redesign the UI unless explicitly instructed.

Reuse existing utility functions whenever possible.

---

## Documentation

After every completed milestone:

- Update project_structure.txt
- Update documentation if requested
- Summarize implementation

---

## Constraints

Never:

- change project architecture
- introduce unnecessary dependencies
- create unnecessary files
- rename folders
- delete existing functionality

Only implement the requested milestone.

If a requested change affects another module, preserve backward compatibility whenever possible.
