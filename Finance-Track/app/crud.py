from sqlalchemy.orm import Session
from sqlalchemy import extract
from app import models, schemas


# ── Categorias ─────────────────────────────────────────
def get_categorias(db: Session):
    return db.query(models.Categoria).all()

def create_categoria(db: Session, categoria: schemas.CategoriaCreate):
    obj = models.Categoria(**categoria.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ── Cuentas ────────────────────────────────────────────
def get_cuentas(db: Session):
    return db.query(models.Cuenta).all()

def create_cuenta(db: Session, cuenta: schemas.CuentaCreate):
    obj = models.Cuenta(**cuenta.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ── Transacciones ──────────────────────────────────────
def get_transacciones(
    db: Session,
    mes: str = None,
    categoria_id: int = None,
    tipo: str = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.Transaccion)

    if mes:
        year, month = mes.split("-")
        query = query.filter(
            extract("year", models.Transaccion.fecha) == int(year),
            extract("month", models.Transaccion.fecha) == int(month)
        )
    if categoria_id:
        query = query.filter(models.Transaccion.categoria_id == categoria_id)
    if tipo:
        query = query.filter(models.Transaccion.tipo == tipo)

    return query.order_by(models.Transaccion.fecha.desc()).offset(skip).limit(limit).all()

def create_transaccion(db: Session, transaccion: schemas.TransaccionCreate):
    obj = models.Transaccion(**transaccion.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_transaccion(db: Session, transaccion_id: int):
    obj = db.query(models.Transaccion).filter(models.Transaccion.id == transaccion_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# ── Presupuestos ───────────────────────────────────────
def get_presupuestos(db: Session, mes: str = None):
    query = db.query(models.Presupuesto)
    if mes:
        query = query.filter(models.Presupuesto.mes == mes)
    return query.all()

def create_presupuesto(db: Session, presupuesto: schemas.PresupuestoCreate):
    obj = models.Presupuesto(**presupuesto.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ── Resumen mensual ────────────────────────────────────
def get_resumen_mensual(db: Session, mes: str) -> schemas.ResumenMensual:
    year, month = mes.split("-")

    transacciones = db.query(models.Transaccion).filter(
        extract("year", models.Transaccion.fecha) == int(year),
        extract("month", models.Transaccion.fecha) == int(month)
    ).all()

    total_ingresos = sum(t.monto for t in transacciones if t.tipo == "ingreso")
    total_gastos = sum(t.monto for t in transacciones if t.tipo == "gasto")

    gastos_por_cat = {}
    for t in transacciones:
        if t.tipo == "gasto":
            nombre_cat = t.categoria.nombre
            gastos_por_cat[nombre_cat] = gastos_por_cat.get(nombre_cat, 0) + t.monto

    presupuestos = {
        p.categoria.nombre: p.monto_limite
        for p in get_presupuestos(db, mes=mes)
    }

    por_categoria = []
    for cat, gastado in gastos_por_cat.items():
        limite = presupuestos.get(cat)
        porcentaje = round((gastado / limite) * 100, 1) if limite else None
        por_categoria.append(schemas.ResumenCategoria(
            categoria=cat,
            total_gastado=round(gastado, 0),
            presupuesto=limite,
            porcentaje_usado=porcentaje,
            alerta=porcentaje > 100 if porcentaje else False
        ))

    return schemas.ResumenMensual(
        mes=mes,
        total_ingresos=round(total_ingresos, 0),
        total_gastos=round(total_gastos, 0),
        balance=round(total_ingresos - total_gastos, 0),
        por_categoria=sorted(por_categoria, key=lambda x: x.total_gastado, reverse=True)
    )