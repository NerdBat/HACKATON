from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
import mlflow.sklearn
import joblib

# === CONFIGURATION ===
MODEL_PATH = "./mlruns/885412425188802638/models/m-33e13dd8a528466f87feb304cbd60e1f/artifacts"
ENCODER_PATH = "label_encoder.pkl"
CITY_OPTIONS = ['AquaCity','Ecoopolis','MetropolisX','Neuroburg','SolarisVille','TechHaven']

# === INITIALISATION ===
app = FastAPI(title="Traffic Density Predictor API")

model = mlflow.sklearn.load_model(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

feature_cols = ['Day Of Week', 'Hour Of Day'] + [f'Is_{c}' for c in CITY_OPTIONS]

@app.get("/", response_class=HTMLResponse)
def form_page():
    html_content = f"""
    <html>
        <head>
            <title>Prédiction de densité du trafic</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #74ABE2, #5563DE);
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    background-color: #fff;
                    padding: 40px;
                    border-radius: 16px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                    width: 360px;
                    text-align: center;
                    animation: fadeIn 0.8s ease;
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(-10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                h1 {{
                    color: #2C3E50;
                    margin-bottom: 20px;
                }}
                label {{
                    font-weight: 600;
                    display: block;
                    margin-top: 15px;
                    text-align: left;
                }}
                select, input[type=number] {{
                    width: 100%;
                    padding: 10px;
                    margin-top: 5px;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    font-size: 15px;
                    box-sizing: border-box;
                }}
                input[type=submit] {{
                    background-color: #5563DE;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 10px;
                    margin-top: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    width: 100%;
                    transition: background-color 0.3s;
                }}
                input[type=submit]:hover {{
                    background-color: #3949AB;
                }}
                footer {{
                    margin-top: 15px;
                    font-size: 13px;
                    color: #777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚦 Prédiction du trafic</h1>
                <form action="/predict" method="post">
                    <label>Ville :</label>
                    <select name="city">
                        {''.join([f'<option value="{c}">{c}</option>' for c in CITY_OPTIONS])}
                    </select>

                    <label>Jour de la semaine (0=Lundi, 6=Dimanche) :</label>
                    <input type="number" name="day" min="0" max="6" value="3">

                    <label>Heure (0-23) :</label>
                    <input type="number" name="hour" min="0" max="23" value="14">

                    <input type="submit" value="Prédire la densité">
                </form>
                <footer>✨ Powered by FastAPI & MLflow</footer>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/predict", response_class=HTMLResponse)
def predict_traffic(city: str = Form(...), day: int = Form(...), hour: int = Form(...)):
    # === Préparation des données ===
    df_input = pd.DataFrame(columns=feature_cols)
    df_input.loc[0] = 0
    df_input['Day Of Week'] = day
    df_input['Hour Of Day'] = hour

    city_col = f'Is_{city}'
    if city_col in df_input.columns:
        df_input[city_col] = 1

    # === Prédiction ===
    pred_num = model.predict(df_input)[0]
    pred_label = label_encoder.inverse_transform([int(pred_num)])[0]

    # === Recommandation selon le trafic ===
    def get_transport_recommendation(pred_label: str) -> str:
        recommendations = {
            "Low": "🚗 La circulation est fluide, vous pouvez prendre la voiture ou le vélo.",
            "Medium": "🚌 Trafic modéré, le bus est une bonne alternative.",
            "High": "🚋 Trafic dense, privilégiez le tramway ou le vélo.",
            "Very High": "🚇 Trafic très chargé, préférez le métro pour gagner du temps."
        }
        return recommendations.get(pred_label, "ℹ️ Aucune recommandation disponible.")
    
    recommendation = get_transport_recommendation(pred_label)

    # === Rendu HTML ===
    return HTMLResponse(f"""
    <html>
        <head>
            <title>Résultat de la prédiction</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #74ABE2, #5563DE);
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .result-box {{
                    background-color: #fff;
                    padding: 40px;
                    border-radius: 16px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                    width: 400px;
                    text-align: center;
                    animation: fadeIn 0.8s ease;
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(-10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                h2 {{
                    color: #2C3E50;
                }}
                h3 {{
                    color: #5563DE;
                    margin-top: 20px;
                }}
                p.reco {{
                    margin-top: 20px;
                    font-weight: 600;
                    background-color: #EEF2FF;
                    border-left: 5px solid #5563DE;
                    padding: 10px;
                    border-radius: 8px;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    color: white;
                    background-color: #5563DE;
                    padding: 10px 20px;
                    border-radius: 8px;
                    text-decoration: none;
                    transition: background-color 0.3s;
                }}
                a:hover {{
                    background-color: #3949AB;
                }}
            </style>
        </head>
        <body>
            <div class="result-box">
                <h2>Résultat 🚦</h2>
                <p><b>Ville :</b> {city}</p>
                <p><b>Jour :</b> {day}</p>
                <p><b>Heure :</b> {hour}</p>
                <h3>➡️ Densité prédite : <b>{pred_label}</b></h3>
                <p class="reco">💡 {recommendation}</p>
                <a href="/">Faire une autre prédiction</a>
            </div>
        </body>
    </html>
    """)
