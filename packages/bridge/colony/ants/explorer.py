"""
Ant Explorer - Agente Explorador Básico
========================================

Agente leve especializado em exploração e descoberta.
Características:
- Baixo consumo de recursos
- Execução paralela
- Comunicação indireta via trilhas
- Foco em descoberta de soluções
"""

import asyncio
import uuid
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from core.security import SecurityManager
from runtime.sandbox import SandboxManager
from colony.ants.communication import AntCommunication

logger = logging.getLogger(__name__)

@dataclass
class ExplorationResult:
    """Resultado de uma exploração"""
    ant_id: str
    task_id: str
    findings: List[Dict[str, Any]]
    trails: List[Dict[str, Any]]
    timestamp: float
    quality_score: float

class AntExplorer:
    """
    Agente explorador básico - Formiga

    Funcionalidades:
    - Exploração de repositórios
    - Busca de dados externos
    - Análise de código
    - Testes de soluções
    """

    def __init__(self, ant_id: Optional[str] = None):
        self.ant_id = ant_id or str(uuid.uuid4())
        self.security = SecurityManager()
        self.sandbox = SandboxManager()
        self.communication = AntCommunication()
        self.active = False
        self.exploration_count = 0

        logger.info(f"AntExplorer {self.ant_id} initialized")

    async def explore_repository(self, repo_path: str, task: Dict[str, Any]) -> ExplorationResult:
        """
        Explora um repositório em busca de soluções relevantes

        Args:
            repo_path: Caminho para o repositório
            task: Descrição da tarefa de exploração

        Returns:
            Resultado da exploração
        """
        start_time = time.time()

        try:
            # Verificar permissões de segurança
            if not await self.security.validate_access(repo_path, 'read'):
                raise PermissionError(f"Access denied to {repo_path}")

            # Executar exploração em sandbox
            findings = await self._analyze_repository(repo_path, task)

            # Criar trilhas de reforço
            trails = await self._create_trails(findings, task)

            # Calcular score de qualidade
            quality_score = self._calculate_quality_score(findings, trails)

            result = ExplorationResult(
                ant_id=self.ant_id,
                task_id=task.get('id', 'unknown'),
                findings=findings,
                trails=trails,
                timestamp=time.time(),
                quality_score=quality_score
            )

            # Comunicar resultado via trilhas
            await self.communication.leave_trail(result)

            self.exploration_count += 1
            logger.info(f"Ant {self.ant_id} completed exploration of {repo_path}")

            return result

        except Exception as e:
            logger.error(f"Ant {self.ant_id} exploration failed: {e}")
            # Mesmo em erro, deixar trilha de "caminho ruim"
            await self.communication.leave_trail({
                'ant_id': self.ant_id,
                'task_id': task.get('id', 'unknown'),
                'error': str(e),
                'timestamp': time.time(),
                'quality_score': 0.0
            })
            raise

    async def _analyze_repository(self, repo_path: str, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Análise específica do repositório baseada na tarefa
        """
        findings = []

        # Análise básica de estrutura
        structure_analysis = await self._analyze_structure(repo_path)
        if structure_analysis:
            findings.append({
                'type': 'structure',
                'data': structure_analysis,
                'relevance': self._calculate_relevance(structure_analysis, task)
            })

        # Análise de código se relevante
        if task.get('analyze_code', False):
            code_analysis = await self._analyze_code(repo_path, task)
            if code_analysis:
                findings.append({
                    'type': 'code',
                    'data': code_analysis,
                    'relevance': self._calculate_relevance(code_analysis, task)
                })

        # Busca de padrões específicos
        if 'patterns' in task:
            pattern_findings = await self._search_patterns(repo_path, task['patterns'])
            if pattern_findings:
                findings.append({
                    'type': 'patterns',
                    'data': pattern_findings,
                    'relevance': self._calculate_relevance(pattern_findings, task)
                })

        return findings

    async def _analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Análise básica da estrutura do repositório"""
        # Implementação simplificada - em produção seria mais robusta
        return {
            'path': repo_path,
            'has_readme': False,  # Verificar se existe README
            'has_tests': False,   # Verificar se existe diretório de testes
            'language': 'unknown' # Detectar linguagem principal
        }

    async def _analyze_code(self, repo_path: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Análise de código baseada na tarefa"""
        # Implementação simplificada
        return {
            'functions_found': [],
            'classes_found': [],
            'imports_analyzed': [],
            'complexity_score': 0.0
        }

    async def _search_patterns(self, repo_path: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Busca de padrões específicos"""
        # Implementação simplificada
        return []

    def _calculate_relevance(self, data: Dict[str, Any], task: Dict[str, Any]) -> float:
        """Calcula relevância dos achados para a tarefa"""
        # Implementação simplificada - score entre 0.0 e 1.0
        return 0.5

    async def _create_trails(self, findings: List[Dict[str, Any]], task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cria trilhas de reforço baseadas nos achados"""
        trails = []

        for finding in findings:
            trail = {
                'ant_id': self.ant_id,
                'task_type': task.get('type', 'unknown'),
                'finding_type': finding['type'],
                'relevance': finding['relevance'],
                'strength': finding['relevance'],  # Força da trilha baseada na relevância
                'timestamp': time.time(),
                'expires_at': time.time() + 3600  # Expira em 1 hora
            }
            trails.append(trail)

        return trails

    def _calculate_quality_score(self, findings: List[Dict[str, Any]], trails: List[Dict[str, Any]]) -> float:
        """Calcula score de qualidade da exploração"""
        if not findings:
            return 0.0

        # Score baseado na quantidade e qualidade dos achados
        relevance_sum = sum(f['relevance'] for f in findings)
        avg_relevance = relevance_sum / len(findings)

        # Bonus por diversidade de tipos
        unique_types = len(set(f['type'] for f in findings))
        diversity_bonus = min(unique_types * 0.1, 0.5)

        return min(avg_relevance + diversity_bonus, 1.0)

    async def start_exploration(self):
        """Inicia o ciclo de exploração da formiga"""
        self.active = True
        logger.info(f"Ant {self.ant_id} started exploration cycle")

        while self.active:
            try:
                # Aguardar tarefa do orquestrador
                task = await self.communication.receive_task()

                if task:
                    # Executar exploração
                    result = await self.explore_repository(task['repo_path'], task)

                    # Relatar resultado
                    await self.communication.report_result(result)

                else:
                    # Sem tarefa, aguardar
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Ant {self.ant_id} exploration cycle error: {e}")
                await asyncio.sleep(5)  # Backoff em caso de erro

    def stop_exploration(self):
        """Para o ciclo de exploração"""
        self.active = False
        logger.info(f"Ant {self.ant_id} stopped exploration cycle")