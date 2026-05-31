class MailProcessorError(Exception):
    """
    Базовый класс для всех исключений нашего приложения, наследуется от встроенного Exception
    """
    pass


class ConfigError(MailProcessorError):
    """Исключение возникающее при проблемах с конфигурационным файлом правил"""
    pass


class FileParseError(MailProcessorError):
    """Исключение при невозможности правильно разобрать структуру письма"""
    pass
