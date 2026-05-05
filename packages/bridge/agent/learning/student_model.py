import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class StudentModel:
    """Mantém o perfil do aluno, histórico e progresso por tema."""

    def __init__(self, persistence_path: Optional[str] = None):
        path = Path(persistence_path) if persistence_path else Path(__file__).resolve().parent
        if path.is_dir() or str(path).endswith(('/', '\\')):
            path = path / "student_data.json"
        self.persistence_path = path
        self.topics: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.persistence_path.exists():
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    self.topics = json.load(f)
            except Exception:
                self.topics = {}

    def save(self) -> None:
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.persistence_path, "w", encoding="utf-8") as f:
            json.dump(self.topics, f, indent=2, ensure_ascii=False)

    def _normalize_topic(self, topic: str) -> str:
        return topic.strip().lower()

    def get_topic_profile(self, topic: str) -> Dict[str, Any]:
        key = self._normalize_topic(topic)
        if key not in self.topics:
            self.topics[key] = {
                "topic": topic.strip(),
                "level": 1,
                "score": 0,
                "correct": 0,
                "incorrect": 0,
                "weaknesses": [],
                "history": [],
                "active_plan": None,
                "last_updated": None,
            }
        return self.topics[key]

    def record_history(self, topic: str, entry: str) -> None:
        profile = self.get_topic_profile(topic)
        profile["history"].append(entry)
        profile["last_updated"] = entry
        self.save()

    def set_active_plan(self, topic: str, plan: Dict[str, Any]) -> None:
        profile = self.get_topic_profile(topic)
        profile["active_plan"] = plan
        profile["last_updated"] = "plan_assigned"
        self.save()

    def get_active_plan(self, topic: str) -> Optional[Dict[str, Any]]:
        return self.get_topic_profile(topic).get("active_plan")

    def update_performance(self, topic: str, correct: bool, feedback: str, weaknesses: Optional[List[str]] = None) -> None:
        profile = self.get_topic_profile(topic)
        if correct:
            profile["correct"] += 1
            profile["score"] += 10
        else:
            profile["incorrect"] += 1
            profile["score"] = max(profile["score"] - 2, 0)

        if weaknesses:
            for weakness in weaknesses:
                if weakness not in profile["weaknesses"]:
                    profile["weaknesses"].append(weakness)

        profile["history"].append(feedback)
        profile["level"] = self._estimate_level(profile)
        profile["last_updated"] = feedback
        self.save()

    def _estimate_level(self, profile: Dict[str, Any]) -> int:
        if profile["score"] >= 80:
            return 4
        if profile["score"] >= 40:
            return 3
        if profile["score"] >= 15:
            return 2
        return 1

    def get_progress(self, topic: str) -> Dict[str, Any]:
        profile = self.get_topic_profile(topic)
        return {
            "topic": profile["topic"],
            "level": profile["level"],
            "score": profile["score"],
            "correct": profile["correct"],
            "incorrect": profile["incorrect"],
            "weaknesses": profile["weaknesses"],
            "history_length": len(profile["history"]),
        }

    def list_topics(self) -> List[str]:
        return [profile["topic"] for profile in self.topics.values()]
