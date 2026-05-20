print ("SCRIPT STARTED")

import os

class FileValidator:

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        print(f"[{self.filename}]: Attempting to open file in '{self.mode}' mode")

        if self.mode not in ["w", "a"] and not os.path.exists(self.filename):
            raise FileNotFoundError(f'({self.filename}): File not found')
            # print(f"[{self.filename}]: FileNotFoundError")

        self.file = open(self.filename, self.mode, newline='')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
            print(f"[{self.filename}]: File closed")

        if exc_type:
            print(f"Exception: {exc_type}")
            print(f"Exception: {exc_val}")

        return False

import csv
# Index, Value = 1,10

try:
    with FileValidator(filename='data_list.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            value = float(row[1])
            print(1 / value)

except FileNotFoundError:
    print("File not found")

except ZeroDivisionError:
    print("Division by zero")