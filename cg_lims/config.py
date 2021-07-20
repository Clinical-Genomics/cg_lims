from pathlib import Path
from pydantic import BaseSettings

CG_LIMS_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = CG_LIMS_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"


class Settings(BaseSettings):
    """Settings for serving the statina app and connect to the mongo database"""

    baseuri: str
    host: str
    username: str
    password: str
    cg_url: str

    class Config:
        env_file = str(ENV_FILE)


class APISetting(Settings):
    """Settings for sending email"""

    cg_lims_host: str
    cg_lims_port: int

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()
