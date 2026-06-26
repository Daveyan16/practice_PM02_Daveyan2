import logging
import sys

logger = logging.getLogger("booking_system")
logger.setLevel(logging.INFO) # Устанавливаем базовый уровень логирования

# Создаем обработчик (handler) для вывода логов в консоль (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Создаем обработчик для записи логов в файл
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG) # В файл будем писать более подробную информацию

# Создаем форматтер, который определяет, как будет выглядеть строка лога
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Применяем форматтер к нашим обработчикам
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Добавляем обработчики к нашему логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)