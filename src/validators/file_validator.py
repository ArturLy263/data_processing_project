import os


class FileValidator:

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        if self.mode not in ["w", "a"] and not os.path.exists(self.filename):
            raise FileNotFoundError(f"Файл не найден: {self.filename}")
        self.file = open(self.filename, self.mode, newline="")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        if exc_type:
            print(f"Ошибка при работе с файлом: {exc_val}")
        return False
