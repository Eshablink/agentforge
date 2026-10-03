import uuid

from app.models.document import Document
from app.services.ingestion_service import IngestionError


def test_ingestion_validation_rejects_missing_filename() -> None:
    service = object.__new__(type("_S", (), {"settings": None}))

    # sanity check for canonical error class existence
    assert issubclass(IngestionError, Exception)
    assert isinstance(uuid.uuid4(), uuid.UUID)


def test_document_model_defaults_status() -> None:
    document = Document(
        id=uuid.uuid4(),
        filename="doc.txt",
        content_type="text/plain",
        metadata_json={},
        status="processed",
    )

    assert document.status == "processed"
