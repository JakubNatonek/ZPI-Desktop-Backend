# Testy backendu (pytest)

## Wymagania

- PostgreSQL zgodny z `.env` (`DATABASE_URL`)
- Aktywne venv i `pip install -r requirements.txt`

## Uruchomienie

```bash
cd ZPI-Desktop-Backend
source .venv/bin/activate
pytest -v
```

## Pokrycie (orientacyjne)

| Plik | Zakres |
|------|--------|
| `test_auth.py` | Logowanie, `/auth/me`, logout, cookies JWT |
| `test_jwt.py` | Brak tokenu, zły/wygasły JWT (cookie i `Authorization: Bearer`) |
| `test_rbac.py` | Uprawnienia: admin vs wykładowca, 401/403 |
| `test_crud_special_equipment.py` | CRUD wyposażenia specjalnego (funkcje + smoke API) |

### Konta testowe

| Login | Hasło | Rola |
|-------|-------|------|
| `admin` | `admin` | admin (seed) |
| `test_lecturer` | `lecturer` | wykladowca (tworzony przy pierwszym uruchomieniu testów) |

Testy RBAC nie obejmują każdego endpointu — sprawdzają reprezentatywne ścieżki (role, działy, użytkownicy, listy rapla).
