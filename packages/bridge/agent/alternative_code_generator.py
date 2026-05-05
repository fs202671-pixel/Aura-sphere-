"""
Alternative Code Generator - Gerador de versões alternativas de código

Sistema que gera variações diferentes do próprio código da IA para evolução.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class AlternativeVersion:
    """Versão alternativa de código gerada"""
    variant_id: str
    original_module: str
    variant_type: str  # "optimization", "refactor", "alternative_algorithm"
    description: str
    code_changes: Dict[str, str]  # {file: new_code}
    metrics: Dict[str, float]  # estimated metrics
    created_at: str
    complexity_score: float  # 0-10


class AlternativeCodeGenerator:
    """Gera versões alternativas de código para evolução"""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("data/code_variants")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.variants: List[AlternativeVersion] = []
        self._load_variants()

    def generate_optimization_variant(self, module_name: str, description: str) -> AlternativeVersion:
        """Gera variante otimizada de um módulo"""
        import uuid

        variant = AlternativeVersion(
            variant_id=f"opt_{uuid.uuid4().hex[:8]}",
            original_module=module_name,
            variant_type="optimization",
            description=description,
            code_changes=self._generate_optimization_changes(module_name),
            metrics={
                "performance": 0.2,  # +20% melhoria esperada
                "memory": 0.15,      # +15% melhoria esperada
                "maintainability": -0.05  # Pode sacrificar um pouco
            },
            created_at=datetime.now().isoformat(),
            complexity_score=4.0
        )

        self.variants.append(variant)
        self._save_variants()
        return variant

    def generate_refactor_variant(self, module_name: str, description: str) -> AlternativeVersion:
        """Gera variante refatorada de um módulo"""
        import uuid

        variant = AlternativeVersion(
            variant_id=f"ref_{uuid.uuid4().hex[:8]}",
            original_module=module_name,
            variant_type="refactor",
            description=description,
            code_changes=self._generate_refactor_changes(module_name),
            metrics={
                "readability": 0.3,  # +30% legibilidade
                "maintainability": 0.25,  # +25% manutenibilidade
                "test_coverage": 0.2  # +20% cobertura de testes
            },
            created_at=datetime.now().isoformat(),
            complexity_score=5.5
        )

        self.variants.append(variant)
        self._save_variants()
        return variant

    def generate_algorithm_variant(self, module_name: str, algorithm_name: str, 
                                 description: str) -> AlternativeVersion:
        """Gera variante com algoritmo alternativo"""
        import uuid

        variant = AlternativeVersion(
            variant_id=f"alg_{uuid.uuid4().hex[:8]}",
            original_module=module_name,
            variant_type="alternative_algorithm",
            description=description,
            code_changes=self._generate_algorithm_changes(module_name, algorithm_name),
            metrics={
                "performance": 0.35,  # +35% performance
                "accuracy": 0.1,      # +10% precisão
                "complexity": 0.15    # +15% complexidade computacional
            },
            created_at=datetime.now().isoformat(),
            complexity_score=7.5
        )

        self.variants.append(variant)
        self._save_variants()
        return variant

    def get_variants(self, module_name: Optional[str] = None,
                    variant_type: Optional[str] = None) -> List[AlternativeVersion]:
        """Retorna variantes filtradas"""
        variants = self.variants

        if module_name:
            variants = [v for v in variants if v.original_module == module_name]

        if variant_type:
            variants = [v for v in variants if v.variant_type == variant_type]

        return variants

    def compare_variants(self, variant_a: AlternativeVersion,
                        variant_b: AlternativeVersion) -> Dict[str, Any]:
        """Compara duas variantes"""
        return {
            "variant_a_id": variant_a.variant_id,
            "variant_b_id": variant_b.variant_id,
            "metrics_a": variant_a.metrics,
            "metrics_b": variant_b.metrics,
            "complexity_a": variant_a.complexity_score,
            "complexity_b": variant_b.complexity_score,
            "recommendation": self._recommend_better_variant(variant_a, variant_b)
        }

    def _generate_optimization_changes(self, module_name: str) -> Dict[str, str]:
        """Gera mudanças de otimização para um módulo"""
        optimizations = {
            "memory": """
# Implementar cache LRU
from functools import lru_cache

@lru_cache(maxsize=256)
def expensive_operation(self, param):
    return self._compute_result(param)

# Usar geradores em vez de listas
def process_items(self, items):
    for item in items:
        yield self.transform(item)
""",
            "performance": """
# Usar estruturas de dados mais eficientes
from collections import defaultdict

# mapear chaves -> lista de valores
cache = defaultdict(list)

# Usar binary search em vez de linear
import bisect
sorted_list = sorted(data)
idx = bisect.bisect_left(sorted_list, value)
""",
            "algorithm": """
# Implementar algoritmo mais eficiente
def optimized_search(self, items, target):
    # Usar busca binária em vez de linear O(n) -> O(log n)
    left, right = 0, len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
        }

        return {f"{module_name}_optimized.py": optimizations.get("performance", "")}

    def _generate_refactor_changes(self, module_name: str) -> Dict[str, str]:
        """Gera mudanças de refatoração para um módulo"""
        refactoring = {
            "structure": """
# Separar responsabilidades
class DataProcessor:
    def process(self, data):
        validated = self._validate(data)
        transformed = self._transform(validated)
        return self._format(transformed)

    def _validate(self, data):
        # Validação
        pass

    def _transform(self, data):
        # Transformação
        pass

    def _format(self, data):
        # Formatação
        pass
""",
            "patterns": """
# Implementar padrões de design
class Factory:
    @staticmethod
    def create(type_name: str):
        if type_name == 'A':
            return TypeA()
        elif type_name == 'B':
            return TypeB()

class Observer:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)
"""
        }

        return {f"{module_name}_refactored.py": refactoring.get("structure", "")}

    def _generate_algorithm_changes(self, module_name: str, algorithm_name: str) -> Dict[str, str]:
        """Gera mudanças de algoritmo alternativo"""
        algorithms = {
            "search": """
# Algoritmo de busca alternativo: Interpolation Search
def interpolation_search(self, data, target):
    low, high = 0, len(data) - 1
    while low <= high and target >= data[low] and target <= data[high]:
        pos = low + int((high - low) / (data[high] - data[low]) * (target - data[low]))
        if data[pos] == target:
            return pos
        if data[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    return -1
""",
            "sort": """
# Algoritmo de ordenação alternativo: Merge Sort
def merge_sort(self, data):
    if len(data) <= 1:
        return data
    mid = len(data) // 2
    left = self.merge_sort(data[:mid])
    right = self.merge_sort(data[mid:])
    return self._merge(left, right)

def _merge(self, left, right):
    result = []
    while left and right:
        if left[0] <= right[0]:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right
"""
        }

        return {f"{module_name}_{algorithm_name}_alt.py": algorithms.get(algorithm_name, "")}

    def _recommend_better_variant(self, variant_a: AlternativeVersion,
                                 variant_b: AlternativeVersion) -> str:
        """Recomenda qual variante é melhor"""
        score_a = sum(variant_a.metrics.values()) / len(variant_a.metrics)
        score_b = sum(variant_b.metrics.values()) / len(variant_b.metrics)

        if score_a > score_b:
            return f"{variant_a.variant_id} é melhor (score: {score_a:.2f} vs {score_b:.2f})"
        else:
            return f"{variant_b.variant_id} é melhor (score: {score_b:.2f} vs {score_a:.2f})"

    def _save_variants(self) -> None:
        """Persiste variantes em arquivo"""
        variants_file = self.base_path / "code_variants.json"
        data = {
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "original_module": v.original_module,
                    "variant_type": v.variant_type,
                    "description": v.description,
                    "code_changes": v.code_changes,
                    "metrics": v.metrics,
                    "created_at": v.created_at,
                    "complexity_score": v.complexity_score
                }
                for v in self.variants
            ]
        }
        variants_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_variants(self) -> None:
        """Carrega variantes do arquivo"""
        variants_file = self.base_path / "code_variants.json"
        if not variants_file.exists():
            return

        try:
            data = json.loads(variants_file.read_text(encoding="utf-8"))
            for v_data in data.get("variants", []):
                variant = AlternativeVersion(
                    variant_id=v_data["variant_id"],
                    original_module=v_data["original_module"],
                    variant_type=v_data["variant_type"],
                    description=v_data["description"],
                    code_changes=v_data["code_changes"],
                    metrics=v_data["metrics"],
                    created_at=v_data["created_at"],
                    complexity_score=v_data["complexity_score"]
                )
                self.variants.append(variant)
        except Exception:
            pass
