from app.core.settings import Settings


def test_settings_validate_chunk_overlap() -> None:
    settings = Settings(chunk_size=100, chunk_overlap=20)
    assert settings.chunk_size == 100
    assert settings.chunk_overlap == 20


def test_settings_content_types_parsing() -> None:
    settings = Settings(supported_content_types="text/plain, application/pdf")
    assert settings.supported_content_type_list == ["text/plain", "application/pdf"]
