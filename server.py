# server.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
from flask import Flask, render_template, request, send_file
import os
import math

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
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
            'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
            'pi': np.pi, 'e': np.e
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
        if not np.isnan(y):
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
    if not np.isnan(y0):
        integral += y0 / 2
    
    # Последняя точка
    yn = safe_eval(expr, b)
    if not np.isnan(yn):
        integral += yn / 2
    
    # Промежуточные точки
    for i in range(1, n):
        x = a + i * h
        y = safe_eval(expr, x)
        if not np.isnan(y):
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
    if not np.isnan(y0):
        integral += y0
    
    # Последняя точка
    yn = safe_eval(expr, b)
    if not np.isnan(yn):
        integral += yn
    
    # Промежуточные точки
    for i in range(1, n):
        x = a + i * h
        y = safe_eval(expr, x)
        if not np.isnan(y):
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
    x_random = np.random.uniform(a, b, n)
    y_values = []
    for x in x_random:
        y = safe_eval(expr, x)
        if not np.isnan(y):
            y_values.append(y)
    
    if len(y_values) > 0:
        integral = (b - a) * np.mean(y_values)
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
        if not np.isnan(y):
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
    integral_values = []
    execution_times = []
    method_names = []
    
    for method_name, method_func in methods:
        if method_name == "Метод Монте-Карло":
            integral, exec_time = method_func(func_expr, a, b, n * 10)
        else:
            integral, exec_time = method_func(func_expr, a, b, n)
        
        results.append({
            'method': method_name,
            'value': integral,
            'time': exec_time
        })
        
        integral_values.append(integral)
        execution_times.append(exec_time)
        method_names.append(method_name)
    
    return results, method_names, integral_values, execution_times

def create_function_plot(func_expr, a, b, n_points=1000):
    """Создание графика функции с заливкой площади под кривой"""
    plt.figure(figsize=(12, 8))
    
    # Генерируем точки для графика
    x_vals = np.linspace(a, b, n_points)
    y_vals = [safe_eval(func_expr, x) for x in x_vals]
    
    # Фильтруем валидные значения
    valid_indices = [i for i, y in enumerate(y_vals) if not np.isnan(y)]
    if not valid_indices:
        plt.text(0.5, 0.5, 'Функция не может быть отображена\nна заданном интервале', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.title(f'График функции: {func_expr}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('graph0_function_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        return
    
    x_valid = [x_vals[i] for i in valid_indices]
    y_valid = [y_vals[i] for i in valid_indices]
    
    # Создаем график
    plt.plot(x_valid, y_valid, 'b-', linewidth=2, label=f'f(x) = {func_expr}')
    
    # Заливаем площадь под кривой
    plt.fill_between(x_valid, y_valid, alpha=0.3, color='blue', label='Площадь под кривой')
    
    # Настраиваем график
    plt.title(f'График функции: {func_expr}', fontsize=16, fontweight='bold')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Добавляем информацию об интеграле
    plt.text(0.02, 0.98, f'∫{func_expr}dx\nот {a} до {b}', 
             transform=plt.gca().transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=12)
    
    plt.tight_layout()
    plt.savefig('graph0_function_plot.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_separate_plots(method_names, integral_values, execution_times, func_expr, a, b):
    """Создание отдельных графиков сравнения методов"""
    plt.style.use('default')
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # График 1: Сравнение значений интеграла
    plt.figure(figsize=(12, 8))
    valid_values = [(i, v) for i, v in enumerate(integral_values) if not np.isnan(v)]
    
    if valid_values:
        indices, values = zip(*valid_values)
        bars = plt.bar([method_names[i] for i in indices], values, 
                      color=[colors[i] for i in indices], alpha=0.8)
        
        plt.title(f'Сравнение значений интеграла\n∫{func_expr}dx от {a} до {b}', 
                 fontsize=14, fontweight='bold')
        plt.ylabel('Значение интеграла')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2., value + max(values)*0.01,
                    f'{value:.6f}', ha='center', va='bottom', fontsize=10)
    else:
        plt.text(0.5, 0.5, 'Ни один метод не смог вычислить интеграл', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.title(f'Сравнение значений интеграла', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graph1_integral_values.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # График 2: Время выполнения методов
    plt.figure(figsize=(12, 8))
    bars = plt.bar(method_names, execution_times, color=colors, alpha=0.8)
    plt.title('Время выполнения методов', fontsize=14, fontweight='bold')
    plt.ylabel('Время (секунды)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(execution_times)*0.01,
                f'{height:.6f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('graph2_execution_times.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # График 3: Сравнение методов (нормализованные значения)
    plt.figure(figsize=(12, 8))
    valid_values = [v for v in integral_values if not np.isnan(v)]
    
    if len(valid_values) > 1:
        min_val, max_val = min(valid_values), max(valid_values)
        if max_val - min_val > 1e-10:
            normalized_values = [(v - min_val) / (max_val - min_val) if not np.isnan(v) else 0 
                               for v in integral_values]
        else:
            normalized_values = [0.5 if not np.isnan(v) else 0 for v in integral_values]
        
        bars = plt.bar(method_names, normalized_values, color=colors, alpha=0.8)
        plt.title('Сравнение методов (нормализованные значения)', fontsize=14, fontweight='bold')
        plt.ylabel('Нормализованное значение')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if not np.isnan(integral_values[i]):
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{normalized_values[i]:.3f}', ha='center', va='bottom', fontsize=10)
    else:
        plt.text(0.5, 0.5, 'Недостаточно данных\nдля сравнения методов', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.title('Сравнение методов', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graph3_methods_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # График 4: Эффективность методов (значение/время)
    plt.figure(figsize=(12, 8))
    efficiency = []
    for i in range(len(method_names)):
        if not np.isnan(integral_values[i]) and execution_times[i] > 0:
            efficiency.append(abs(integral_values[i]) / execution_times[i])
        else:
            efficiency.append(float('nan'))
    
    if any(not np.isnan(eff) for eff in efficiency):
        valid_eff = [eff for eff in efficiency if not np.isnan(eff)]
        if valid_eff:
            bars = plt.bar(method_names, efficiency, color=colors, alpha=0.8)
            plt.title('Эффективность методов (|значение|/время)', fontsize=14, fontweight='bold')
            plt.ylabel('Эффективность')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if not np.isnan(height):
                    plt.text(bar.get_x() + bar.get_width()/2., height + max(valid_eff)*0.01,
                            f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    else:
        plt.text(0.5, 0.5, 'Недостаточно данных\nдля вычисления эффективности', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        plt.title('Эффективность методов', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graph4_efficiency.png', dpi=300, bbox_inches='tight')
    plt.close()

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
                if not np.isnan(y):
                    valid_points += 1
            except:
                pass
        
        if valid_points == 0:
            return "Ошибка: функция не может быть вычислена на заданном интервале"
        
        # Создаем график функции
        create_function_plot(func_expr, a, b)
        
        # Вычисляем интеграл
        results, method_names, integral_values, execution_times = calculate_integral(func_expr, a, b, n)
        create_separate_plots(method_names, integral_values, execution_times, display_expr, a, b)
        
        # Создаем таблицу времени выполнения
        time_table_data = []
        for i, result in enumerate(results):
            time_table_data.append({
                'method': result['method'],
                'time': result['time'],
                'value': result['value']
            })
        
        # Сортируем по времени выполнения
        time_table_data.sort(key=lambda x: x['time'])
        
        return render_template('index.html', 
                             results=results, 
                             func_expr=display_expr,
                             a=a, b=b, n=n,
                             functions=FUNCTIONS,
                             func_type=func_type,
                             time_table=time_table_data)
    
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

@app.route('/graph/<int:graph_num>')
def get_graph(graph_num):
    graph_files = {
        0: 'graph0_function_plot.png',
        1: 'graph1_integral_values.png',
        2: 'graph2_execution_times.png', 
        3: 'graph3_methods_comparison.png',
        4: 'graph4_efficiency.png'
    }
    
    if graph_num in graph_files:
        return send_file(graph_files[graph_num], mimetype='image/png')
    else:
        return "График не найден", 404

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5000)