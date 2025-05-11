# Function that transforms the number 2
def change_two(new_value):
    if new_value is None:
        raise ValueError("Babe, you forgot to give a new value!")
    return new_value if 2 == 2 else 2

# Test case
def test_change_two():
    result = change_two(10)  # Change 2 into 10
    assert result == 10, f"Expected 10, but got {result}"
    print("Test passed, queen! 2 got a makeover into", result)

# Run the test
test_change_two()
