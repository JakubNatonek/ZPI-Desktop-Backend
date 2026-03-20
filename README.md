# ZPI Desktop Backend

Prosty backend oparty na FastAPI.

## Wymagania

- Python 3.12+
- Wirtualne środowisko (`venv`)

## Instalacja lokalna

### Windows (PowerShell)

```powershell
python -m venv .venv;
.\.venv\Scripts\Activate.ps1;
pip install -r requirements.txt;
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Jak wyjść z venv

```bash
deactivate
```

## Uruchomienie docker

**Prepare environment:**

```powershell
copy .env.example .env.docker
```

**1. Starting (Build and start containers)**

```powershell
docker compose -f docker-compose.yml up -d --build
```

**2. Shutting down (Stop and remove containers)**

```powershell
docker compose -f docker-compose.yml down
```

**3. Check status (View running containers)**

```powershell
docker compose -f docker-compose.yml ps -a
```

**4. Restart (After initial build)**

```powershell
docker compose -f docker-compose.yml up -d
```

## Uruchomienie lokalne

**Prepare environment:**

```powershell
copy .env.example .env
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1;
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload;
```

### Linux/macOS

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Aplikacja będzie dostępna pod adresem: `http://127.0.0.1:8000`.

## Endpoint testowy

- `GET /` -> zwraca status `ok`

### Swagger
`http://127.0.0.1:8000/docs#/default`

## Migracje (Alembic)

Ta sekcja opisuje standardowy workflow migracji po zmianach w modelach SQLAlchemy.

### 1. Aktywuj środowisko

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Upewnij się, ze ustawiony jest poprawny DATABASE_URL

Alembic pobiera polaczenie z `.env` (przez `alembic/env.py`).

### 3. Wygeneruj nowa migracje po zmianie modeli

```powershell
python -m alembic revision --autogenerate -m "opis zmiany"
```

Przyklad:

```powershell
python -m alembic revision --autogenerate -m "add status to messages"
```

### 4. Sprawdz wygenerowany plik

Przed uruchomieniem migracji sprawdz `upgrade()` i `downgrade()` w nowym pliku w `alembic/versions`.

### 5. Zastosuj migracje

```powershell
python -m alembic upgrade head
```

### 6. Zweryfikuj stan rewizji

```powershell
python -m alembic current
python -m alembic heads
```

### Przydatne komendy

```powershell
python -m alembic downgrade -1
python -m alembic history
```