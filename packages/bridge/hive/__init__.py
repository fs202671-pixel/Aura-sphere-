"""
Hive System - Sistema de Colmeia (Bees)
======================================

Sistema de agentes organizadores e executores.
Características:
- Organização de tarefas
- Coordenação de execução
- Priorização inteligente
- Decisão coletiva
"""

from .bees.worker import BeeWorker
from .bees.scout import BeeScout
from .bees.coordinator import BeeCoordinator
from .bees.guard import BeeGuard

__all__ = ['BeeWorker', 'BeeScout', 'BeeCoordinator', 'BeeGuard']