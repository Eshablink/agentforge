"""One-shot maintenance entry point; never run automatically on API startup."""
from app.db.session import SessionLocal
from app.services.auth_service import cleanup_sessions


def main() -> None:
    with SessionLocal() as db:
        cleanup_sessions(db, batch_size=500)


if __name__ == "__main__":
    main()
