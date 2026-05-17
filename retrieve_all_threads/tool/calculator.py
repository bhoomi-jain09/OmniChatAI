from langchain_core.tools import tool


@tool
def calculator(first_num: float, second_num: float, operation: str):
    """Tool for calculation: addition, subtraction, division and multiplication."""
    try:
        if operation == "addition":
            result = first_num + second_num
        elif operation == "subtraction":
            result = first_num - second_num
        elif operation == "multiplication":
            result = first_num * second_num
        elif operation == "division":
            if second_num == 0:
                return {"error": "Denominator cannot be zero."}
            result = first_num / second_num
        else:
            return {"error": f"Unknown operation: {operation}. Use addition, subtraction, multiplication, or division."}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}
