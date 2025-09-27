import math
import datetime
import pandas as pd
from tools import ToolManager, BaseTool, get_current_time, calculator, Final_Answer, run_sql_query

# --- Mock/Helper Functions for Testing ---

def mock_sql_query(query: str, params: tuple = (), db_file="sales_data.db"):
    """
    Mock function to simulate a database query for testing without an actual DB file.
    """
    if "SUM" in query:
        # Simulate a single numerical result (e.g., total revenue)
        return 5000000 
    elif "SELECT * FROM unified_sales_data" in query:
        # Simulate a DataFrame result
        return "Row 1, Value A\nRow 2, Value B"
    elif "non_existent_table" in query:
        # Simulate a database error
        raise sqlite3.Error("No such table: non_existent_table")
    return "Mock Query Result"

# Override the run_sql_query function for safe testing
# NOTE: In a real environment, you would use mocking frameworks like 'unittest.mock'
# But since we are using simple asserts, we override it directly here for demonstration.
# run_sql_query = BaseTool("run_sql_query", mock_sql_query) # Uncomment this if you want to use the mock tool

def test_tool_manager_registration():
    """Kiểm tra chức năng khởi tạo và đăng ký công cụ, bao gồm cả mô tả."""
    
    # --- Helper Tool Definition ---
    def print_meomeo(name: str, times: int = 1):
        """tool that will return meomeo repeated N times with the given name."""
        return ("meomeo " * times) + name
    
    def simple_add(a: int, b: int):
        """tool for adding two numbers."""
        return a + b
    
    test_meomeo_tool = BaseTool("print_meomeo", print_meomeo)
    test_add_tool = BaseTool("simple_add", simple_add)

    register = ToolManager()
    register.add_tool(test_meomeo_tool)
    register.add_tool(test_add_tool)

    print("\n--- Unit Test for tools module ---")
    print("-- Case 1: BaseTool Initialization and Run (Positional Args)")
    assert test_meomeo_tool.description.strip() == "tool that will return meomeo repeated N times with the given name."
    # Test multiple arguments
    assert test_meomeo_tool.run("nam", 3) == "meomeo meomeo meomeo nam"
    # Test single argument
    assert test_add_tool.run(5, 7) == 12
    print("   -> Result (Case 1): Success!")

    print("-- Case 2: ToolManager Registration and Retrieval")
    retrieved_tool = register.get_tool("print_meomeo")
    assert retrieved_tool.run("Dung", 1) == "meomeo Dung"
    
    # Test error on non-existent tool
    try:
        register.get_tool("non_existent_tool")
        assert False, "Should have raised ValueError"
    except ValueError:
        assert True
    print("   -> Result (Case 2): Success!")

    print("-- Case 3: ToolManager Description Formatting (Critical for Agent)")
    expected_description = (
        "- print_meomeo: tool that will return meomeo repeated N times with the given name.\n"
        "- simple_add: tool for adding two numbers."
    )
    assert register.get_descriptions() == expected_description
    print("   -> Result (Case 3): Success!")


    print("\n-- Case 4: BaseTool Error Handling (Division by Zero)")
    def problematic_func(a, b):
        """Always raises an error."""
        return a / b

    error_tool = BaseTool("error_div", problematic_func)
    error_result = error_tool.run(10, 0)
    assert "Error running tool 'error_div': division by zero" in error_result
    print("   -> Result (Case 4): Success!")


def test_concrete_tools_functionality():
    """Kiểm tra chức năng của các công cụ cụ thể: calculator và get_current_time."""
    print("\n-- Case 5: Calculator Tool")
    
    # Addition
    assert calculator('add', 10, 5, 2) == 17
    # Subtraction
    assert calculator('subtract', 10, 3) == 7
    # Multiplication
    assert calculator('multiply', 2, 3, 4) == 24
    # Division
    assert calculator('divide', 10, 2) == 5.0
    # Division by Zero Error
    assert calculator('divide', 10, 0) == "Cannot divide by zero."
    # Unsupported operation
    assert calculator('power', 2, 3) == "Unsupported operation: power"
    print("   -> Result (Case 5): Success!")


    print("\n-- Case 6: Get Current Time Tool")
    
    # Test specific components (exact numbers cannot be asserted, just types/ranges)
    now = datetime.datetime.now()
    assert isinstance(get_current_time('year'), int)
    assert get_current_time('year') == now.year
    assert get_current_time('month') == now.month

    # Test default datetime format
    datetime_str = get_current_time()
    assert isinstance(datetime_str, str)
    # Check if the format matches YYYY-MM-DD HH:MM:SS
    assert len(datetime_str) == 19 and datetime_str[4] == '-'
    
    # Test unsupported component
    assert "Unsupported time component" in get_current_time('week')
    print("   -> Result (Case 6): Success!")
    
    
def test_final_answer():
    """Kiểm tra định dạng của công cụ Final_Answer."""
    print("\n-- Case 7: Final Answer Tool Formatting")

    # Case 7.1: Simple answer with no args
    result1 = Final_Answer("This is the final result.")
    assert result1 == "\n--- Final Answer: This is the final result. ---", "Wrong format"

    # Case 7.2: Answer with arguments (placeholder substitution)
    result2 = Final_Answer("Total cost is $@0 and the date is @1.", 100.50, "2025-01-01")
    assert result2 == "\n--- Final Answer: Total cost is $100.5 and the date is 2025-01-01. ---", "Failed to substitute arg into answer"
    print("   -> Result (Case 7): Success!")
    
    
def run_all_tests():
    """Runs all defined test functions."""
    try:
        test_tool_manager_registration()
        test_concrete_tools_functionality()
        test_final_answer()
        # You can add a test for run_sql_query here if you mock the DB interaction.
        print("\n*** ALL TESTS PASSED! ***")
    except AssertionError as e:
        print(f"\n*** TEST FAILED! ***")
        print(f"Assertion Error: {e}")
        
if __name__ == '__main__':
    run_all_tests()

