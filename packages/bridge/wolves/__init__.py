"""
Wolves Defense Module
====================

Módulo dos lobos do sistema de defesa ativa.
Inclui scouts, sentinels, responders, forensics e recovery.
"""

from .scout import WolfScout
from .sentinel import WolfSentinel, RiskLevel
from .responder import WolfResponder, ResponseAction
from .forensic import WolfForensic, EvidenceType
from .recovery import WolfRecovery, RecoveryAction

__version__ = "1.0.0"
__author__ = "Aura Sphere Defense System"

__all__ = [
    'WolfScout',
    'WolfSentinel',
    'WolfResponder',
    'WolfForensic',
    'WolfRecovery',
    'RiskLevel',
    'ResponseAction',
    'EvidenceType',
    'RecoveryAction'
]