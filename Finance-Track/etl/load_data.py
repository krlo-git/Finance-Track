import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.database import SessionLocal, create_tables
from app import models
from etl.clean import limpiar_dataframe


def seed_catalogos(db):
    """Inserta cuentas base si no existen."""
    cuentas = [
        ("Platinum Card", "credito"),
        ("Silver Card", "credito"),
        ("Checking", "debito"),
        ("Savings", "debito"),
    ]
    for nombre, tipo in cuentas:
        existe = db.query(models.Cuenta).filter_by(nombre=nombre).first()
        if not existe:
            db.add(models.Cuenta(nombre=nombre, tipo=tipo))
    db.commit()
    print("✓ Catálogos base cargados")


def cargar_csv(filepath: str):
    db = SessionLocal()
    create_tables()
    seed_catalogos(db)

    df = pd.read_csv(filepath)
    df = limpiar_dataframe(df)

    cargadas = 0
    errores = 0

    for _, row in df.iterrows():
        try:
            # Buscar o crear categoría
            categoria = db.query(models.Categoria).filter_by(nombre=row["categoria"]).first()
            if not categoria:
                categoria = models.Categoria(nombre=row["categoria"], tipo=row["tipo"])
                db.add(categoria)
                db.flush()

            # Buscar o crear cuenta
            cuenta = db.query(models.Cuenta).filter_by(nombre=row["cuenta"]).first()
            if not cuenta:
                cuenta = models.Cuenta(nombre=row["cuenta"], tipo="debito")
                db.add(cuenta)
                db.flush()

            transaccion = models.Transaccion(
                fecha=row["fecha"],
                descripcion=row["descripcion"],
                monto=row["monto"],
                tipo=row["tipo"],
                categoria_id=categoria.id,
                cuenta_id=cuenta.id,
            )
            db.add(transaccion)
            cargadas += 1

        except Exception as e:
            print(f"  ✗ Error en fila {_}: {e}")
            errores += 1

    db.commit()
    db.close()
    print(f"✓ Carga completa: {cargadas} transacciones insertadas, {errores} errores")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Ruta al CSV")
    args = parser.parse_args()
    cargar_csv(args.file)