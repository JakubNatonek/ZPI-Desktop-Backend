from app.core.database import engine
from app.models.model_user import User
from app.models.model_audit_log import AuditLog
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN last_changes_viewed_at TIMESTAMP WITH TIME ZONE;'))
        conn.commit()
        print("Column last_changes_viewed_at added successfully.")
    except Exception as e:
        print("Column might already exist or error:", e)

AuditLog.__table__.create(bind=engine, checkfirst=True)
print("AuditLog table ensured.")
