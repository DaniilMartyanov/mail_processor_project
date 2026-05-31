import json
from pathlib import Path
from typing import Any
from mail_processor.exceptions import ConfigError


class RuleEngine:
    """
    Движок классификации электронных писем на основе правил из внешнего конфигурационного файла.
    """

    def __init__(self, rules_path: Path) -> None:
        """
        Initializes the RuleEngine.

        Args:
            rules_path (Path): Путь к файлу конфигурации JSON, содержащему правила классификации.
        """
        self.rules: dict = self._load_rules(rules_path)

    def _load_rules(self, rules_path: Path) -> dict:
        """
        Загружает и парсит правила классификации из JSON-файла с использованием EAFP-подхода.

        Args:
            rules_path (Path): Путь к файлу конфигурации JSON.

        Returns:
            dict: Словарь с загруженными правилами классификации.

        Raises:
            ConfigError: Если файл не найден, содержит некорректный JSON или произошла системная ошибка ввода-вывода.
        """
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            raise ConfigError(f"Ошибка загрузки конфигурации правил: {e}")

    def classify(self, email: Any) -> str:
        """
        Определяет смысловую категорию письма на основе совпадения ключевых слов в теме и теле.

        Args:
            email (Any): Объект электронного письма, содержащий текстовые атрибуты subject и body.

        Returns:
            str: Название определенной категории или 'unclassified', если совпадений не найдено.
        """
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()

        for category, rules in self.rules.get("categories", {}).items():
            for kw in rules.get("keywords_subject", []):
                if kw.lower() in subject_lower:
                    return category
            
            for kw in rules.get("keywords_body", []):
                if kw.lower() in body_lower:
                    return category

        return "unclassified"