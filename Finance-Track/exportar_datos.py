import requests
import pandas as pd

txs = requests.get("http://localhost:8000/transacciones?limit=1000").json()

df = pd.DataFrame([{
    "fecha": t["fecha"],
    "descripcion": t["descripcion"],
    "monto": t["monto"],
    "tipo": t["tipo"],
    "categoria": t["categoria"]["nombre"],
    "cuenta": t["cuenta"]["nombre"]
} for t in txs])

df.to_csv("data/processed/transacciones.csv", index=False)
print(f"Exportadas {len(df)} transacciones")