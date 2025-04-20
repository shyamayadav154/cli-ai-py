def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def calculate_subtraction(numbers):
    total = numbers[0]
    for num in numbers[1:]:
        total -= num
    return total

def main():
    numbers = [1, 2, 3, 4, 5]
    sum_result = calculate_sum(numbers)
    subtraction_result = calculate_subtraction(numbers)
    print(f"Sum: {sum_result}")
    print(f"Subtraction: {subtraction_result}")

if __name__ == "__main__":
    main()
