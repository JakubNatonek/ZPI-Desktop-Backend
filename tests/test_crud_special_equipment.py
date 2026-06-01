"""Unit tests for app.cruds.crud_special_equipment (create, read, update, delete)."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.cruds.crud_special_equipment import (
    create_special_equipment,
    delete_special_equipment,
    get_special_equipment_by_id,
    get_special_equipment_by_name,
    update_special_equipment,
)


def _unique_name(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def test_crud_create_read_update_delete(db_session: Session) -> None:
    name = _unique_name("pytest_equipment")
    created = create_special_equipment(db_session, name)
    db_session.commit()
    db_session.refresh(created)

    loaded = get_special_equipment_by_id(db_session, int(created.id))
    assert loaded is not None
    assert loaded.name == name

    found_by_name = get_special_equipment_by_name(db_session, name)
    assert found_by_name is not None
    assert int(found_by_name.id) == int(created.id)

    new_name = _unique_name("pytest_equipment_updated")
    updated = update_special_equipment(db_session, int(created.id), new_name)
    assert updated is not None
    assert updated.name == new_name

    assert delete_special_equipment(db_session, int(created.id)) is True
    assert get_special_equipment_by_id(db_session, int(created.id)) is None


def test_crud_update_duplicate_name_raises(db_session: Session) -> None:
    first = create_special_equipment(db_session, _unique_name("pytest_eq_a"))
    second = create_special_equipment(db_session, _unique_name("pytest_eq_b"))
    db_session.commit()

    try:
        with pytest.raises(ValueError, match="already exists"):
            update_special_equipment(db_session, int(second.id), str(first.name))
    finally:
        delete_special_equipment(db_session, int(first.id))
        delete_special_equipment(db_session, int(second.id))


def test_crud_delete_missing_returns_false(db_session: Session) -> None:
    assert delete_special_equipment(db_session, 999_999_999) is False


def test_api_special_equipment_crud_flow(admin_client: TestClient) -> None:
    """API smoke test — router wywołuje funkcje CRUD."""
    name = _unique_name("pytest_api_equipment")

    create = admin_client.post("/special-equipment", json={"name": name})
    assert create.status_code == 201
    item_id = create.json()["id"]
    assert create.json()["name"] == name

    detail = admin_client.get(f"/special-equipment/{item_id}")
    assert detail.status_code == 200
    assert detail.json()["name"] == name

    updated_name = _unique_name("pytest_api_equipment_upd")
    update = admin_client.put(
        f"/special-equipment/{item_id}",
        json={"name": updated_name},
    )
    assert update.status_code == 200
    assert update.json()["name"] == updated_name

    delete = admin_client.delete(f"/special-equipment/{item_id}")
    assert delete.status_code == 204

    missing = admin_client.get(f"/special-equipment/{item_id}")
    assert missing.status_code == 404
