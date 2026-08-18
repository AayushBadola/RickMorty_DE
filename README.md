# RickMorty_DE

<p>
  <img src="https://img.shields.io/badge/Author-Aayush%20Badola-blueviolet?style=for-the-badge" alt="Author" />
  <img src="https://img.shields.io/badge/Python-3.11.9-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11.9" />
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

<p>
  <img src="https://img.shields.io/badge/GraphQL-E10098?style=flat-square&logo=graphql&logoColor=white" alt="GraphQL" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/Psycopg-3-336791?style=flat-square" alt="Psycopg 3" />
  <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License: MIT" />
</p>

A modular, Docker-supported data engineering project built around the Rick & Morty GraphQL API.

The project extracts the current character dataset, cleans and validates it with Pandas, synchronizes it with PostgreSQL using record hashes, maintains SQLite-derived databases for backup and fuzzy name search, and provides a command-line application for character lookup and attribute-based filtering.

## Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [How the Project Works](#how-the-project-works)
- [Application Usage](#application-usage)
- [Direct Pipeline Usage](#direct-pipeline-usage)
- [Docker Usage](#docker-usage)
- [Project Structure](#project-structure)
- [Module Responsibilities](#module-responsibilities)
- [Configuration and Security](#configuration-and-security)
- [Technology Stack](#technology-stack)
- [What This Project Demonstrates](#what-this-project-demonstrates)
- [What It Does Not Currently Include](#what-it-does-not-currently-include)
- [Data Source](#data-source)
- [License](#license)

## Requirements

Install the following before running the project:

| Tool | Version |
|---|---|
| Python | 3.13 or newer |
| Docker Desktop | latest |
| Git | latest |

Docker Desktop provides the isolated PostgreSQL environment used by the project.

## Quick Start

### 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd RickMorty_DE
```

### 2. Create and activate a Python virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create the environment file

Create your local `.env` from the example:

```powershell
copy .env.example .env
```

The supplied values are intended for the PostgreSQL container created by Docker Compose.

### 5. Start PostgreSQL

```powershell
docker compose up -d postgres
```

The PostgreSQL container is exposed to the host on port `5433`, while it continues to use port `5432` internally inside Docker.

### 6. Run the application

```powershell
python main.py
```

On the first run, `main.py` automatically initializes the database when the required PostgreSQL table and local derived databases do not yet exist. After initialization, later runs reuse the existing data.

## How the Project Works

```text
Rick & Morty GraphQL API
          |
          v
      extract.py
          |
          v
   Character objects
          |
          v
       clean.py
          |
          v
Pandas cleaning + validation
          |
          v
     SHA-256 hashes
          |
          v
        load.py
          |
          v
      PostgreSQL
       /       \
      /         \
     v           v
backup_data.db  char_names.db
   snapshot       search index
                     |
                     v
                  search.py
                     |
                     v
                 main.py
                     |
                     v
              query.py / filters
```

### 1. Extraction

`src/extract.py` communicates with the Rick & Morty GraphQL API.

It handles pagination and retrieves the current character dataset. The project requests only the fields it needs:

- ID
- Name
- Status
- Species
- Type
- Gender
- Origin name
- Location name

The API response is converted into structured `Character` objects before being passed to the cleaning stage.

### 2. Cleaning, Validation, and Hashing

`src/clean.py` converts the extracted records into a Pandas DataFrame.

It performs:

- missing-value handling
- text normalization
- required-column validation
- duplicate ID detection
- deterministic SHA-256 record hashing

The hash is generated from the relevant fields of each character and is used to determine whether a record changed since the previous pipeline run.

### 3. PostgreSQL Synchronization

`src/load.py` synchronizes the cleaned DataFrame with PostgreSQL.

The synchronization rules are:

```text
New ID + no existing row
    -> INSERT

Existing ID + same record hash
    -> NO CHANGE

Existing ID + different record hash
    -> UPDATE

Database ID missing from the current API snapshot
    -> DELETE
```

This means repeated pipeline runs do not unnecessarily rewrite unchanged rows.

### 4. SQLite Search Index

`data/char_names.db` is a lightweight derived search index.

It contains only the fields needed for local name resolution:

```text
id
name
origin_name
```

The index supports:

- exact character-name matching
- fuzzy matching with `difflib`
- duplicate-name disambiguation using character origin

For example, if multiple characters are named `Rick Sanchez`, the application can show their origins and let the user choose the correct record.

SQLite is not the source of truth. The PostgreSQL dataset is authoritative, and the search index is refreshed from PostgreSQL after a successful database synchronization.

### 5. Backup Snapshot

`data/backup_data.db` is a SQLite snapshot of the cleaned PostgreSQL character dataset.

It is maintained as a local recovery/reference copy and can be regenerated through the database management functions.

### 6. PostgreSQL Attribute Filtering

`src/query.py` provides dynamic filtering against PostgreSQL.

The filter function accepts optional values such as:

```python
find_characters(
    status=None,
    species=None,
    gender=None,
    origin=None,
    location=None
)
```

Only supplied filters are included in the SQL query, and the conditions are combined with `AND`.

For example:

```python
find_characters(
    status="Alive",
    species="Human"
)
```

produces the equivalent of:

```sql
SELECT *
FROM characters
WHERE status = 'Alive'
  AND species = 'Human';
```

### 7. Database Management

`src/database_manager.py` provides higher-level database lifecycle operations.

**Automatic first-run initialization**
When `main.py` starts on a fresh setup, it checks whether the database has been initialized. If not, it runs a full rebuild automatically.

**Update Database**
Checks the current API snapshot against PostgreSQL and applies only required changes. If there are no changes, the derived SQLite databases are not unnecessarily rewritten.

**Rebuild Database**
A rebuild is a destructive full regeneration. It removes the existing PostgreSQL character table and local SQLite snapshots, then runs a fresh extraction and rebuilds:

```text
PostgreSQL
backup_data.db
char_names.db
```

This provides a clean recovery/reset path when required.

## Application Usage

After starting PostgreSQL, normal usage is simply:

```powershell
python main.py
```

The application provides options for:

```text
1. Search Character
2. Find Characters
3. Developer Options
4. Exit
```

### Search by Name

You can enter an exact name or a misspelled name.

Example:

```text
Enter Character Name: Rik Sanches

Did you mean Rick Sanchez?
```

If multiple characters have the same name, the application displays their origins and asks you to choose one.

### Find Characters by Attributes

You can search without knowing the character's name by supplying any combination of:

- Status
- Species
- Gender
- Origin
- Location

Leave a field blank when you do not want that field included in the filter.

### Developer Options

Developer Options provide manual database lifecycle controls:

```text
1. Rebuild Database
2. Update Database
3. Back
```

Normal users do not need to call `database_manager.py` directly.

## Direct Pipeline Usage

For development or testing, the ETL pipeline can also be run directly:

```powershell
python pipeline.py
```

The pipeline performs:

```text
Extract
  -> Clean
  -> Validate / Hash
  -> Synchronize PostgreSQL
```

The higher-level database manager is responsible for refreshing the derived SQLite databases after successful synchronization.

## Docker Usage

The normal application workflow uses Docker for PostgreSQL and Python locally:

```powershell
docker compose up -d postgres
python main.py
```

The project also supports a fully containerized application run:

```powershell
docker compose run --rm app python main.py
```

Other useful commands:

```powershell
# Stop the PostgreSQL container
docker compose down

# Stop containers and remove the PostgreSQL volume
docker compose down -v
```

`docker compose down -v` is destructive for the Docker PostgreSQL data and should only be used when you intentionally want a fresh database environment.

## Project Structure

```text
RickMorty_DE/
|
+-- data/
|   +-- char_names.db
|   +-- backup_data.db
|
+-- src/
|   +-- extract.py
|   +-- clean.py
|   +-- load.py
|   +-- search.py
|   +-- query.py
|   +-- database_manager.py
|
+-- utils/
|   +-- display.py
|
+-- pipeline.py
+-- main.py
|
+-- .env.example
+-- .gitignore
+-- .dockerignore
+-- Dockerfile
+-- docker-compose.yml
+-- requirements.txt
+-- README.md
```

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `src/extract.py` | GraphQL extraction and `Character` object creation |
| `src/clean.py` | Pandas cleaning, normalization, validation, and hashing |
| `src/load.py` | PostgreSQL table creation and incremental synchronization |
| `src/search.py` | Read-only SQLite exact/fuzzy search |
| `src/query.py` | PostgreSQL record lookup and dynamic filtering |
| `src/database_manager.py` | Rebuilds, updates, backups, and search-index lifecycle |
| `pipeline.py` | Extract -> clean -> PostgreSQL orchestration |
| `utils/display.py` | User input, menus, validation, and presentation |
| `main.py` | Application orchestration |

## Configuration and Security

The repository contains `.env.example` but should never contain a real `.env` file.

Create your local `.env` with:

```env
RICK_MORTY_GRAPHQL_URL=https://rickandmortyapi.com/graphql

POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=rickmorty
POSTGRES_USER=rickmorty
POSTGRES_PASSWORD=rickmorty
```

The PostgreSQL credentials above are for the isolated local Docker database. They are not credentials for a remote production database.

Do not commit real secrets, API keys, or production credentials.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and pipeline logic |
| GraphQL | Source data extraction |
| Requests | HTTP communication |
| Pandas | Data cleaning and transformation |
| PostgreSQL | Authoritative relational dataset |
| SQLite | Search index and backup snapshot |
| Psycopg 3 | Python <-> PostgreSQL connectivity |
| `difflib` | Fuzzy character-name matching |
| Docker | Reproducible service environment |
| Docker Compose | PostgreSQL/app orchestration |
| Git/GitHub | Version control |

## What This Project Demonstrates

This project is intentionally focused on practical data-engineering concepts rather than trying to include every DE technology in one repository.

It demonstrates:

- API and GraphQL ingestion
- pagination handling
- modular ETL design
- Pandas transformations
- data quality validation
- deterministic record hashing
- incremental synchronization
- PostgreSQL persistence
- dynamic SQL filtering
- local search indexing
- database backups and rebuilds
- Dockerized PostgreSQL
- reproducible local execution
- separation of responsibilities between pipeline, database, search, query, and UI layers

## What It Does Not Currently Include

This project does not currently include:

- Airflow or another workflow scheduler
- cloud object storage such as S3
- PySpark / distributed processing
- a cloud data warehouse
- dbt
- Kafka / streaming
- Kubernetes
- production monitoring and observability
- production-grade secret management

Those technologies are intentionally outside the current scope. They can be added in later projects or future iterations when they solve a real requirement rather than being added only for the sake of using more tools.

## Data Source

This project uses the public Rick & Morty API and its GraphQL interface:

```text
https://rickandmortyapi.com/graphql
```

The project extracts the current character data available from the source when the pipeline is run.

## License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2026 Aayush Badola

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

For the full text, see the [LICENSE](LICENSE) file in the repository root.

---

Maintained by **Aayush Badola**