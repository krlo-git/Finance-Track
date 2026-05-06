import pandas as pd

COLUMNAS_REQUERIDAS = {"Date", "Description", "Amount", "Transaction Type", "Category", "Account Name"}

MAPA_TIPOS = {
    "debit": "gasto",
    "credit": "ingreso",
}

def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Validar columnas
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(f"El CSV no tiene las columnas requeridas: {faltantes}")

    # Renombrar columnas a nuestro esquema
    df = df.rename(columns={
        "Date": "fecha",
        "Description": "descripcion",
        "Amount": "monto",
        "Transaction Type": "tipo",
        "Category": "categoria",
        "Account Name": "cuenta"
    })

    # Eliminar filas vacías
    df = df.dropna(how="all")

    # Fechas
    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=False, errors="coerce").dt.date
    df = df.dropna(subset=["fecha"])

    # Montos: siempre positivo
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").abs()
    df = df.dropna(subset=["monto"])
    df = df[df["monto"] > 0]

    # Tipo: debit → gasto, credit → ingreso
    df["tipo"] = df["tipo"].str.strip().str.lower().map(MAPA_TIPOS)
    df = df.dropna(subset=["tipo"])

    # Texto
    df["descripcion"] = df["descripcion"].str.strip().str.slice(0, 200)
    df["categoria"] = df["categoria"].str.strip().str.title()
    df["cuenta"] = df["cuenta"].str.strip().str.title()

    df = df.reset_index(drop=True)
    print(f"✓ Limpieza completa: {len(df)} filas válidas")
    return df