import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "MULE MATRIX"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    DATA_DIR: Path = DATA_DIR
    SAVED_MODELS_DIR: Path = SAVED_MODELS_DIR
    
    # Databases
    DATABASE_PATH: Path = DATA_DIR / "mule_matrix.db"
    TEST_DATABASE_PATH: Path = DATA_DIR / "test_mule_matrix.db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{self.DATABASE_PATH.as_posix()}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"sqlite:///{self.TEST_DATABASE_PATH.as_posix()}"

    # Engine Defaults & Thresholds
    VELOCITY_RAPID_PASSTHROUGH_THRESHOLD: float = 0.85  # 85% passed through within window
    VELOCITY_BURST_TX_COUNT: int = 5                   # >=5 txs in window
    BFS_DEFAULT_MAX_HOPS: int = 4
    BFS_MAX_SEARCH_BUDGET: int = 250                   # max nodes or edges to explore
    BFS_LOOKBACK_HOURS: int = 72
    BFS_LOOKAHEAD_HOURS: int = 72
    
    # Model Artifact Paths
    ISOLATION_FOREST_PATH: Path = SAVED_MODELS_DIR / "isolation_forest.joblib"
    GRAPHSAGE_MODEL_PATH: Path = SAVED_MODELS_DIR / "graphsage_model.pt"
    GRAPHSAGE_METADATA_PATH: Path = SAVED_MODELS_DIR / "graphsage_meta.json"

settings = Settings()
