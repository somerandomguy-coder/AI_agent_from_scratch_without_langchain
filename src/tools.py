import math
import datetime
from typing import List, Any

class BaseTool:
    """
    A base class for all tools.
    The description of the tool is automatically taken from the function's docstring.
    """
    def __init__(self, name: str, func):
        """
        Initializes the tool.

        Args:
            name (str): The name of the tool.
            func (callable): The function that the tool will execute.
        """
        self.name = name
        self.description = func.__doc__
        self.func = func

    def run(self, *args):
        """Executes the tool's function with the given arguments."""
        try:
            return self.func(*args)
        except Exception as e:
            return f"Error running tool '{self.name}': {e}"

class ToolManager:
    """
    A registry to manage and retrieve tools.
    """
    def __init__(self):
        self.tools = {}

    def add_tool(self, tool: BaseTool):
        """Adds a tool to the manager."""
        if not isinstance(tool, BaseTool):
            raise TypeError("Only instances of BaseTool can be added.")
        self.tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> BaseTool:
        """Retrieves a tool by its name."""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")
        return tool

    def get_all_tools(self) -> List[BaseTool]:
        """Returns a list of all registered tools."""
        return list(self.tools.values())

    def get_descriptions(self) -> List[str]:
        """Returns a list of descriptions of all registered tools."""
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.get_all_tools()])
        return tool_descriptions

# --- Concrete Tool Implementations ---

def get_current_time(component: str = "datetime"):
    """
    Gets the current time or a specific component of the date.

    Args:
        component (str, optional): The component to return.
                                   Options are 'year', 'month', 'day', or 'datetime'.
                                   Defaults to 'datetime'.
    """
    now = datetime.datetime.now()
    if component == 'year':
        return now.year
    elif component == 'month':
        return now.month
    elif component == 'day':
        return now.day
    elif component == 'datetime':
        return now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return f"Unsupported time component: {component}. Options are 'year', 'month', 'day', or 'datetime'."


def calculator(operation: str, *args):
    """
    Performs basic mathematical operations (e.g., add, subtract, multiply, divide).

    The first argument should be the operation name (e.g., 'add'), and
    the rest are the numbers to operate on.
    """

    # We'll use a simple, safe set of operations

    if operation == 'add':
        return sum(args)
    elif operation == 'subtract':
        if len(args) != 2:
            return "Subtract requires exactly two arguments."
        return args[0] - args[1]
    elif operation == 'multiply':
        result = 1
        for num in args:
            result *= num
        return result
    elif operation == 'divide':
        if len(args) != 2:
            return "Divide requires exactly two arguments."
        if args[1] == 0:
            return "Cannot divide by zero."
        return args[0] / args[1]
    else:
        return f"Unsupported operation: {operation}"

def run_sql_query(query: str, params: tuple = (), db_file="sales_data.db"):
    """
    Executes a SQL query on the specified SQLite database file using parameterized queries
    and returns the results. This prevents SQL injection vulnerabilities.

    Args:
        query (str): The SQL query string to execute, using '?' placeholders for parameters.
        params (tuple): A tuple of values to substitute into the query placeholders.
        db_file (str): The name of the database file.

    Returns:
        str: The query results formatted as a string, or an error message.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)

        # Use pandas.read_sql_query with the params argument for safe execution
        df = pd.read_sql_query(query, conn, params=params)

        # If the result is a single value, return it directly.
        if len(df) == 1 and len(df.columns) == 1:
            return df.iloc[0, 0]

        # Otherwise, return the results as a string
        return df.to_string()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    except pd.io.sql.DatabaseError as e:
        return f"Query execution error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        if conn:
            conn.close()

def Final_Answer(answer: str, *arg):
    """
    Print the final answer to the user.

    Args:

        Answer (str): The answer to print to user, using '@' placeholders for parameters.
        The rest are the parameters to substitute into the query placeholders.
    """
    if len(arg) == 0:
        return f"\n--- Final Answer: {answer} ---"
    else:
        for i, a in enumerate(arg):
            answer = answer.replace(f"@{i}", str(a))
        return f"\n--- Final Answer: {answer} ---"
