"""
Colony System - Formigas (Ants)
===============================

Sistema de agentes exploradores leves e paralelos para descoberta, análise e busca.

Características:
- Execução massiva paralela
- Baixo custo individual
- Comunicação indireta via memória
- Trilhas de reforço para soluções eficientes
"""

from .ants import AntExplorer, AntCommunication, TrailSystem, AntCoordinator

__all__ = ['AntExplorer', 'AntCommunication', 'TrailSystem', 'AntCoordinator']