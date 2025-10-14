import pandas as pd
import csv
import os
import tempfile

from sqlalchemy import create_engine, text
from sqlalchemy.types import DECIMAL, SmallInteger, String, Boolean

MYSQL_USER = "root"
MYSQL_PASS = "ahahjesuisunautremotdepasse"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB   = "hackaton"

MYSQL_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    "?charset=utf8mb4&local_infile=1"
)

engine = create_engine(MYSQL_URL, pool_pre_ping=True, connect_args={"local_infile": 1})

# Test rapide de la connexion
with engine.begin() as conn:
    conn.execute(text("SELECT 1"))
print("✅ Connexion MySQL OK")

TABLE = "traffic_data"

df = pd.read_sql(f"SELECT * FROM `{TABLE}`", con=engine)

# Transformation
df['Energy Consumption'] = df['Energy Consumption'].astype(str).str.replace('.', ',', regex=False)
df['Traffic Density'] = df['Traffic Density'].astype(str).str.replace('.', ',', regex=False)
df['Speed'] = df['Speed'].astype(str).str.replace('.', ',', regex=False)

TABLE_DST = "traffic_viz"

df["Is Peak Hour"] = df["Is Peak Hour"].astype(bool)
df["Random Event Occurred"] = df["Random Event Occurred"].astype(bool)
df["Hour Of Day"] = df["Hour Of Day"].astype("uint8")  # TINYINT UNSIGNED
# Eviter NaN dans les VARCHAR de sortie
for col in ["City","Vehicle Type","Weather","Economic Condition","Day Of Week",
            "Speed","Energy Consumption","Traffic Density"]:
    df[col] = df[col].fillna("")
    
# Colonnes dans l’ordre de la table cible
cols = ["City","Vehicle Type","Weather","Economic Condition","Day Of Week",
        "Hour Of Day","Speed","Is Peak Hour","Random Event Occurred",
        "Energy Consumption","Traffic Density"]
df_out = df[cols]

create_sql = f"""
CREATE TABLE IF NOT EXISTS `{TABLE_DST}` (
  `City` VARCHAR(100),
  `Vehicle Type` VARCHAR(50),
  `Weather` VARCHAR(50),
  `Economic Condition` VARCHAR(50),
  `Day Of Week` VARCHAR(20),
  `Hour Of Day` TINYINT UNSIGNED,
  `Speed` VARCHAR(20),
  `Is Peak Hour` BOOLEAN,
  `Random Event Occurred` BOOLEAN,
  `Energy Consumption` VARCHAR(20),
  `Traffic Density` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
with engine.begin() as conn:
    conn.execute(text(create_sql))
    # on repart propre
    conn.execute(text(f"TRUNCATE TABLE `{TABLE_DST}`"))

# 4) Export CSV temporaire puis LOAD DATA LOCAL INFILE
tmp_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
tmp_csv_path = tmp_csv.name
tmp_csv.close()

# Écrire un CSV simple: séparateur ',', guillemets si besoin, fin de ligne '\n'
df_out.to_csv(tmp_csv_path, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)
print("📝 CSV temporaire prêt →", tmp_csv_path)

load_sql = f"""
LOAD DATA LOCAL INFILE :path
INTO TABLE `{TABLE_DST}`
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(`City`,`Vehicle Type`,`Weather`,`Economic Condition`,`Day Of Week`,
 `Hour Of Day`,`Speed`,`Is Peak Hour`,`Random Event Occurred`,
 `Energy Consumption`,`Traffic Density`);
"""

try:
    with engine.begin() as conn:
        conn.execute(text(load_sql), {"path": tmp_csv_path})
    print(f"⚡ `{TABLE_DST}` chargé via LOAD DATA LOCAL INFILE.")
finally:
    try:
        os.remove(tmp_csv_path)
    except OSError:
        pass

# 5) Vérification
with engine.begin() as conn:
    n = conn.execute(text(f"SELECT COUNT(*) FROM `{TABLE_DST}`")).scalar_one()
print(f"✅ Lignes dans `{TABLE_DST}` :", n)

df.to_csv("on_compte_sur_toi.csv", index=False)