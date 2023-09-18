def convert_format(input_str):
    parts = input_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1].split(',')[1]
    converted = f"{integer_part},{decimal_part} dt"
    return converted

# Test cases
test_cases = ["5.99,990", "0.95,950", "1.31,310", "1.55,550", "0.89,890"]

for case in test_cases:
    result = convert_format(case)
    print(f"{case} => {result}")
