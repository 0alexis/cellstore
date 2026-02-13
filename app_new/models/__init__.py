"""
Modelos de base de datos
"""
from .user import User
from .celular import Celular
from .transaccion import Transaccion
from .tradein import TradeIn, Deuda
from .configuracion import ConfiguracionEmpresa

__all__ = [
    'User',
    'Celular', 
    'Transaccion',
    'TradeIn',
    'Deuda',
    'ConfiguracionEmpresa'
]
