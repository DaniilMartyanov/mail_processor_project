import re 
from pathlib import Path  
from mail_processor.exceptions import FileParseError


class Email:
    """класс отвечающий за парсинг и структуру письма"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.headers = {}
        self.body = ""
        self.is_valid = False
        self._parse()

    def _parse(self) -> None:

        content = ""

        for encoding in ["utf-8", "windows-1251", "latin-1"]:
            try:
                with open(self.file_path, "r", encoding=encoding) as f:
                    content = f.read()
                break 
            except (UnicodeDecodeError, OSError):
                continue

        if not content.strip():
            raise FileParseError(f"Файл пуст или недоступен для чтения: {self.file_path.name}")

        header_patterns = {
            "from": re.compile(r"^(From|От кого|Ot kogo):\s*(.*)$", re.IGNORECASE),
            "to": re.compile(r"^(To|Кому|Komu):\s*(.*)$", re.IGNORECASE),
            "date": re.compile(r"^(Date|Дата|Data):\s*(.*)$", re.IGNORECASE),
            "subject": re.compile(r"^(Subject|Тема|Tema):\s*(.*)$", re.IGNORECASE)
        }

        lines = content.splitlines()
        body_start_idx = 0

        for idx, line in enumerate(lines):
            matched = False
            for key, pattern in header_patterns.items():
                match = pattern.match(line)
                if match:
                    self.headers[key] = match.group(2).strip()
                    matched = True
                    break

            if not line.strip() and self.headers:
                body_start_idx = idx + 1
                break

            if not matched and self.headers and idx > 0:
                body_start_idx = idx
                break

        self.body = "\n".join(lines[body_start_idx:]).strip()
        self.is_valid = True

    @property
    def subject(self) -> str:
        return self.headers.get("subject", "")

    @property
    def sender(self) -> str:
        return self.headers.get("from", "")
