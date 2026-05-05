"""
Collective Memory - Memória Coletiva
===================================

Memória compartilhada entre agentes da colônia.
Características:
- Armazenamento de trilhas
- Compartilhamento de conhecimento
- Persistência de aprendizado
- Acesso concorrente seguro
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Entrada na memória coletiva"""
    key: str
    data: Any
    timestamp: float
    expires_at: Optional[float] = None
    access_count: int = 0
    last_access: float = 0.0

    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        return self.expires_at is not None and time.time() > self.expires_at

    def access(self):
        """Registra acesso à entrada"""
        self.access_count += 1
        self.last_access = time.time()

class CollectiveMemory:
    """
    Memória coletiva para compartilhamento entre agentes

    Funcionalidades:
    - Armazenamento de trilhas
    - Compartilhamento de tarefas
    - Relatórios de exploração
    - Persistência em disco
    """

    def __init__(self, storage_path: str = "collective_memory.json"):
        self.storage_path = storage_path
        self.memory: Dict[str, MemoryEntry] = {}
        self.lock = Lock()
        self.max_entries = 10000  # Limitar tamanho da memória
        self.cleanup_interval = 300  # Limpeza a cada 5 minutos

        # Carregar memória persistida
        self._load_memory()

        # Iniciar limpeza automática, se houver loop de evento em execução
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            logger.info("Nenhum loop de evento em execução; a limpeza periódica da memória será iniciada posteriormente")

        logger.info(f"CollectiveMemory initialized with {len(self.memory)} entries")

    def _load_memory(self):
        """Carrega memória do disco"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                for key, entry_data in data.items():
                    entry = MemoryEntry(
                        key=key,
                        data=entry_data['data'],
                        timestamp=entry_data['timestamp'],
                        expires_at=entry_data.get('expires_at'),
                        access_count=entry_data.get('access_count', 0),
                        last_access=entry_data.get('last_access', entry_data['timestamp'])
                    )
                    self.memory[key] = entry

                logger.info(f"Loaded {len(self.memory)} entries from {self.storage_path}")

            except Exception as e:
                logger.error(f"Failed to load memory: {e}")

    def _save_memory(self):
        """Salva memória no disco"""
        try:
            data = {}
            for key, entry in self.memory.items():
                if not entry.is_expired():
                    data[key] = {
                        'data': entry.data,
                        'timestamp': entry.timestamp,
                        'expires_at': entry.expires_at,
                        'access_count': entry.access_count,
                        'last_access': entry.last_access
                    }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    async def _periodic_cleanup(self):
        """Limpeza periódica de entradas expiradas"""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            self._cleanup_expired()

    def _cleanup_expired(self):
        """Remove entradas expiradas"""
        expired_keys = [key for key, entry in self.memory.items() if entry.is_expired()]

        for key in expired_keys:
            del self.memory[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

        # Salvar após limpeza
        self._save_memory()

    async def store_trail(self, trail_data: Dict[str, Any]):
        """
        Armazena uma trilha na memória

        Args:
            trail_data: Dados da trilha
        """
        key = f"trail_{trail_data['ant_id']}_{int(time.time() * 1000)}"

        entry = MemoryEntry(
            key=key,
            data=trail_data,
            timestamp=time.time(),
            expires_at=trail_data.get('expires_at')
        )

        with self.lock:
            self.memory[key] = entry

            # Limitar tamanho
            if len(self.memory) > self.max_entries:
                self._evict_old_entries()

        logger.debug(f"Stored trail: {key}")

    async def get_trails_by_type(self, task_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca trilhas por tipo de tarefa

        Args:
            task_type: Tipo de tarefa
            limit: Número máximo de resultados

        Returns:
            Lista de trilhas encontradas
        """
        trails = []

        with self.lock:
            for entry in self.memory.values():
                if entry.is_expired():
                    continue

                if (entry.data.get('type') == 'exploration_result' and
                    entry.data.get('data', {}).get('task_type') == task_type):
                    trails.append(entry.data)
                    entry.access()

        # Ordenar por relevância/timestamp
        trails.sort(key=lambda t: t.get('data', {}).get('quality_score', 0), reverse=True)

        return trails[:limit]

    async def store_task(self, task_data: Dict[str, Any]):
        """
        Armazena uma tarefa pendente

        Args:
            task_data: Dados da tarefa
        """
        key = f"task_{task_data['id']}"

        entry = MemoryEntry(
            key=key,
            data={**task_data, 'status': 'pending'},
            timestamp=time.time(),
            expires_at=time.time() + 3600  # Expira em 1 hora
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored task: {key}")

    async def get_pending_tasks(self, ant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca tarefas pendentes

        Args:
            ant_id: ID da formiga (opcional, para filtrar)

        Returns:
            Lista de tarefas pendentes
        """
        tasks = []

        with self.lock:
            for entry in self.memory.values():
                if entry.is_expired():
                    continue

                if (entry.data.get('type') == 'task' or entry.key.startswith('task_')):
                    if entry.data.get('status') == 'pending':
                        if ant_id is None or entry.data.get('assigned_ant') == ant_id:
                            tasks.append(entry.data)
                            entry.access()

        # Ordenar por timestamp (mais antigas primeiro)
        tasks.sort(key=lambda t: t.get('timestamp', 0))

        return tasks

    async def update_task_status(self, task_id: str, status: str, ant_id: Optional[str] = None):
        """
        Atualiza status de uma tarefa

        Args:
            task_id: ID da tarefa
            status: Novo status
            ant_id: ID da formiga que está processando
        """
        key = f"task_{task_id}"

        with self.lock:
            if key in self.memory:
                entry = self.memory[key]
                entry.data['status'] = status
                if ant_id:
                    entry.data['processing_ant'] = ant_id
                entry.data['status_updated'] = time.time()
                entry.access()

                logger.debug(f"Updated task {task_id} status to {status}")

    async def store_report(self, report_data: Dict[str, Any]):
        """
        Armazena um relatório de exploração

        Args:
            report_data: Dados do relatório
        """
        key = f"report_{report_data['ant_id']}_{int(time.time() * 1000)}"

        entry = MemoryEntry(
            key=key,
            data=report_data,
            timestamp=time.time(),
            expires_at=time.time() + 86400  # Expira em 24 horas
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored report: {key}")

    async def get_all_reports(self) -> List[Dict[str, Any]]:
        """Busca todos os relatórios disponíveis"""
        reports = []

        with self.lock:
            for entry in self.memory.values():
                if entry.is_expired():
                    continue

                if entry.data.get('type') == 'exploration_report':
                    reports.append(entry.data)
                    entry.access()

        return reports

    def _evict_old_entries(self):
        """Remove entradas antigas quando memória cheia"""
        # Ordenar por último acesso
        entries = sorted(self.memory.items(), key=lambda x: x[1].last_access)

        # Remover 10% das entradas mais antigas
        to_remove = len(entries) // 10
        for key, _ in entries[:to_remove]:
            del self.memory[key]

        logger.debug(f"Evicted {to_remove} old entries")

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        with self.lock:
            total_entries = len(self.memory)
            expired_entries = sum(1 for e in self.memory.values() if e.is_expired())
            trails = sum(1 for e in self.memory.values() if e.key.startswith('trail_'))
            tasks = sum(1 for e in self.memory.values() if e.key.startswith('task_'))
            reports = sum(1 for e in self.memory.values() if e.key.startswith('report_'))

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'trails': trails,
            'tasks': tasks,
            'reports': reports,
            'max_entries': self.max_entries
        }

    async def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna tarefas recentes"""
        tasks = []

        with self.lock:
            for entry in self.memory.values():
                if entry.is_expired():
                    continue
                if entry.key.startswith('task_'):
                    tasks.append(entry.data)
                    entry.access()

        tasks.sort(key=lambda t: t.get('timestamp', 0), reverse=True)
        return tasks[:limit]

    async def get_recent_data(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna dados recentes que não são apenas tarefas ou relatórios"""
        payloads = []

        with self.lock:
            for entry in self.memory.values():
                if entry.is_expired():
                    continue
                if not entry.key.startswith(('task_', 'report_', 'trail_', 'alert_', 'incident_', 'containment_', 'human_alert_', 'security_event_')):
                    payloads.append(entry.data)
                    entry.access()

        payloads.sort(key=lambda d: d.get('timestamp', 0), reverse=True)
        return payloads[:limit]

    async def store_security_event(self, event_data: Dict[str, Any]):
        """Armazena evento de segurança"""
        key = f"security_event_{event_data['event_id']}"
        entry = MemoryEntry(
            key=key,
            data={**event_data, 'type': 'security_event'},
            timestamp=time.time(),
            expires_at=time.time() + 86400
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored security event: {key}")

    async def update_security_event(self, event_id: str, updates: Dict[str, Any]):
        """Atualiza um evento de segurança existente"""
        key = f"security_event_{event_id}"
        with self.lock:
            if key in self.memory:
                entry = self.memory[key]
                entry.data.update(updates)
                entry.access()
                logger.debug(f"Updated security event: {key}")

    async def store_alert(self, alert_data: Dict[str, Any]):
        """Armazena alerta escalado"""
        alert_id = alert_data.get('alert_id') or f"alert_{int(time.time() * 1000)}"
        key = f"alert_{alert_id}"
        alert_record = {
            **alert_data,
            'type': 'alert',
            'escalated': alert_data.get('severity', 0) >= 3,
            'handled': alert_data.get('handled', False)
        }

        entry = MemoryEntry(
            key=key,
            data=alert_record,
            timestamp=time.time(),
            expires_at=time.time() + 86400
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored alert: {key}")

    async def get_escalated_alerts(self, min_risk_level: int = 3) -> List[Dict[str, Any]]:
        """Retorna alertas escalados que ainda não foram tratados"""
        alerts = []

        with self.lock:
            for entry in self.memory.values():
                if entry.is_expired():
                    continue
                if entry.data.get('type') == 'alert':
                    if not entry.data.get('handled', False) and entry.data.get('severity', 0) >= min_risk_level:
                        alerts.append(entry.data)
                        entry.access()

        return alerts

    async def store_incident(self, incident_data: Dict[str, Any]):
        """Armazena incidente"""
        key = f"incident_{incident_data.get('incident_id', int(time.time() * 1000))}"
        entry = MemoryEntry(
            key=key,
            data={**incident_data, 'type': 'incident'},
            timestamp=time.time(),
            expires_at=time.time() + 86400
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored incident: {key}")

    async def store_containment_result(self, result_data: Dict[str, Any]):
        """Armazena resultado de contenção"""
        key = f"containment_{result_data.get('action_id', int(time.time() * 1000))}"
        entry = MemoryEntry(
            key=key,
            data={**result_data, 'type': 'containment_result'},
            timestamp=time.time(),
            expires_at=time.time() + 86400
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored containment result: {key}")

    async def store_human_alert(self, alert_data: Dict[str, Any]):
        """Armazena alerta humano"""
        key = f"human_alert_{alert_data.get('alert_id', int(time.time() * 1000))}"
        entry = MemoryEntry(
            key=key,
            data={**alert_data, 'type': 'human_alert'},
            timestamp=time.time(),
            expires_at=time.time() + 86400
        )

        with self.lock:
            self.memory[key] = entry

        logger.debug(f"Stored human alert: {key}")

    async def update_alert_status(self, alert_id: str, handled: bool = True):
        """Atualiza o status de um alerta escalado"""
        key = f"alert_{alert_id}"
        with self.lock:
            if key in self.memory:
                entry = self.memory[key]
                entry.data['handled'] = handled
                entry.access()
                logger.debug(f"Updated alert status: {key}")

    async def cleanup_security_events(self, max_age: float = 86400):
        """Remove eventos de segurança antigos"""
        cutoff = time.time() - max_age
        with self.lock:
            for key in list(self.memory.keys()):
                if key.startswith('security_event_'):
                    entry = self.memory[key]
                    if entry.timestamp < cutoff:
                        del self.memory[key]
                        logger.debug(f"Cleaned up security event: {key}")

        self._save_memory()

    async def clear_memory(self):
        """Limpa toda a memória (usar com cuidado)"""
        with self.lock:
            self.memory.clear()
            self._save_memory()

        logger.warning("Memory cleared")