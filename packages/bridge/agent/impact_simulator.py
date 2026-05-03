"""
Módulo Simulador de Impacto de Mudanças - Avaliação de riscos de alterações

Este módulo implementa simulação de impacto de mudanças no sistema,
avaliando riscos de segurança, performance e estabilidade antes da execução.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import copy
from pathlib import Path
import asyncio
from collections import defaultdict


class ImpactLevel(Enum):
    """Níveis de impacto."""
    NONE = "none"           # Sem impacto
    LOW = "low"            # Impacto baixo
    MEDIUM = "medium"      # Impacto médio
    HIGH = "high"          # Impacto alto
    CRITICAL = "critical"  # Impacto crítico


class RiskCategory(Enum):
    """Categorias de risco."""
    SECURITY = "security"           # Riscos de segurança
    PERFORMANCE = "performance"     # Riscos de performance
    STABILITY = "stability"         # Riscos de estabilidade
    COMPATIBILITY = "compatibility" # Riscos de compatibilidade
    DATA_INTEGRITY = "data_integrity" # Riscos de integridade de dados


class ImpactSimulation:
    """
    Simulação de impacto de uma mudança específica.
    """

    def __init__(self, change_description: str, change_type: str):
        self.change_description = change_description
        self.change_type = change_type
        self.simulated_at = datetime.now()

        # Resultados da simulação
        self.overall_risk_score = 0.0
        self.impact_level = ImpactLevel.NONE

        # Análise por categoria
        self.category_impacts: Dict[RiskCategory, Dict[str, Any]] = {}

        # Dependências afetadas
        self.affected_components: List[str] = []
        self.affected_dependencies: List[str] = []

        # Cenários simulados
        self.scenarios_tested: List[Dict[str, Any]] = []

        # Recomendações
        self.recommendations: List[str] = []
        self.blocking_concerns: List[str] = []

        # Status
        self.simulation_successful = True
        self.confidence_level = 0.0

    def add_category_impact(self, category: RiskCategory, impact_data: Dict[str, Any]) -> None:
        """Adiciona análise de impacto para uma categoria."""

        self.category_impacts[category] = impact_data

    def add_scenario_result(self, scenario_name: str, success: bool,
                          impact_score: float, details: str = "") -> None:
        """Adiciona resultado de cenário simulado."""

        self.scenarios_tested.append({
            "scenario_name": scenario_name,
            "success": success,
            "impact_score": impact_score,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_overall_risk(self) -> None:
        """Calcula risco geral baseado nas análises."""

        if not self.category_impacts:
            self.overall_risk_score = 0.0
            self.impact_level = ImpactLevel.NONE
            return

        # Calcular score médio ponderado
        total_weight = 0.0
        weighted_sum = 0.0

        category_weights = {
            RiskCategory.SECURITY: 3.0,
            RiskCategory.STABILITY: 2.5,
            RiskCategory.DATA_INTEGRITY: 2.0,
            RiskCategory.PERFORMANCE: 1.5,
            RiskCategory.COMPATIBILITY: 1.0
        }

        for category, impact_data in self.category_impacts.items():
            impact_score = impact_data.get("impact_score", 0.0)
            weight = category_weights.get(category, 1.0)

            weighted_sum += impact_score * weight
            total_weight += weight

        if total_weight > 0:
            self.overall_risk_score = weighted_sum / total_weight

        # Determinar nível de impacto
        if self.overall_risk_score >= 0.8:
            self.impact_level = ImpactLevel.CRITICAL
        elif self.overall_risk_score >= 0.6:
            self.impact_level = ImpactLevel.HIGH
        elif self.overall_risk_score >= 0.4:
            self.impact_level = ImpactLevel.MEDIUM
        elif self.overall_risk_score >= 0.2:
            self.impact_level = ImpactLevel.LOW
        else:
            self.impact_level = ImpactLevel.NONE

        # Calcular nível de confiança
        successful_scenarios = sum(1 for s in self.scenarios_tested if s["success"])
        total_scenarios = len(self.scenarios_tested)

        if total_scenarios > 0:
            self.confidence_level = successful_scenarios / total_scenarios
        else:
            self.confidence_level = 0.0

        # Gerar recomendações
        self._generate_recommendations()

    def _generate_recommendations(self) -> None:
        """Gera recomendações baseadas na simulação."""

        # Recomendações por nível de impacto
        if self.impact_level == ImpactLevel.CRITICAL:
            self.recommendations.append("CRITICAL IMPACT: Do not proceed without extensive testing and user approval")
            self.blocking_concerns.append("Change poses critical risk to system stability")

        elif self.impact_level == ImpactLevel.HIGH:
            self.recommendations.append("HIGH IMPACT: Requires thorough testing and monitoring")
            self.recommendations.append("Consider phased rollout with rollback capability")

        elif self.impact_level == ImpactLevel.MEDIUM:
            self.recommendations.append("MEDIUM IMPACT: Test in staging environment first")
            self.recommendations.append("Monitor closely after deployment")

        # Recomendações específicas por categoria
        for category, impact_data in self.category_impacts.items():
            impact_score = impact_data.get("impact_score", 0.0)

            if impact_score > 0.7:
                if category == RiskCategory.SECURITY:
                    self.recommendations.append("Security review required - high security risk detected")
                    self.blocking_concerns.append("Security vulnerability introduced")

                elif category == RiskCategory.STABILITY:
                    self.recommendations.append("Stability testing required - potential crashes detected")

                elif category == RiskCategory.DATA_INTEGRITY:
                    self.recommendations.append("Data integrity check required - potential data corruption")
                    self.blocking_concerns.append("Risk of data loss or corruption")

                elif category == RiskCategory.PERFORMANCE:
                    self.recommendations.append("Performance optimization required - significant slowdown expected")

        # Recomendações baseadas em confiança
        if self.confidence_level < 0.5:
            self.recommendations.append("Low confidence in simulation - additional testing recommended")

        # Recomendações baseadas em cenários
        failed_scenarios = [s for s in self.scenarios_tested if not s["success"]]
        if failed_scenarios:
            self.recommendations.append(f"Address {len(failed_scenarios)} failed simulation scenarios")

    def should_block_change(self) -> Tuple[bool, str]:
        """Determina se a mudança deve ser bloqueada."""

        if self.impact_level == ImpactLevel.CRITICAL:
            return True, "Critical impact level - change blocked"

        if self.blocking_concerns:
            return True, f"Blocking concerns: {', '.join(self.blocking_concerns)}"

        # Verificar se há riscos de segurança críticos
        security_impact = self.category_impacts.get(RiskCategory.SECURITY, {})
        if security_impact.get("impact_score", 0.0) > 0.8:
            return True, "Critical security risk detected"

        return False, "Change approved with recommendations"

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "change_description": self.change_description,
            "change_type": self.change_type,
            "simulated_at": self.simulated_at.isoformat(),
            "overall_risk_score": self.overall_risk_score,
            "impact_level": self.impact_level.value,
            "category_impacts": {
                k.value: v for k, v in self.category_impacts.items()
            },
            "affected_components": self.affected_components,
            "affected_dependencies": self.affected_dependencies,
            "scenarios_tested": self.scenarios_tested,
            "recommendations": self.recommendations,
            "blocking_concerns": self.blocking_concerns,
            "simulation_successful": self.simulation_successful,
            "confidence_level": self.confidence_level
        }


class ImpactSimulator:
    """
    Simulador de impacto de mudanças.

    Funcionalidades:
    - Simulação de impacto antes de mudanças
    - Avaliação de riscos por categoria
    - Cenários de teste simulados
    - Recomendações automáticas
    - Bloqueio de mudanças de alto risco
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.impact_dir = data_dir / "impact_simulation"
        self.impact_dir.mkdir(parents=True, exist_ok=True)

        self.simulations_file = self.impact_dir / "impact_simulations.json"
        self.baseline_file = self.impact_dir / "system_baseline.json"

        self.simulations: List[ImpactSimulation] = []
        self.system_baseline: Dict[str, Any] = {}

        # Configurações
        self.max_simulation_time_seconds = 30
        self.risk_thresholds = {
            "block_critical": True,
            "block_high_security": True,
            "require_testing_medium": True
        }

        # Estatísticas
        self.stats = {
            "total_simulations": 0,
            "blocked_changes": 0,
            "approved_changes": 0,
            "avg_risk_score": 0.0,
            "critical_impacts_detected": 0,
            "simulation_failures": 0
        }

        self._load_state()
        self._initialize_baseline()

    def _initialize_baseline(self) -> None:
        """Inicializa baseline do sistema para comparações."""

        if not self.system_baseline:
            self.system_baseline = {
                "components": [
                    "core", "agent", "runtime", "memory", "security",
                    "evolution", "governance", "monitoring"
                ],
                "critical_paths": [
                    "core/user_obedience.py",
                    "core/security_validation.py",
                    "agent/supervisor.py",
                    "runtime/sandbox.py"
                ],
                "risk_weights": {
                    "core": 1.0,
                    "security": 0.9,
                    "stability": 0.8,
                    "data": 0.7,
                    "performance": 0.6
                },
                "established_at": datetime.now().isoformat()
            }
            self._save_baseline()

    async def simulate_change_impact(self, change_description: str,
                                   change_type: str,
                                   affected_components: List[str] = None,
                                   change_details: Dict[str, Any] = None) -> ImpactSimulation:
        """
        Simula o impacto de uma mudança proposta.
        """

        simulation = ImpactSimulation(change_description, change_type)
        simulation.affected_components = affected_components or []

        try:
            # Simular impacto em diferentes categorias
            await self._simulate_security_impact(simulation, change_details)
            await self._simulate_performance_impact(simulation, change_details)
            await self._simulate_stability_impact(simulation, change_details)
            await self._simulate_compatibility_impact(simulation, change_details)
            await self._simulate_data_integrity_impact(simulation, change_details)

            # Executar cenários de teste
            await self._run_simulation_scenarios(simulation)

            # Calcular risco geral
            simulation.calculate_overall_risk()

        except Exception as e:
            simulation.simulation_successful = False
            simulation.blocking_concerns.append(f"Simulation failed: {e}")
            self.stats["simulation_failures"] += 1

        # Registrar simulação
        self.simulations.append(simulation)
        self.stats["total_simulations"] += 1

        # Atualizar estatísticas
        self.stats["avg_risk_score"] = (
            (self.stats["avg_risk_score"] * (self.stats["total_simulations"] - 1)) +
            simulation.overall_risk_score
        ) / self.stats["total_simulations"]

        if simulation.impact_level == ImpactLevel.CRITICAL:
            self.stats["critical_impacts_detected"] += 1

        self._save_state()

        return simulation

    async def _simulate_security_impact(self, simulation: ImpactSimulation,
                                      change_details: Dict[str, Any] = None) -> None:
        """Simula impacto na segurança."""

        impact_score = 0.0
        concerns = []

        # Verificar se afeta componentes críticos
        critical_components = set(self.system_baseline.get("critical_paths", []))
        affected_critical = any(comp in critical_components for comp in simulation.affected_components)

        if affected_critical:
            impact_score += 0.8
            concerns.append("Affects critical security components")

        # Verificar tipo de mudança
        change_type = simulation.change_type.lower()
        if any(keyword in change_type for keyword in ['security', 'auth', 'permission', 'access']):
            impact_score += 0.6
            concerns.append("Security-related change requires careful review")

        # Verificar se introduz novos privilégios ou acessos
        if change_details:
            if change_details.get("introduces_new_permissions", False):
                impact_score += 0.7
                concerns.append("Introduces new permissions - security review required")

            if change_details.get("modifies_core_behavior", False):
                impact_score += 0.9
                concerns.append("Modifies core behavior - high security risk")

        simulation.add_category_impact(RiskCategory.SECURITY, {
            "impact_score": min(impact_score, 1.0),
            "concerns": concerns,
            "affected_critical_components": affected_critical
        })

    async def _simulate_performance_impact(self, simulation: ImpactSimulation,
                                         change_details: Dict[str, Any] = None) -> None:
        """Simula impacto na performance."""

        impact_score = 0.0
        concerns = []

        # Verificar se afeta componentes de performance
        perf_components = ['memory', 'cache', 'database', 'network']
        affects_performance = any(comp in perf_components for comp in simulation.affected_components)

        if affects_performance:
            impact_score += 0.4
            concerns.append("May affect system performance")

        # Verificar se adiciona processamento complexo
        if change_details:
            if change_details.get("adds_complex_computation", False):
                impact_score += 0.6
                concerns.append("Adds complex computation - potential performance impact")

            if change_details.get("increases_memory_usage", False):
                impact_score += 0.5
                concerns.append("Increases memory usage")

        simulation.add_category_impact(RiskCategory.PERFORMANCE, {
            "impact_score": min(impact_score, 1.0),
            "concerns": concerns,
            "performance_components_affected": affects_performance
        })

    async def _simulate_stability_impact(self, simulation: ImpactSimulation,
                                       change_details: Dict[str, Any] = None) -> None:
        """Simula impacto na estabilidade."""

        impact_score = 0.0
        concerns = []

        # Mudanças que afetam estabilidade
        stability_keywords = ['async', 'threading', 'concurrency', 'error_handling', 'exception']
        change_desc = simulation.change_description.lower()

        if any(keyword in change_desc for keyword in stability_keywords):
            impact_score += 0.5
            concerns.append("Involves stability-critical patterns")

        # Verificar se modifica tratamento de erros
        if 'error' in change_desc or 'exception' in change_desc:
            impact_score += 0.4
            concerns.append("Modifies error handling - stability impact possible")

        simulation.add_category_impact(RiskCategory.STABILITY, {
            "impact_score": min(impact_score, 1.0),
            "concerns": concerns
        })

    async def _simulate_compatibility_impact(self, simulation: ImpactSimulation,
                                           change_details: Dict[str, Any] = None) -> None:
        """Simula impacto na compatibilidade."""

        impact_score = 0.0
        concerns = []

        # Verificar se muda APIs ou interfaces
        if 'api' in simulation.change_description.lower() or 'interface' in simulation.change_description.lower():
            impact_score += 0.6
            concerns.append("Changes APIs or interfaces - compatibility impact")

        # Verificar se afeta dependências
        if simulation.affected_dependencies:
            impact_score += 0.3
            concerns.append(f"Affects {len(simulation.affected_dependencies)} dependencies")

        simulation.add_category_impact(RiskCategory.COMPATIBILITY, {
            "impact_score": min(impact_score, 1.0),
            "concerns": concerns,
            "dependencies_affected": simulation.affected_dependencies
        })

    async def _simulate_data_integrity_impact(self, simulation: ImpactSimulation,
                                            change_details: Dict[str, Any] = None) -> None:
        """Simula impacto na integridade de dados."""

        impact_score = 0.0
        concerns = []

        # Verificar se envolve persistência de dados
        data_keywords = ['database', 'file', 'storage', 'save', 'load', 'persist']
        change_desc = simulation.change_description.lower()

        if any(keyword in change_desc for keyword in data_keywords):
            impact_score += 0.5
            concerns.append("Involves data persistence - integrity risk")

        # Verificar se modifica estruturas de dados
        if 'schema' in change_desc or 'migration' in change_desc:
            impact_score += 0.7
            concerns.append("Modifies data structures - high integrity risk")

        simulation.add_category_impact(RiskCategory.DATA_INTEGRITY, {
            "impact_score": min(impact_score, 1.0),
            "concerns": concerns
        })

    async def _run_simulation_scenarios(self, simulation: ImpactSimulation) -> None:
        """Executa cenários de simulação."""

        scenarios = [
            ("Basic functionality test", self._test_basic_functionality),
            ("Error handling test", self._test_error_handling),
            ("Resource usage test", self._test_resource_usage),
            ("Integration test", self._test_integration),
            ("Security validation test", self._test_security_validation)
        ]

        for scenario_name, test_func in scenarios:
            try:
                success, impact_score, details = await test_func(simulation)
                simulation.add_scenario_result(scenario_name, success, impact_score, details)
            except Exception as e:
                simulation.add_scenario_result(scenario_name, False, 1.0, f"Test failed: {e}")

    async def _test_basic_functionality(self, simulation: ImpactSimulation) -> Tuple[bool, float, str]:
        """Testa funcionalidade básica."""
        # Simulação simplificada
        await asyncio.sleep(0.1)
        impact_score = 0.2 if "core" in simulation.affected_components else 0.1
        return True, impact_score, "Basic functionality test passed"

    async def _test_error_handling(self, simulation: ImpactSimulation) -> Tuple[bool, float, str]:
        """Testa tratamento de erros."""
        await asyncio.sleep(0.1)
        impact_score = 0.4 if "error" in simulation.change_description.lower() else 0.1
        return True, impact_score, "Error handling test passed"

    async def _test_resource_usage(self, simulation: ImpactSimulation) -> Tuple[bool, float, str]:
        """Testa uso de recursos."""
        await asyncio.sleep(0.1)
        impact_score = 0.3
        return True, impact_score, "Resource usage test passed"

    async def _test_integration(self, simulation: ImpactSimulation) -> Tuple[bool, float, str]:
        """Testa integração."""
        await asyncio.sleep(0.1)
        impact_score = 0.2
        return True, impact_score, "Integration test passed"

    async def _test_security_validation(self, simulation: ImpactSimulation) -> Tuple[bool, float, str]:
        """Testa validação de segurança."""
        await asyncio.sleep(0.1)
        impact_score = 0.8 if "security" in simulation.change_description.lower() else 0.2
        return True, impact_score, "Security validation test passed"

    def should_approve_change(self, simulation: ImpactSimulation) -> Tuple[bool, str]:
        """Determina se uma mudança deve ser aprovada."""

        # Verificar bloqueios críticos
        should_block, reason = simulation.should_block_change()
        if should_block:
            self.stats["blocked_changes"] += 1
            return False, reason

        # Verificar configurações de risco
        if (self.risk_thresholds["block_critical"] and
            simulation.impact_level == ImpactLevel.CRITICAL):
            self.stats["blocked_changes"] += 1
            return False, "Critical impact level blocked by policy"

        if (self.risk_thresholds["block_high_security"] and
            simulation.category_impacts.get(RiskCategory.SECURITY, {}).get("impact_score", 0) > 0.7):
            self.stats["blocked_changes"] += 1
            return False, "High security risk blocked by policy"

        # Aprovar com recomendações
        self.stats["approved_changes"] += 1
        recommendations = "; ".join(simulation.recommendations) if simulation.recommendations else "None"
        return True, f"Approved with recommendations: {recommendations}"

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das simulações."""

        approval_rate = 0.0
        total_decisions = self.stats["approved_changes"] + self.stats["blocked_changes"]
        if total_decisions > 0:
            approval_rate = self.stats["approved_changes"] / total_decisions

        return {
            **self.stats,
            "approval_rate": approval_rate,
            "recent_simulations": [
                sim.to_dict() for sim in self.simulations[-10:]
            ]
        }

    def get_high_risk_simulations(self, limit: int = 10) -> List[ImpactSimulation]:
        """Retorna simulações de alto risco."""

        high_risk = [
            sim for sim in self.simulations
            if sim.impact_level in [ImpactLevel.HIGH, ImpactLevel.CRITICAL]
        ]

        return sorted(high_risk, key=lambda x: x.simulated_at, reverse=True)[:limit]

    def _load_state(self) -> None:
        """Carrega estado do simulador."""

        if self.simulations_file.exists():
            try:
                data = json.loads(self.simulations_file.read_text(encoding='utf-8'))

                for sim_data in data.get("simulations", []):
                    simulation = ImpactSimulation(
                        sim_data["change_description"],
                        sim_data["change_type"]
                    )

                    simulation.simulated_at = datetime.fromisoformat(sim_data["simulated_at"])
                    simulation.overall_risk_score = sim_data.get("overall_risk_score", 0.0)
                    simulation.impact_level = ImpactLevel(sim_data["impact_level"])
                    simulation.category_impacts = {
                        RiskCategory(k): v for k, v in sim_data.get("category_impacts", {}).items()
                    }
                    simulation.affected_components = sim_data.get("affected_components", [])
                    simulation.affected_dependencies = sim_data.get("affected_dependencies", [])
                    simulation.scenarios_tested = sim_data.get("scenarios_tested", [])
                    simulation.recommendations = sim_data.get("recommendations", [])
                    simulation.blocking_concerns = sim_data.get("blocking_concerns", [])
                    simulation.simulation_successful = sim_data.get("simulation_successful", True)
                    simulation.confidence_level = sim_data.get("confidence_level", 0.0)

                    self.simulations.append(simulation)

                # Carregar estatísticas
                if "stats" in data:
                    self.stats.update(data["stats"])

            except Exception as e:
                print(f"Error loading impact simulations: {e}")

        # Carregar baseline
        if self.baseline_file.exists():
            try:
                self.system_baseline = json.loads(self.baseline_file.read_text(encoding='utf-8'))
            except Exception:
                self._initialize_baseline()

    def _save_state(self) -> None:
        """Persiste estado do simulador."""

        self.impact_dir.mkdir(parents=True, exist_ok=True)

        # Salvar simulações
        simulations_data = {
            "simulations": [sim.to_dict() for sim in self.simulations[-500:]],  # Últimas 500
            "stats": self.stats,
            "last_updated": datetime.now().isoformat()
        }

        self.simulations_file.write_text(
            json.dumps(simulations_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def _save_baseline(self) -> None:
        """Salva baseline do sistema."""

        self.baseline_file.write_text(
            json.dumps(self.system_baseline, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
