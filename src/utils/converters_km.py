def convert_distance(value, direction):
    CONVERTION_FACTOR = 0.621371
    if direction == "KM_TO_MI":
        result = value * CONVERTION_FACTOR
        unit = "miles"
    elif direction == "MI_TO_KM":
        result = value / CONVERTION_FACTOR
        unit = "kilometers"
    else:
        return None, None
    return result, unit

def run_converter():
        while True:
            print("1 Convert KM to MI")
            print("2 Convert MI to KM")
            print("Q. Exit")

            choice =input("Choose option: ").upper()

            if choice == "Q":
                print("Break")
                break

            if choice == "1":
                direction = "KM_TO_MI"
            elif choice == "2":
                direction = "MI_TO_KM"
            else:
                print("Invalid")
                continue

            try:
                value = float(input("Text: "))
            except ValueError:
                print("Invalid")
                continue

            if value < 0:
                print("Invalid")
                continue

            result, unit = convert_distance(value, direction)
            print(f"Result: {result}, Unit: {unit}")


if __name__ == "__main__":
