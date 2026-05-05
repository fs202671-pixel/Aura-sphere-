"""
Ant Coordinator - Coordenador de Formigas
=========================================

Gerencia um enxame de formigas exploradoras.
Características:
- Controle de população de formigas
- Distribuição de tarefas
- Coleta de resultados
- Otimização de exploração
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

from .explorer import AntExplorer
from .communication import AntCommunication
from .trails import TrailSystem
from core.security import SecurityManager

logger = logging.getLogger(__name__)

class AntCoordinator:
    """
    Coordenador do enxame de formigas

    Funcionalidades:
    - Gerenciar população de formigas
    - Distribuir tarefas de exploração
    - Coletar e analisar resultados
    - Otimizar estratégias de exploração
    """

    def __init__(self, max_ants: int = 10):
        self.max_ants = max_ants
        self.active_ants: Dict[str, AntExplorer] = {}
        self.ant_tasks: Dict[str, asyncio.Task] = {}
        self.trail_system = TrailSystem()
        self.security = SecurityManager()

        # Executor para paralelismo controlado
        self.executor = ThreadPoolExecutor(max_workers=max_ants)

        logger.info(f"AntCoordinator initialized with max {max_ants} ants")

    async def spawn_ant(self, ant_id: Optional[str] = None) -> str:
        """
        Cria uma nova formiga exploradora

        Args:
            ant_id: ID opcional para a formiga

        Returns:
            ID da formiga criada
        """
        if len(self.active_ants) >= self.max_ants:
            raise RuntimeError(f"Maximum ant limit reached ({self.max_ants})")

        ant_id = ant_id or f"ant_{uuid.uuid4().hex[:8]}"
        ant = AntExplorer(ant_id)

        # Configurar comunicação
        ant.communication.set_ant_id(ant_id)

        self.active_ants[ant_id] = ant

        # Iniciar ciclo de exploração
        task = asyncio.create_task(self._ant_lifecycle(ant))
        self.ant_tasks[ant_id] = task

        logger.info(f"Spawned ant {ant_id}")
        return ant_id

    async def _ant_lifecycle(self, ant: AntExplorer):
        """Ciclo de vida de uma formiga"""
        try:
            await ant.start_exploration()
        except Exception as e:
            logger.error(f"Ant {ant.ant_id} lifecycle error: {e}")
        finally:
            # Cleanup quando a formiga termina
            if ant.ant_id in self.active_ants:
                del self.active_ants[ant.ant_id]
            if ant.ant_id in self.ant_tasks:
                del self.ant_tasks[ant.ant_id]
            logger.info(f"Ant {ant.ant_id} lifecycle ended")

    async def assign_exploration_task(self, repo_path: str, task_config: Dict[str, Any]) -> List[str]:
        """
        Atribui tarefa de exploração para múltiplas formigas

        Args:
            repo_path: Caminho do repositório
            task_config: Configuração da tarefa

        Returns:
            Lista de IDs das formigas designadas
        """
        # Determinar número de formigas baseado na complexidade
        complexity = self._estimate_complexity(task_config)
        ant_count = min(max(1, complexity // 2), len(self.active_ants))

        if ant_count > len(self.active_ants):
            # Spawn mais formigas se necessário
            needed = ant_count - len(self.active_ants)
            for _ in range(needed):
                await self.spawn_ant()

        # Selecionar formigas disponíveis
        available_ants = list(self.active_ants.keys())[:ant_count]

        # Distribuir tarefa para cada formiga
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        for ant_id in available_ants:
            task_data = {
                'id': f"{task_id}_{ant_id}",
                'repo_path': repo_path,
                'config': task_config,
                'assigned_ant': ant_id,
                'timestamp': asyncio.get_event_loop().time()
            }

            # Enviar tarefa via comunicação
            await self.active_ants[ant_id].communication.memory.store_task(task_data)

        logger.info(f"Assigned exploration task {task_id} to {len(available_ants)} ants")
        return available_ants

    def _estimate_complexity(self, task_config: Dict[str, Any]) -> int:
        """Estima complexidade da tarefa para determinar número de formigas"""
        complexity = 1

        # Fatores de complexidade
        if task_config.get('analyze_code', False):
            complexity += 2

        if 'patterns' in task_config:
            complexity += len(task_config['patterns'])

        if task_config.get('deep_analysis', False):
            complexity += 3

        return min(complexity, 10)  # Limitar complexidade máxima

    async def collect_results(self, task_id: str, timeout: float = 30.0) -> List[Dict[str, Any]]:
        """
        Coleta resultados de uma tarefa de exploração

        Args:
            task_id: ID da tarefa
            timeout: Tempo limite para coleta

        Returns:
            Lista de resultados coletados
        """
        start_time = asyncio.get_event_loop().time()
        results = []

        while asyncio.get_event_loop().time() - start_time < timeout:
            # Buscar resultados na memória coletiva
            task_results = await self._gather_task_results(task_id)

            if task_results:
                results.extend(task_results)

                # Verificar se todos os resultados foram coletados
                expected_ants = len([aid for aid in self.active_ants.keys() if f"{task_id}_{aid}" in [r.get('task_id') for r in results]])
                if len(results) >= expected_ants:
                    break

            await asyncio.sleep(0.5)

        # Processar e agregar resultados
        aggregated_results = self._aggregate_results(results)

        logger.info(f"Collected {len(results)} results for task {task_id}")
        return aggregated_results

    async def _gather_task_results(self, task_id: str) -> List[Dict[str, Any]]:
        """Coleta resultados específicos de uma tarefa"""
        # Buscar na memória coletiva
        all_reports = await self.active_ants[list(self.active_ants.keys())[0]].communication.memory.get_all_reports()

        task_reports = [
            report for report in all_reports
            if report.get('result', {}).get('task_id', '').startswith(task_id)
        ]

        return [report['result'] for report in task_reports]

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Agrega resultados de múltiplas formigas"""
        if not results:
            return []

        # Agrupar por tipo de achado
        aggregated = {}

        for result in results:
            for finding in result.get('findings', []):
                finding_type = finding['type']

                if finding_type not in aggregated:
                    aggregated[finding_type] = {
                        'type': finding_type,
                        'total_findings': 0,
                        'avg_relevance': 0.0,
                        'sources': [],
                        'consensus_data': {}
                    }

                # Agregar dados
                aggregated[finding_type]['total_findings'] += 1
                aggregated[finding_type]['avg_relevance'] += finding['relevance']
                aggregated[finding_type]['sources'].append(result['ant_id'])

                # Mesclar dados de consenso
                self._merge_consensus_data(aggregated[finding_type]['consensus_data'], finding['data'])

        # Calcular médias e finalizar
        for agg in aggregated.values():
            if agg['total_findings'] > 0:
                agg['avg_relevance'] /= agg['total_findings']
            agg['confidence'] = min(agg['total_findings'] / len(results), 1.0)

        return list(aggregated.values())

    def _merge_consensus_data(self, consensus: Dict[str, Any], new_data: Dict[str, Any]):
        """Mescla dados para formar consenso"""
        for key, value in new_data.items():
            if key not in consensus:
                consensus[key] = value
            elif isinstance(value, list):
                if not isinstance(consensus[key], list):
                    consensus[key] = [consensus[key]]
                consensus[key].extend(value)
            elif isinstance(value, dict):
                if not isinstance(consensus[key], dict):
                    consensus[key] = {}
                self._merge_consensus_data(consensus[key], value)
            else:
                # Para valores simples, manter o último (poderia ser média/voto)
                consensus[key] = value

    async def explore_subtask(self, subtask: Dict[str, Any], user_command: str) -> List[Dict[str, Any]]:
        """
        Explora uma subtarefa específica usando formigas

        Args:
            subtask: Configuração da subtarefa
            user_command: Comando original do usuário

        Returns:
            Lista de resultados da exploração
        """
        try:
            # Converter subtarefa para formato de tarefa de exploração
            task_config = {
                "type": subtask.get("type", "general_exploration"),
                "description": subtask.get("description", ""),
                "user_command": user_command,
                "analyze_code": True,
                "patterns": [subtask.get("type", "general")],
                "deep_analysis": subtask.get("type") in ["analyze_content", "gather_intelligence"]
            }

            # Usar repositório atual como alvo (pode ser parametrizado)
            repo_path = "."  # repositório atual

            # Atribuir tarefa para formigas
            ant_ids = await self.assign_exploration_task(repo_path, task_config)

            if not ant_ids:
                logger.warning("No ants available for exploration")
                return []

            # Aguardar e coletar resultados
            task_id = f"subtask_{uuid.uuid4().hex[:8]}"
            results = await self.collect_results(task_id, timeout=15.0)

            # Adicionar metadados
            for result in results:
                result["ant_id"] = ant_ids[0] if ant_ids else "unknown"
                result["subtask_type"] = subtask.get("type")
                result["user_command"] = user_command

            logger.info(f"Explored subtask {subtask.get('type')} with {len(results)} findings")
            return results

        except Exception as e:
            logger.error(f"Error exploring subtask: {e}")
            return [{"error": str(e), "ant_id": "error", "subtask_type": subtask.get("type")}]

    async def optimize_exploration(self):
        """Otimiza estratégias de exploração baseadas em performance"""
        # Evaporar trilhas antigas
        self.trail_system.evaporate_trails()
        self.trail_system.cleanup_expired_trails()

        # Analisar padrões
        analysis = self.trail_system.analyze_trail_patterns()

        # Ajustar população de formigas baseada na análise
        await self._adjust_population(analysis)

        # Reforçar caminhos bem-sucedidos
        await self._reinforce_successful_paths(analysis)

        logger.info("Exploration optimization completed")

    async def _adjust_population(self, analysis: Dict[str, Any]):
        """Ajusta população de formigas baseada na análise"""
        current_population = len(self.active_ants)

        # Lógica de ajuste baseada em padrões emergentes
        emerging_patterns = len(analysis.get('emerging_patterns', []))

        if emerging_patterns > 3:
            # Muitos padrões - aumentar exploração
            target_population = min(current_population + 2, self.max_ants)
        elif emerging_patterns < 1:
            # Poucos padrões - reduzir exploração
            target_population = max(current_population - 1, 1)
        else:
            target_population = current_population

        # Ajustar população
        while len(self.active_ants) < target_population:
            await self.spawn_ant()

        # Não reduzir população aqui - deixar morrer naturalmente

    async def _reinforce_successful_paths(self, analysis: Dict[str, Any]):
        """Reforça caminhos bem-sucedidos"""
        for pattern in analysis.get('emerging_patterns', []):
            target_type = pattern['type']
            confidence = pattern['confidence']

            # Reforçar trilha
            self.trail_system.reinforce_trail(target_type, confidence * 0.1)

    async def get_swarm_status(self) -> Dict[str, Any]:
        """Retorna status atual do enxame"""
        return {
            'active_ants': len(self.active_ants),
            'max_ants': self.max_ants,
            'trail_types': len(self.trail_system.trails),
            'total_trails': sum(len(trails) for trails in self.trail_system.trails.values()),
            'ant_ids': list(self.active_ants.keys())
        }

    async def shutdown(self):
        """Desliga o coordenador e todas as formigas"""
        logger.info("Shutting down AntCoordinator")

        # Parar todas as formigas
        for ant in self.active_ants.values():
            ant.stop_exploration()

        # Aguardar tarefas terminarem
        if self.ant_tasks:
            await asyncio.gather(*self.ant_tasks.values(), return_exceptions=True)

        # Limpar estado
        self.active_ants.clear()
        self.ant_tasks.clear()

        # Persistir trilhas se necessário
        trail_data = self.trail_system.export_trails()
        # TODO: Salvar em arquivo ou banco

        logger.info("AntCoordinator shutdown complete")