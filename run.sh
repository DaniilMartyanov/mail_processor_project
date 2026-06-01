INBOX_DIR="./inbox"
OUTPUT_DIR="./output"
PYTHON_SCRIPT="main.py"

echo "Инициализация запуска обработчика почты"

if [ ! -d "$INBOX_DIR" ]; then
    echo "Директория '$INBOX_DIR' отсутствует. Создаю пустую папку"
    mkdir -p "$INBOX_DIR"
fi

if [ -d "$OUTPUT_DIR" ]; then
    echo "Удаление старых результатов в '$OUTPUT_DIR'"
    rm -rf "$OUTPUT_DIR"
fi

echo "Запуск обработки писем"
py "$PYTHON_SCRIPT" "$INBOX_DIR" "$OUTPUT_DIR"
