from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from app.models import TipoTransaccion


# ── Categoria ──────────────────────────────────────────
class CategoriaBase(BaseModel):
    nombre: str
    tipo: TipoTransaccion

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaOut(CategoriaBase):
    id: int
    class Config:
        from_attributes = True


# ── Cuenta ─────────────────────────────────────────────
class CuentaBase(BaseModel):
    nombre: str
    tipo: str

class CuentaCreate(CuentaBase):
    pass

class CuentaOut(CuentaBase):
    id: int
    class Config:
        from_attributes = True


# ── Transaccion ────────────────────────────────────────
class TransaccionBase(BaseModel):
    fecha: date
    descripcion: str
    monto: float = Field(gt=0, description="Monto debe ser positivo")
    tipo: TipoTransaccion
    categoria_id: int
    cuenta_id: int

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionOut(TransaccionBase):
    id: int
    categoria: CategoriaOut
    cuenta: CuentaOut
    class Config:
        from_attributes = True


# ── Presupuesto ────────────────────────────────────────
class PresupuestoBase(BaseModel):
    categoria_id: int
    mes: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Formato: YYYY-MM")
    monto_limite: float = Field(gt=0)

class PresupuestoCreate(PresupuestoBase):
    pass

class PresupuestoOut(PresupuestoBase):
    id: int
    categoria: CategoriaOut
    class Config:
        from_attributes = True


# ── Resumen mensual ────────────────────────────────────
class ResumenCategoria(BaseModel):
    categoria: str
    total_gastado: float
    presupuesto: Optional[float] = None
    porcentaje_usado: Optional[float] = None
    alerta: bool = False

class ResumenMensual(BaseModel):
    mes: str
    total_ingresos: float
    total_gastos: float
    balance: float
    por_categoria: list[ResumenCategoria]