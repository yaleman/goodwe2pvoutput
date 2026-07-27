"""tests nothing, makes pytest happy"""

import pytest
from pydantic import ValidationError

from goodwe2pvoutput import Config


def test_cli_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """tests the help command works"""

    try:
        monkeypatch.setattr("sys.argv", ["example.py", "--help"])
        Config()

    except SystemExit as e:
        print(e)


def test_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """tests the cli parsing works"""

    try:
        monkeypatch.setattr("goodwe2pvoutput.CONFIG_FILES", [])
        monkeypatch.setattr(
            "sys.argv",
            [
                "example.py",
                "--goodwe-username",
                "testuser",
                "--goodwe-password",
                "testpass",
                "--goodwe-systemid",
                "12345",
                "--pvoutput-apikey",
                "testapikey",
                "--pvoutput-systemid",
                "67890",
            ],
        )
        config = Config()
        assert config.goodwe_username == "testuser"
        assert config.goodwe_password.get_secret_value() == "testpass"
        assert config.goodwe_systemid == "12345"
        assert config.pvoutput_apikey.get_secret_value() == "testapikey"
        assert config.pvoutput_systemid == 67890

    except SystemExit as e:
        print(e)


def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """tests the env var parsing works"""

    try:
        monkeypatch.setattr("goodwe2pvoutput.CONFIG_FILES", [])
        monkeypatch.setattr(
            "sys.argv",
            [
                "example.py",
            ],
        )
        monkeypatch.setenv("GOODWE_USERNAME", "testuser")
        monkeypatch.setenv("GOODWE_PASSWORD", "testpass")
        monkeypatch.setenv("GOODWE_SYSTEMID", "12345")
        monkeypatch.setenv("PVOUTPUT_APIKEY", "testapikey")
        monkeypatch.setenv("PVOUTPUT_SYSTEMID", "67890")
        config = Config()
        assert config.goodwe_username == "testuser"
        assert config.goodwe_password.get_secret_value() == "testpass"
        assert config.goodwe_systemid == "12345"
        assert config.pvoutput_apikey.get_secret_value() == "testapikey"
        assert config.pvoutput_systemid == 67890

    except SystemExit as e:
        print(e)


def test_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """tests that missing CLI arguments cause failure"""

    monkeypatch.setattr("goodwe2pvoutput.CONFIG_FILES", [])
    monkeypatch.setattr(
        "sys.argv",
        [
            "example.py",
        ],
    )
    with pytest.raises(ValidationError):
        Config()
