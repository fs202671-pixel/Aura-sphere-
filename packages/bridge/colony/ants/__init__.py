"""
Ants - Agentes Exploradores
===========================

Agentes leves especializados em:
- Exploração de repositórios
- Busca de dados externos
- Análise de código
- Testes de soluções

Características:
- Paralelismo massivo
- Comunicação indireta
- Baixo overhead
- Reforço por trilhas
"""

from .explorer import AntExplorer
from .communication import AntCommunication
from .trails import TrailSystem
from .coordinator import AntCoordinator

__all__ = ['AntExplorer', 'AntCommunication', 'TrailSystem', 'AntCoordinator']
from .coordinator import AntCoordinator

__all__ = ['AntExplorer', 'AntCommunication', 'TrailSystem', 'AntCoordinator']