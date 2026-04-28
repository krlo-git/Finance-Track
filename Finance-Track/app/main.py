from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, schemas
from app.database import get_db, create_tables

app = FastAPI(
    title="Finance Tracker API",
    description="API para rastreo de finanzas personales",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    create_tables()


# ── Health check ───────────────────────────────────────
@app.get("/", tags=["General"])
def root():
    return {"status": "ok", "mensaje": "Finance Tracker API activa"}


# ── Categorias ─────────────────────────────────────────
@app.get("/categorias", response_model=list[schemas.CategoriaOut], tags=["Categorias"])
def listar_categorias(db: Session = Depends(get_db)):
    return crud.get_categorias(db)

@app.post("/categorias", response_model=schemas.CategoriaOut, status_code=201, tags=["Categorias"])
def crear_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    return crud.create_categoria(db, categoria)


# ── Cuentas ────────────────────────────────────────────
@app.get("/cuentas", response_model=list[schemas.CuentaOut], tags=["Cuentas"])
def listar_cuentas(db: Session = Depends(get_db)):
    return crud.get_cuentas(db)

@app.post("/cuentas", response_model=schemas.CuentaOut, status_code=201, tags=["Cuentas"])
def crear_cuenta(cuenta: schemas.CuentaCreate, db: Session = Depends(get_db)):
    return crud.create_cuenta(db, cuenta)


# ── Transacciones ──────────────────────────────────────
@app.get("/transacciones", response_model=list[schemas.TransaccionOut], tags=["Transacciones"])
def listar_transacciones(
    mes: Optional[str] = None,
    categoria_id: Optional[int] = None,
    tipo: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_transacciones(db, mes=mes, categoria_id=categoria_id, tipo=tipo, skip=skip, limit=limit)

@app.post("/transacciones", response_model=schemas.TransaccionOut, status_code=201, tags=["Transacciones"])
def crear_transaccion(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db)):
    return crud.create_transaccion(db, transaccion)

@app.delete("/transacciones/{transaccion_id}", tags=["Transacciones"])
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_transaccion(db, transaccion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return {"mensaje": f"Transacción {transaccion_id} eliminada"}


# ── Presupuestos ───────────────────────────────────────
@app.get("/presupuestos", response_model=list[schemas.PresupuestoOut], tags=["Presupuestos"])
def listar_presupuestos(mes: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_presupuestos(db, mes=mes)

@app.post("/presupuestos", response_model=schemas.PresupuestoOut, status_code=201, tags=["Presupuestos"])
def crear_presupuesto(presupuesto: schemas.PresupuestoCreate, db: Session = Depends(get_db)):
    return crud.create_presupuesto(db, presupuesto)


# ── Resumen mensual ────────────────────────────────────
@app.get("/resumen", response_model=schemas.ResumenMensual, tags=["Analisis"])
def resumen_mensual(mes: str, db: Session = Depends(get_db)):
    return crud.get_resumen_mensual(db, mes)