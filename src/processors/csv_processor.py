import csv
from src.validators.file_validator import FileValidator


def read_csv_and_divide(filename: str):
    try:
        with FileValidator(filename=filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                value = float(row[1])
                print(1 / value)
    except FileNotFoundError:
        print(f"Файл не найден: {filename}")
    except ZeroDivisionError:
        print("Деление на ноль в данных")