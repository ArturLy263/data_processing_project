import pytest
from src.validators.file_validator import FileValidator


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        with FileValidator("nonexistent_file.csv", "r") as f:
            pass


def test_write_mode_creates_file(tmp_path):
    filepath = tmp_path / "test.csv"
    with FileValidator(str(filepath), "w") as f:
        f.write("test")
    assert filepath.exists()
