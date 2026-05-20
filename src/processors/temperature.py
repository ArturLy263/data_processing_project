class TemperatureStream:

    def __init__(self, data_list, threshold, min_valid=100):
        self.data_list = data_list
        self.threshold = threshold
        self.min_valid = min_valid
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.data_list):
            value = self.data_list[self.index]
            self.index += 1
            if value < self.min_valid:
                continue
            return value
        raise StopIteration