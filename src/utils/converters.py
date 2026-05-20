RAW_KELWIN_DATA = [290.15, 305.5, 200, 273.15, 350.9, 475.9, 274.2, 477.7, 122.3, 534]

def kelvin_to_celsius_converter(value):
    for data in value:
        celsius = data - 273.15
        yield celsius

class TemperatureStream:
    def __init__(self, data_list, threshold):
        self.data_list = data_list
        self.threshold = threshold
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.data_list):
            value = self.data_list[self.index]
            self.index += 1

            if value < 100:
                continue

            return value
        raise StopIteration

# if __name__ == '__main__':
#     stream = TemperatureStream(RAW_KELWIN_DATA, 50)
#     celsius_generator = kelvin_to_celsius_converter(stream)
#
#     for temp_c in celsius_generator:
#         if temp_c > stream.threshold:
#             print(f"ALERT: 52.85 °C - High Reading")
#         else:
#             print(f"Normal temperature reading")

if __name__ == '__main__':
    stream = TemperatureStream(RAW_KELWIN_DATA, 50) 
    celsius_generator = kelvin_to_celsius_converter(stream) 

    for temp_c in celsius_generator:  
        if temp_c > stream.threshold:  
            print(f"ALERT: {temp_c:.2f} °C - High Reading")
        else:
            print(f"Normal temperature reading: {temp_c:.2f} °C")
