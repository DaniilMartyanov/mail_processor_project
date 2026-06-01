import shutil
import logging
from pathlib import Path
from mail_processor.models import Email
from mail_processor.rules import RuleEngine
from mail_processor.exceptions import FileParseError, ConfigError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class EmailProcessor:
    def __init__(self, src_dir, dst_dir, rules_path):
        self.src_dir = Path(src_dir)
        self.dst_dir = Path(dst_dir)
        self.rules_path = Path(rules_path)
        self.stats = {}

    def setup_directories(self, categories):
        self.dst_dir.mkdir(parents=True, exist_ok=True)
        all_categories = categories + ["unclassified", "corrupted"]
        for cat in all_categories:
            (self.dst_dir / cat).mkdir(parents=True, exist_ok=True)
            self.stats[cat] = 0

    def process_all(self):
        try:
            engine = RuleEngine(self.rules_path)
        except ConfigError as e:
            logging.error(f"Не удалось инициализировать процессор из-за ошибки правил: {e}")
            return
        categories = list(engine.rules["categories"])
        self.setup_directories(categories)
        if not self.src_dir.exists():
            logging.error(f"Исходная директория {self.src_dir} не существует.")
            return
        for file_path in self.src_dir.iterdir():
            if file_path.is_dir() or file_path.name.startswith('.'):
                continue
            try:
                email = Email(file_path)
                category = engine.classify(email)
                dest_folder = self.dst_dir / category
                self.stats[category] += 1
                logging.info(f"Файл {file_path.name} отнесен к категории: {category}")
            except FileParseError as e:
                dest_folder = self.dst_dir / "corrupted"
                self.stats["corrupted"] = self.stats.get("corrupted", 0) + 1
                logging.warning(f"Файл {file_path.name} поврежден или пуст. Перемещен в 'corrupted'. Ошибка: {e}")
            except Exception as e:
                dest_folder = self.dst_dir / "corrupted"
                self.stats["corrupted"] = self.stats.get("corrupted", 0) + 1
                logging.error(f"Непредвиденная ошибка при обработке {file_path.name}: {e}")
            try:
                shutil.move(file_path, dest_folder / file_path.name)
            except OSError as e:
                logging.error(f"Не удалось скопировать файл {file_path.name}: {e}")

        self.generate_report()

    def generate_report(self):
        report_path = self.dst_dir / "report.txt"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("=== Отчет по обработке почты ===\n")
                for cat, count in self.stats.items():
                    f.write(f"Категория '{cat}': {count} шт.\n")
            logging.info(f"Аналитический отчет сохранен в {report_path}")
        except OSError as e:
            logging.error(f"Не удалось создать файл отчета: {e}")

        try:
            import matplotlib.pyplot as plt
            active_stats = {k: v for k, v in self.stats.items() if v > 0}
            if active_stats:
                plt.figure(figsize=(8, 4))
                plt.barh(list(active_stats.keys()), list(active_stats.values()), color='#2980b9')
                plt.title("Распределение писем по категориям", fontsize=12, fontweight='bold')
                plt.xlabel("Количество (шт.)")
                plt.tight_layout()
                plt.savefig(self.dst_dir / "report_chart.png", dpi=150)
                plt.close()
                logging.info("График аналитики сохранен.")
        except ImportError:
            logging.warning("Библиотека matplotlib не найдена. График не построен.")