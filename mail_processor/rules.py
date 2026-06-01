import json
from pathlib import Path
from typing import Any
from mail_processor.exceptions import ConfigError


class RuleEngine:
    """
    Механизм классификации электронных писем на основе подсчета совпадений ключевых слов.
    
    Загружает правила из внешнего конфигурационного файла и определяет наиболее 
    вероятную категорию письма, суммируя количество найденных ключевых слов в теме и теле.
    """

    def __init__(self, rules_path: Path) -> None:
        """
        Initializes the RuleEngine instance.

        Args:
            rules_path (Path): Путь к файлу конфигурации JSON, содержащему правила классификации.
        """
        self.rules: dict = self._load_rules(rules_path)

    def _load_rules(self, rules_path: Path) -> dict:
        """
        Безопасно загружает и парсит правила классификации из JSON-файла с использованием EAFP-подхода.

        Args:
            rules_path (Path): Путь к файлу конфигурации JSON.

        Returns:
            dict: Словарь с загруженными правилами классификации.

        Raises:
            ConfigError: Если файл не найден, содержит некорректный JSON или произошла 
                         системная ошибка ввода-вывода.
        """
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            raise ConfigError(f"Ошибка загрузки конфигурации правил: {e}")

    def classify(self, email: Any) -> str:
        """
        Определяет смысловую категорию письма на основе максимального числа совпадений ключевых слов.
        
        Анализирует тему и тело письма, подсчитывая все вхождения ключевых слов для 
        каждой категории. Побеждает категория с наибольшим итоговым счетом (score). В случае
        равенства баллов возвращается первая из категорий с максимальным весом.

        Args:
            email (Any): Объект электронного письма, содержащий текстовые атрибуты subject и body.

        Returns:
            str: Название категории с максимальным количеством совпадений или 
                 'unclassified', если совпадений не обнаружено.
        """
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()

        category_scores = {}

        for category, rules in self.rules.get("categories", {}).items():
            score = 0
            
            for kw in rules.get("keywords_subject", []):
                kw_lower = kw.lower()
                if kw_lower:
                    score += subject_lower.count(kw_lower)
            
            for kw in rules.get("keywords_body", []):
                kw_lower = kw.lower()
                if kw_lower:
                    score += body_lower.count(kw_lower)
            
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return "unclassified"

        return max(category_scores, key=category_scores.get)