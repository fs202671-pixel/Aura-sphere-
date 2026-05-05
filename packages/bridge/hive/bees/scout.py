"""
Bee Scout - Abelha Batedora
===========================

Agente que recebe e processa dados das formigas exploradoras.
Características:
- Coleta de dados de exploração
- Filtragem e validação inicial
- Preparação para processamento
- Comunicação com coordenadores
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from memory.collective import CollectiveMemory
from core.security import SecurityManager

logger = logging.getLogger(__name__)

@dataclass
class ProcessedData:
    """Dados processados de exploração"""
    source_ant: str
    data_type: str
    processed_data: Dict[str, Any]
    quality_score: float
    timestamp: float
    validation_status: str

class BeeScout:
    """
    Abelha batedora - interface entre exploração e organização

    Funcionalidades:
    - Monitorar resultados de exploração
    - Validar e filtrar dados
    - Preparar dados para processamento
    - Comunicar com coordenadores
    """

    def __init__(self, scout_id: Optional[str] = None):
        self.scout_id = scout_id or f"scout_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()
        self.active = False
        self.processed_count = 0

        logger.info(f"BeeScout {self.scout_id} initialized")

    async def start_scouting(self):
        """Inicia o ciclo de reconhecimento"""
        self.active = True
        logger.info(f"BeeScout {self.scout_id} started scouting")

        while self.active:
            try:
                # Buscar novos dados de exploração
                exploration_data = await self._collect_exploration_data()

                if exploration_data:
                    # Processar dados coletados
                    processed_data = await self._process_exploration_data(exploration_data)

                    # Enviar para coordenadores
                    await self._send_to_coordinators(processed_data)

                    self.processed_count += len(processed_data)

                # Aguardar antes da próxima coleta
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"BeeScout {self.scout_id} error: {e}")
                await asyncio.sleep(5)

    async def _collect_exploration_data(self) -> List[Dict[str, Any]]:
        """
        Coleta dados de exploração das formigas

        Returns:
            Lista de dados de exploração não processados
        """
        # Buscar relatórios de exploração na memória coletiva
        reports = await self.memory.get_all_reports()

        # Filtrar apenas dados novos (não processados por este scout)
        new_data = []
        for report in reports:
            if self._is_new_data(report):
                new_data.append(report)

        return new_data

    def _is_new_data(self, report: Dict[str, Any]) -> bool:
        """Verifica se os dados são novos para este scout"""
        # Implementação simplificada - em produção usaria timestamps e IDs
        processed_key = f"processed_{self.scout_id}_{report.get('ant_id', 'unknown')}"
        # TODO: Verificar se já foi processado
        return True

    async def _process_exploration_data(self, raw_data: List[Dict[str, Any]]) -> List[ProcessedData]:
        """
        Processa dados brutos de exploração

        Args:
            raw_data: Dados brutos das formigas

        Returns:
            Dados processados e validados
        """
        processed_data = []

        for data in raw_data:
            try:
                # Validar segurança dos dados
                if not await self._validate_data_security(data):
                    logger.warning(f"Data from ant {data.get('ant_id')} failed security validation")
                    continue

                # Processar dados específicos
                processed = await self._extract_findings(data)

                # Calcular qualidade
                quality_score = self._assess_data_quality(processed)

                # Criar objeto processado
                processed_obj = ProcessedData(
                    source_ant=data.get('ant_id', 'unknown'),
                    data_type=data.get('type', 'unknown'),
                    processed_data=processed,
                    quality_score=quality_score,
                    timestamp=time.time(),
                    validation_status='valid'
                )

                processed_data.append(processed_obj)

            except Exception as e:
                logger.error(f"Failed to process data from ant {data.get('ant_id')}: {e}")

        return processed_data

    async def _validate_data_security(self, data: Dict[str, Any]) -> bool:
        """
        Valida segurança dos dados recebidos

        Args:
            data: Dados a validar

        Returns:
            True se seguro, False caso contrário
        """
        # Verificar se os dados vêm de uma fonte autorizada
        ant_id = data.get('ant_id')
        if not ant_id:
            return False

        # Verificar integridade dos dados
        # TODO: Implementar verificação de assinatura ou hash

        # Verificar se não contém código malicioso
        data_str = str(data)
        dangerous_patterns = ['exec(', 'eval(', 'import os', 'subprocess']

        for pattern in dangerous_patterns:
            if pattern in data_str:
                logger.warning(f"Dangerous pattern detected in data from {ant_id}: {pattern}")
                return False

        return True

    async def _extract_findings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai achados relevantes dos dados brutos

        Args:
            data: Dados brutos

        Returns:
            Achados extraídos e estruturados
        """
        result = data.get('result', {})
        findings = result.get('findings', [])

        # Estruturar achados por tipo
        structured_findings = {
            'structure_findings': [],
            'code_findings': [],
            'pattern_findings': [],
            'summary': {
                'total_findings': len(findings),
                'types_found': set(),
                'avg_relevance': 0.0
            }
        }

        total_relevance = 0.0

        for finding in findings:
            finding_type = finding.get('type', 'unknown')
            structured_findings['summary']['types_found'].add(finding_type)

            # Categorizar achado
            if finding_type == 'structure':
                structured_findings['structure_findings'].append(finding)
            elif finding_type == 'code':
                structured_findings['code_findings'].append(finding)
            elif finding_type == 'patterns':
                structured_findings['pattern_findings'].append(finding)

            total_relevance += finding.get('relevance', 0.0)

        # Calcular média de relevância
        if findings:
            structured_findings['summary']['avg_relevance'] = total_relevance / len(findings)

        return structured_findings

    def _assess_data_quality(self, processed_data: Dict[str, Any]) -> float:
        """
        Avalia qualidade dos dados processados

        Args:
            processed_data: Dados processados

        Returns:
            Score de qualidade (0.0 a 1.0)
        """
        summary = processed_data.get('summary', {})
        quality_score = 0.0

        # Fatores de qualidade
        total_findings = summary.get('total_findings', 0)
        avg_relevance = summary.get('avg_relevance', 0.0)
        types_count = len(summary.get('types_found', set()))

        # Score baseado na quantidade de achados
        if total_findings > 0:
            quality_score += min(total_findings / 10, 0.4)  # Até 0.4 por volume

        # Score baseado na relevância média
        quality_score += avg_relevance * 0.4  # Até 0.4 por relevância

        # Score baseado na diversidade de tipos
        quality_score += min(types_count / 5, 0.2)  # Até 0.2 por diversidade

        return min(quality_score, 1.0)

    async def _send_to_coordinators(self, processed_data: List[ProcessedData]):
        """
        Envia dados processados para os coordenadores

        Args:
            processed_data: Dados a enviar
        """
        # Armazenar na memória coletiva para coordenadores
        for data in processed_data:
            task_data = {
                'type': 'scout_report',
                'scout_id': self.scout_id,
                'source_ant': data.source_ant,
                'data_type': data.data_type,
                'processed_data': data.processed_data,
                'quality_score': data.quality_score,
                'timestamp': data.timestamp,
                'validation_status': data.validation_status
            }

            await self.memory.store_task(task_data)

        if processed_data:
            logger.info(f"BeeScout {self.scout_id} sent {len(processed_data)} reports to coordinators")

    async def get_scout_status(self) -> Dict[str, Any]:
        """Retorna status do scout"""
        return {
            'scout_id': self.scout_id,
            'active': self.active,
            'processed_count': self.processed_count,
            'uptime': time.time() - (time.time() - 0)  # TODO: track start time
        }

    def stop_scouting(self):
        """Para o ciclo de reconhecimento"""
        self.active = False
        logger.info(f"BeeScout {self.scout_id} stopped scouting")