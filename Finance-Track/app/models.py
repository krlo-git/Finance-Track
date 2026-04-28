from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TipoTransaccion(str, enum.Enum):
    ingreso = "ingreso"
    gasto = "gasto"


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    tipo = Column(Enum(TipoTransaccion), nullable=False)

    transacciones = relationship("Transaccion", back_populates="categoria")
    presupuestos = relationship("Presupuesto", back_populates="categoria")


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(30), nullable=False)

    transacciones = relationship("Transaccion", back_populates="cuenta")


class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    descripcion = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    tipo = Column(Enum(TipoTransaccion), nullable=False)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)

    categoria = relationship("Categoria", back_populates="transacciones")
    cuenta = relationship("Cuenta", back_populates="transacciones")


class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    mes = Column(String(7), nullable=False)
    monto_limite = Column(Float, nullable=False)

    categoria = relationship("Categoria", back_populates="presupuestos")