# ZPI Desktop Backend

Prosty backend oparty o FastAPI.

## Wymagania

- Python 3.12+
- Wirtualne srodowisko (`venv`)

## Instalacja

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uruchomienie

```bash
uvicorn app.main:app --reload
```

Aplikacja bedzie dostepna pod adresem: `http://127.0.0.1:8000`.

## Endpoint testowy

- `GET /` -> zwraca status `ok`
