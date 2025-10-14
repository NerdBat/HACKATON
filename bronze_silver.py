import boto3
import pandas as pd
from io import BytesIO
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.types import DECIMAL, SmallInteger, String, Boolean

ENDPOINT   = "https://play.min.io"      # ou "http://localhost:9000" si MinIO local
ACCESS_KEY = "Q3AM3UQ867SPQQA43P2F"     # clés publiques de MinIO Play
SECRET_KEY = "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG"

BUCKET = "hackatonraw"
KEY    = "futuristic_city_traffic.csv"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

def read_minio_to_df(bucket: str, key: str, filetype: str | None = None) -> pd.DataFrame:
    """
    Télécharge un objet MinIO en mémoire et le charge dans un DataFrame.
    filetype: 'csv' | 'parquet' | 'json' (si None, déduit de l'extension).
    """
    # 1) télécharger l'objet en mémoire
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read()
    buf = BytesIO(data)

    # 2) déterminer le type si non fourni
    if filetype is None:
        ext = Path(key).suffix.lower().lstrip(".")
        filetype = {"csv": "csv", "parquet": "parquet", "pq": "parquet", "json": "json"}.get(ext, "csv")

    # 3) lire selon le format
    if filetype == "csv":
        return pd.read_csv(buf, sep=",", encoding="utf-8")
    elif filetype == "parquet":
        return pd.read_parquet(buf)
    elif filetype == "json":
        try:
            return pd.read_json(buf, lines=True)
        except ValueError:
            buf.seek(0)
            return pd.read_json(buf)
    else:
        raise ValueError(f"Type de fichier non supporté: {filetype}")


df = read_minio_to_df(BUCKET, KEY)

"""df['Energy Consumption'] = df['Energy Consumption'].astype(str).str.replace('.', ',', regex=False)
df['Traffic Density'] = df['Traffic Density'].astype(str).str.replace('.', ',', regex=False)
df['Speed'] = df['Speed'].astype(str).str.replace('.', ',', regex=False)"""

df["Is Peak Hour"] = df["Is Peak Hour"].astype(bool)
df["Random Event Occurred"] = df["Random Event Occurred"].astype(bool)

assert df["Hour Of Day"].between(0, 23).all(), "Hour Of Day doit être entre 0 et 23"

MYSQL_USER = "root"
MYSQL_PASS = "mot de passe"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB   = "hackaton"

MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

engine = create_engine(MYSQL_URL, pool_pre_ping=True)

# Test rapide de la connexion
with engine.begin() as conn:
    conn.execute(text("SELECT 1"))
print("✅ Connexion MySQL OK")

dtype_map = {
    "City": String(100),
    "Vehicle Type": String(50),
    "Weather": String(50),
    "Economic Condition": String(50),
    "Day Of Week": String(20),
    "Hour Of Day": SmallInteger(),           # 0..23
    "Speed": DECIMAL(10, 4),
    "Is Peak Hour": Boolean(),               # MySQL -> TINYINT(1)
    "Random Event Occurred": Boolean(),      # MySQL -> TINYINT(1)
    "Energy Consumption": DECIMAL(12, 4),
    "Traffic Density": DECIMAL(12, 4),
}

TABLE = "traffic_data"

df.to_sql(
    TABLE,
    con=engine,
    if_exists="replace",      # replace ou append
    index=False,
    method="multi",
    chunksize=200_000,       
    dtype=dtype_map
)

print(f"✅ DataFrame écrit dans MySQL → table `{TABLE}`")

with engine.begin() as conn:
    n, = conn.execute(text("SELECT COUNT(*) FROM traffic_data")).scalar_one(), 
print("🚦 Lignes en base:", n)