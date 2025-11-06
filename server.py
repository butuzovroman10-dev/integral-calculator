# server.py
from flask import Flask, request, jsonify, render_template
import sympy as sp
import numpy as np
import time
import os
import math
import json

app = Flask(__name__)

# Словарь доступных функций
FUNCTIONS = {
    'x^2': 'x**2',
    'x^3': 'x**3', 
    'sin(x)': 'sin(x)',
    'cos(x)': 'cos(x)',
    'tan(x)': 'tan(x)',
    'exp(x)': 'exp(x)',
    'ln(x)': 'log(x)',
    'sqrt(x)': 'sqrt(x)',
    '1/x': '1/x',
    'sinh(x)': 'sinh(x)',
    'cosh(x)': 'cosh(x)',
    'tanh(x)': 'tanh(x)',
    'e^(-x^2)': 'exp(-x**2)',
    'sin(x)/x': 'sin(x)/x if x != 0 else 1',
    'x*sin(x)': 'x*sin(x)',
    'x*cos(x)': 'x*cos(x)'
}

def safe_eval(expr, x):
    """Безопасное вычисление математического выражения"""
    try:
        # Создаем безопасное окружение для eval
        safe_dict = {
            'x': x,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
            'pi': math.pi, 'e': math.e
        }
        return eval(expr, {"__builtins__": {}}, safe_dict)
    except:
        return float('nan')

def rectangle_method(expr, a, b, n):
    """Метод прямоугольников (средних)"""
    start_time = time.time()
    h = (b - a) / n
    integral = 0
    for i in range(n):
        x = a + (i + 0.5) * h
        y = safe_eval(expr, x)
        if not math.isnan(y):
            integral += y
    integral *= h
    end_time = time.time()
    return integral, end_time - start_time

def trapezoidal_method(expr, a, b, n):
    """Метод трапеций"""
    start_time = time.time()
    h = (b - a) / n
    integral = 0
    
    # Первая точка
    y0 = safe_eval(expr, a)
    if not math.isnan(y0):
        integral += y0 / 2
    
    # Последняя точка
    yn = safe_eval(expr, b)
    if not math.isnan(yn):
        integral += yn / 2
    
    # Промежуточные точки
    for i in range(1, n):
        x = a + i * h
        y = safe_eval(expr, x)
        if not math.isnan(y):
            integral += y
    
    integral *= h
    end_time = time.time()
    return integral, end_time - start_time

def simpson_method(expr, a, b, n):
    """Метод Симпсона"""
    if n % 2 != 0:
        n += 1
    start_time = time.time()
    h = (b - a) / n
    integral = 0
    
    # Первая точка
    y0 = safe_eval(expr, a)
    if not math.isnan(y0):
        integral += y0
    
    # Последняя точка
    yn = safe_eval(expr, b)
    if not math.isnan(yn):
        integral += yn
    
    # Промежуточные точки
    for i in range(1, n):
        x = a + i * h
        y = safe_eval(expr, x)
        if not math.isnan(y):
            if i % 2 == 0:
                integral += 2 * y
            else:
                integral += 4 * y
    
    integral *= h / 3
    end_time = time.time()
    return integral, end_time - start_time

def monte_carlo_method(expr, a, b, n):
    """Метод Монте-Карло"""
    start_time = time.time()
    
    # Используем встроенный random вместо numpy
    import random
    x_random = [random.uniform(a, b) for _ in range(n)]
    y_values = []
    
    for x in x_random:
        y = safe_eval(expr, x)
        if not math.isnan(y):
            y_values.append(y)
    
    if len(y_values) > 0:
        integral = (b - a) * sum(y_values) / len(y_values)
    else:
        integral = float('nan')
    
    end_time = time.time()
    return integral, end_time - start_time

def gauss_quadrature(expr, a, b, n_points=5):
    """Метод Гауссовой квадратуры"""
    start_time = time.time()
    
    if n_points == 2:
        points = [-0.57735027, 0.57735027]
        weights = [1.0, 1.0]
    elif n_points == 3:
        points = [-0.77459667, 0, 0.77459667]
        weights = [0.55555556, 0.88888889, 0.55555556]
    elif n_points == 4:
        points = [-0.86113631, -0.33998104, 0.33998104, 0.86113631]
        weights = [0.34785485, 0.65214515, 0.65214515, 0.34785485]
    else:
        points = [-0.90617985, -0.53846931, 0, 0.53846931, 0.90617985]
        weights = [0.23692689, 0.47862867, 0.56888889, 0.47862867, 0.23692689]
    
    integral = 0
    valid_points = 0
    for i in range(len(points)):
        x = (b - a) / 2 * points[i] + (a + b) / 2
        y = safe_eval(expr, x)
        if not math.isnan(y):
            integral += weights[i] * y
            valid_points += 1
    
    if valid_points > 0:
        integral *= (b - a) / 2
    else:
        integral = float('nan')
    
    end_time = time.time()
    return integral, end_time - start_time

def calculate_integral(func_expr, a, b, n):
    """Вычисление интеграла всеми методами"""
    
    methods = [
        ("Метод прямоугольников", rectangle_method),
        ("Метод трапеций", trapezoidal_method), 
        ("Метод Симпсона", simpson_method),
        ("Метод Монте-Карло", monte_carlo_method),
        ("Метод Гаусса", gauss_quadrature)
    ]
    
    results = []
    
    for method_name, method_func in methods:
        if method_name == "Метод Монте-Карло":
            integral, exec_time = method_func(func_expr, a, b, n * 10)
        else:
            integral, exec_time = method_func(func_expr, a, b, n)
        
        results.append({
            'method': method_name,
            'value': integral if not math.isnan(integral) else 'Не удалось вычислить',
            'time': f"{exec_time:.6f} сек"
        })
    
    return results

@app.route('/')
def index():
    return render_template('index.html', functions=FUNCTIONS)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        func_type = request.form['func_type']
        
        if func_type == 'preset':
            func_name = request.form['function']
            func_expr = FUNCTIONS[func_name]
            display_expr = func_name
        else:  # custom
            func_expr = request.form['custom_function']
            display_expr = func_expr
        
        a = float(request.form['a'])
        b = float(request.form['b'])
        n = int(request.form['n'])
        
        if a >= b:
            return "Ошибка: нижний предел должен быть меньше верхнего предела"
        
        # Проверяем функцию на нескольких точках
        test_points = [a, (a+b)/2, b]
        valid_points = 0
        for x in test_points:
            try:
                y = safe_eval(func_expr, x)
                if not math.isnan(y):
                    valid_points += 1
            except:
                pass
        
        if valid_points == 0:
            return "Ошибка: функция не может быть вычислена на заданном интервале"
        
        # Вычисляем интеграл
        results = calculate_integral(func_expr, a, b, n)
        
        return render_template('index.html', 
                             results=results, 
                             func_expr=display_expr,
                             a=a, b=b, n=n,
                             functions=FUNCTIONS,
                             func_type=func_type)
    
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API endpoint для вычисления интеграла"""
    try:
        data = request.get_json()
        
        func_expr = data.get('function')
        a = float(data.get('a'))
        b = float(data.get('b'))
        n = int(data.get('n', 1000))
        
        results = calculate_integral(func_expr, a, b, n)
        
        return jsonify({
            'success': True,
            'function': func_expr,
            'interval': [a, b],
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Integral Calculator API is running"})

if __name__ == '__main__':
    # Создаем папку templates если её нет
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=False, host='0.0.0.0', port=5000)