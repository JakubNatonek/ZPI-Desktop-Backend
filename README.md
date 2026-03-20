# ZPI Desktop Backend

Prosty backend oparty o FastAPI.

## Wymagania

- Python 3.12+
- Wirtualne srodowisko (`venv`)

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
uvicorn app.main:app --reload
```
### jak wyjsc z venv 
deactivate

## Uruchomienie lokalne


### Windows (PowerShell)
uvicorn app.main:app --reload

```powershell
.\.venv\Scripts\Activate.ps1;
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload;
```

### Linux/macOS

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Aplikacja bedzie dostepna pod adresem: `http://127.0.0.1:8000`.

## Endpoint testowy

- `GET /` -> zwraca status `ok`

### Swager
`http://127.0.0.1:8000/docs#/default`