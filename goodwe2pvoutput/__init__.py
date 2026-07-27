import logging
from pathlib import Path
from typing import Self

from pvoutput.parameters import ADDSTATUS_PARAMETERS
from pydantic import (
    Field,
    SecretStr,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    CliImplicitFlag,
    EnvSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger("goodwe2pvoutput")

__all__ = ["CONFIG_FILES", "LOGGER", "Config"]

CONFIG_FILES = [
    "./goodwe2pvoutput.json",
    "/etc/goodwe2pvoutput.json",
    f"{Path.home()!s}/.goodwe2pvoutput.json",
]


class Config(BaseSettings, cli_parse_args=True, cli_kebab_case=True):
    logging_level: str = Field("INFO", description="Logging level")

    goodwe_username: str = Field(description="Goodwe username (email)")
    goodwe_password: SecretStr = Field(description="Goodwe account password")
    goodwe_systemid: str = Field(description="Goodwe account systemd ID")

    schedule_minutes: int = Field(10, description="Schedule time in minutes")

    pvoutput_apikey: SecretStr = Field(description="PVOutput API key")
    pvoutput_systemid: int = Field(description="PVOutput system ID")
    pvoutput_donation_made: bool = Field(
        False, description="Donation made to PVOutput, enable extra fields"
    )
    pvoutput_soc_enable: bool = Field(
        False, description="Enable State of Charge logging"
    )
    pvoutput_soc_field: str | None = Field(
        default=None, description="State of Charge field name"
    )

    show_config: CliImplicitFlag[bool] = Field(
        False,
        description="Show the configuration and exit",
        exclude=True,
    )
    dry_run: CliImplicitFlag[bool] = Field(
        False,
        description="Dry run, do not send data to PVOutput",
        exclude=True,
    )

    model_config = SettingsConfigDict(env_prefix="", extra="forbid", frozen=True)

    @field_serializer("goodwe_password", "pvoutput_apikey", when_used="always")
    def dump_secret(self, v):
        val = v.get_secret_value() if v else ""
        return val[: min(len(val) // 2, 5)] + "..." if v else None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return EnvSettingsSource(settings_cls, env_prefix=""), JsonConfigSettingsSource(
            settings_cls, json_file=CONFIG_FILES, deep_merge=True
        )

    @field_validator("logging_level")
    @classmethod
    def check_logging_level(cls, v: str) -> str:
        if v.upper() not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]:
            raise ValueError(f"Invalid logging level: {v}")
        return v.upper()

    @model_validator(mode="after")
    def check_soc_field(self) -> Self:
        if self.pvoutput_soc_enable and not self.pvoutput_donation_made:
            raise ValueError("Cannot log State of Charge if you have not donated")
        if (
            self.pvoutput_soc_field is not None
            and self.pvoutput_soc_field not in ADDSTATUS_PARAMETERS
        ):
            raise ValueError(
                f'Cannot log State of Charge to field "{self.pvoutput_soc_field}" - field does not exist'
            )
        return self
