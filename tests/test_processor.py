import pytest
from pathlib import Path
from mail_processor.models import Email
from mail_processor.rules import RuleEngine
from mail_processor.exceptions import FileParseError, ConfigError
from mail_processor.engine import EmailProcessor
import shutil


@pytest.fixture
def create_test_file(tmp_path):
    def create(filename, content):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path
    return create


def test_parse_valid_email(create_test_file):
    content = "От кого: ivanivanov@yandex.ru\nТема: Закончились ручки\n\nМне нечем писать!"
    file_path = create_test_file("test_mail.txt", content)
    
    email = Email(file_path)
    assert email.is_valid is True
    assert email.sender == "ivanivanov@yandex.ru"
    assert email.subject == "Закончились ручки"
    assert "Мне нечем писать!" in email.body


def test_parse_empty_file_raises_error(create_test_file):
    file_path = create_test_file("empty.txt", "")
    with pytest.raises(FileParseError):
        Email(file_path)

@pytest.mark.parametrize("subject,body,expected_category", [
    ("Вы выиграли суперприз", "Зайдите на totally-not-spam.ru", "security_alert"),
    ("Критический инцидент: упал код", "Ошибка 500 в системе авторизации", "critical_incidents"),
    ("Заявка на ежегодный отпуск", "Прошу согласовать отпуск с понедельника", "hr_admin"),
    ("Вопрос по работе", "Привет, как дела?", "unclassified")
])
def test_classification_logic(tmp_path, create_test_file, subject, body, expected_category):
    rules_json = """{
      "categories": {
        "security_alert": {
          "keywords_subject": ["выиграли"], "keywords_body": ["totally-not-spam"]
        },
        "critical_incidents": {
          "keywords_subject": ["упал"], "keywords_body": ["ошибка 500"]
        },
        "hr_admin": {
          "keywords_subject": ["отпуск"], "keywords_body": ["согласовать"]
        }
      }
    }"""
    rules_path = tmp_path / "rules_test.json"
    rules_path.write_text(rules_json, encoding="utf-8")
    
    email_content = f"Subject: {subject}\n\n{body}"
    email_file = create_test_file("mail.txt", email_content)
    
    email = Email(email_file)
    engine = RuleEngine(rules_path)
    
    assert engine.classify(email) == expected_category

def test_parse_unknown_format_raises_error(create_test_file):
    file_path = create_test_file("test.json", '{"key": "value"}')
    with pytest.raises(FileParseError):
        Email(file_path)

def test_missing_rules_file_raises_config_error(tmp_path):
    fake_rules = tmp_path / "nonexistent.json"
    with pytest.raises(ConfigError):
        RuleEngine(fake_rules)

def test_invalid_json_rules_raises_config_error(tmp_path):
    invalid_json = tmp_path / "bad.json"
    invalid_json.write_text("{ invalid json }", encoding="utf-8")
    with pytest.raises(ConfigError):
        RuleEngine(invalid_json)

def test_parse_transliterated_headers(create_test_file):
    content = "Ot kogo: a.fedorova@yandex.ru\nTema: Bolnichnyy nada\n\nText"
    file_path = create_test_file("translit.txt", content)
    email = Email(file_path)
    assert email.sender == "a.fedorova@yandex.ru"
    assert email.subject == "Bolnichnyy nada"
    assert "Text" in email.body

def test_email_without_body(create_test_file):
    content = "Subject: subject\nFrom: user@yandex.ru"
    file_path = create_test_file("no_body.txt", content)
    email = Email(file_path)
    assert email.subject == "subject"
    assert email.body == ""

def test_processor_moves_file_to_category(tmp_path, create_test_file):
    rules = tmp_path / "rules.json"
    rules.write_text('{"categories": {"test_cat": {"keywords_subject": ["test"], "keywords_body": []}}}')
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    email_content = "Subject: test\n\nBody"
    email_file = create_test_file("test_email.txt", email_content)
    shutil.move(email_file, inbox / "test_email.txt")
    
    processor = EmailProcessor(src_dir=inbox, dst_dir=tmp_path / "out", rules_path=rules)
    processor.process_all()
    
    out_cat = tmp_path / "out" / "test_cat"
    assert out_cat.exists()
    assert (out_cat / "test_email.txt").exists()
