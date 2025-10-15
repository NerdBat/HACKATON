import boto3
from pathlib import Path
from tempfile import NamedTemporaryFile
from sqlalchemy import create_engine, text

# --- MinIO  ---
ENDPOINT   = "https://play.min.io"
ACCESS_KEY = "Q3AM3UQ867SPQQA43P2F"
SECRET_KEY = "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG"

BUCKET = "hackatonraw"
KEY    = "futuristic_city_traffic.csv"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# --- MySQL ---
MYSQL_USER = "root"
MYSQL_PASS = "jesuisunmotdepasse"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB   = "hackaton"

# local_infile=1 + connect_args pour PyMySQL
MYSQL_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    "?charset=utf8mb4&local_infile=1"
)
engine = create_engine(MYSQL_URL, pool_pre_ping=True, connect_args={"local_infile": 1})

TABLE = "traffic_data"

# --- 1) Télécharger l'objet MinIO vers un fichier temporaire (zéro copie en RAM) ---
with NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
    tmp_name = tmp.name
    s3.download_fileobj(BUCKET, KEY, tmp)

print(f"📥 CSV téléchargé → {tmp_name}")

# --- 2) Créer la table ---
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS `{TABLE}` (
  `City`                   VARCHAR(100),
  `Vehicle Type`          VARCHAR(50),
  `Weather`               VARCHAR(50),
  `Economic Condition`    VARCHAR(50),
  `Day Of Week`           VARCHAR(20),
  `Hour Of Day`           SMALLINT,
  `Speed`                 DECIMAL(10,4),
  `Is Peak Hour`          TINYINT(1),
  `Random Event Occurred` TINYINT(1),
  `Energy Consumption`    DECIMAL(12,4),
  `Traffic Density`       DECIMAL(12,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# --- 3) Bulk load ultra-rapide ---
# On importe dans des variables @col pour convertir proprement types/booléens
load_sql = f"""
LOAD DATA LOCAL INFILE :path
INTO TABLE `{TABLE}`
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@City, @VehicleType, @Weather, @EconomicCondition, @DayOfWeek,
 @HourOfDay, @Speed, @IsPeak, @RandomEvent, @EnergyConsumption, @TrafficDensity)
SET
  `City`                   = NULLIF(@City,''),
  `Vehicle Type`           = NULLIF(@VehicleType,''),
  `Weather`                = NULLIF(@Weather,''),
  `Economic Condition`     = NULLIF(@EconomicCondition,''),
  `Day Of Week`            = NULLIF(@DayOfWeek,''),
  `Hour Of Day`            = NULLIF(@HourOfDay,''),
  `Speed`                  = NULLIF(@Speed,''),
  `Is Peak Hour`           = CASE LOWER(TRIM(@IsPeak))
                               WHEN 'true' THEN 1 WHEN '1' THEN 1
                               WHEN 'false' THEN 0 WHEN '0' THEN 0
                               ELSE NULL
                             END,
  `Random Event Occurred`  = CASE LOWER(TRIM(@RandomEvent))
                               WHEN 'true' THEN 1 WHEN '1' THEN 1
                               WHEN 'false' THEN 0 WHEN '0' THEN 0
                               ELSE NULL
                             END,
  `Energy Consumption`     = NULLIF(@EnergyConsumption,''),
  `Traffic Density`        = NULLIF(@TrafficDensity,'');
"""

with engine.begin() as conn:
    # Assure la connexion
    conn.execute(text("SELECT 1"))

    # (re)crée la table vide (on la remplace pour aller plus vite)
    conn.execute(text(f"DROP TABLE IF EXISTS `{TABLE}`"))
    conn.execute(text(create_table_sql))

    # Accélérations session (désactive contraintes/index pendant l'import)
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    conn.execute(text("SET UNIQUE_CHECKS=0"))
    conn.execute(text("SET AUTOCOMMIT=0"))

    # Si un index secondaire existait, on pourrait faire:
    # conn.execute(text(f"ALTER TABLE `{TABLE}` DISABLE KEYS"))

    # Charger le fichier
    conn.execute(text(load_sql), {"path": tmp_name})

    # Réactiver
    # conn.execute(text(f"ALTER TABLE `{TABLE}` ENABLE KEYS"))
    conn.execute(text("SET UNIQUE_CHECKS=1"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

# Vérif rapide
with engine.begin() as conn:
    n = conn.execute(text(f"SELECT COUNT(*) FROM `{TABLE}`")).scalar_one()
print("✅ Lignes chargées :", n)
