import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/add")
async def add(a: float, b: float) -> float:
    return a + b

@app.get("/subtraction")
async def subtraction(a: float, b: float) -> float:
    return a - b

@app.get("/multiply")
async def multiply(a: float, b: float) -> float:
    return a * b

@app.get("/divide")
async def divide(a: float, b: float) -> float:
    return a / b

@app.get("/expression")
async def expression(a: float, b: float, op:str):
    if op == "+":
        return add(a, b)
    elif op == "-":
        return subtraction(a, b)
    elif op == "*":
        return multiply(a, b)
    elif op == "/":
        return divide(a, b)
    else:
        raise Exception()

@app.get("/complication")
async def complication(exp: str) -> float:
    # Убираем пробелы и %20
    exp = exp.replace(" ", "").replace("%20", "")

    # Обрабатываем скобки рекурсивно
    while '(' in exp:
        start = exp.rfind('(')
        end = exp.find(')', start)

        # Вычисляем выражение внутри скобок
        sub_result = await complication(exp[start + 1:end])

        # Заменяем скобочное выражение на результат
        exp = exp[:start] + str(sub_result) + exp[end + 1:]

    i = 0
    current_num = ""
    numbers = []
    operators = []

    while i < len(exp):
        if exp[i] in "+-*/":
            numbers.append(float(current_num))
            operators.append(exp[i])
            current_num = ""
        else:
            current_num += exp[i]
        i += 1

    numbers.append(float(current_num))

    # Сначала умножаем и делим
    i = 0
    while i < len(operators):
        if operators[i] in "*/":
            if operators[i] == "*":
                result = numbers[i] * numbers[i + 1]
            else:
                result = numbers[i] / numbers[i + 1]
            numbers[i] = result
            numbers.pop(i + 1)
            operators.pop(i)
        else:
            i += 1

    # Потом складываем и вычитаем
    result = numbers[0]
    for i in range(len(operators)):
        if operators[i] == "+":
            result += numbers[i + 1]
        else:
            result -= numbers[i + 1]

    return result

if __name__ == "__main__":
    uvicorn.run(app)
    # Проверка на http://localhost:8000/complication?exp=(1+5)* 6 + (4 - 6)/(8-3)
