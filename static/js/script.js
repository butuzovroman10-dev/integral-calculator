class ComprehensiveIntegralCalculator {
    constructor() {
        this.initializeEventListeners();
        this.loadExamples();
    }

    initializeEventListeners() {
        document.getElementById('calculateBtn').addEventListener('click', () => this.calculate());
        document.getElementById('clearBtn').addEventListener('click', () => this.clear());
        document.getElementById('examplesBtn').addEventListener('click', () => this.toggleExamples());
        
        document.getElementById('functionInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.calculate();
        });
    }

    async calculate() {
        const functionInput = document.getElementById('functionInput').value.trim();
        const lowerLimit = document.getElementById('lowerLimit').value.trim() || '0';
        const upperLimit = document.getElementById('upperLimit').value.trim() || '1';

        if (!functionInput) {
            this.showResult('error', 'Введите функцию для интегрирования');
            return;
        }

        this.showResult('loading', 'Вычисление всеми методами...');

        try {
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    function: functionInput,
                    lower_limit: lowerLimit,
                    upper_limit: upperLimit
                })
            });

            const data = await response.json();
            data.success ? this.displayAllResults(data) : this.showResult('error', data.error);
            
        } catch (error) {
            this.showResult('error', 'Ошибка соединения с сервером');
            console.error('Error:', error);
        }
    }

    displayAllResults(data) {
        this.displaySummaryTable(data);
        this.displayDetailedTable(data);
        this.displayPlot(data.function_plot, 'plotContainer');
        this.displayPlot(data.comparison_plot, 'comparisonPlotContainer');
    }

    displaySummaryTable(data) {
        const validResults = data.results.filter(r => r.success);
        const analyticalResult = validResults.find(r => r.method === 'Аналитический');
        const numericalResults = validResults.filter(r => r.method !== 'Аналитический');
        
        // Находим лучший численный метод
        const bestNumerical = numericalResults.reduce((best, current) => {
            return current.error < best.error ? current : best;
        }, numericalResults[0]);

        let summaryHTML = `
            <div class="summary-result">
                <h4>📈 Сводные результаты</h4>
                ${analyticalResult ? `
                    <div class="analytical-info">
                        <p><strong>Аналитическое значение:</strong> ${analyticalResult.value}</p>
                        <p><strong>Время вычисления:</strong> ${analyticalResult.time.toFixed(6)} с</p>
                    </div>
                ` : ''}
                
                <div class="best-method">
                    <h5>🏆 Лучший численный метод: ${bestNumerical.method}</h5>
                    <p><strong>Значение:</strong> ${bestNumerical.value.toFixed(8)}</p>
                    <p><strong>Погрешность:</strong> ${bestNumerical.error.toFixed(8)}</p>
                    <p><strong>Время:</strong> ${bestNumerical.time.toFixed(6)} с</p>
                </div>

                <div class="methods-ranking">
                    <h5>📊 Рейтинг методов по точности:</h5>
                    <ol>
        `;

        // Сортируем по погрешности (возрастание)
        const sortedByAccuracy = [...numericalResults].sort((a, b) => a.error - b.error);
        sortedByAccuracy.forEach((result, index) => {
            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`;
            summaryHTML += `
                <li>${medal} ${result.method}: погрешность = ${result.error.toFixed(8)}</li>
            `;
        });

        summaryHTML += `
                    </ol>
                </div>
            </div>
        `;

        this.showResult('success', summaryHTML);
    }

    displayDetailedTable(data) {
        const tableBody = document.getElementById('comparisonBody');
        tableBody.innerHTML = '';
        
        const validResults = data.results.filter(r => r.success);
        const analyticalResult = validResults.find(r => r.method === 'Аналитический');
        
        validResults.forEach(result => {
            const relativeError = analyticalResult ? 
                (result.error / Math.abs(analyticalResult.value) * 100).toFixed(6) + '%' : 'N/A';
            
            const row = `
                <tr class="${result.method === 'Аналитический' ? 'reference-row' : ''}">
                    <td><strong>${result.method}</strong></td>
                    <td>${result.method === 'Аналитический' ? result.value : result.value.toFixed(8)}</td>
                    <td>${result.time.toFixed(6)}</td>
                    <td>${result.method === 'Аналитический' ? '0' : result.error.toFixed(8)}</td>
                    <td>${result.method === 'Аналитический' ? '0%' : relativeError}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });

        document.getElementById('comparisonSection').style.display = 'block';
    }

    displayPlot(plotData, containerId) {
        if (plotData) {
            const container = document.getElementById(containerId);
            container.innerHTML = `<img src="data:image/png;base64,${plotData}" alt="График" style="width: 100%; height: auto; border-radius: 10px;">`;
        }
    }

    showResult(type, message) {
        const resultElement = document.getElementById('resultOutput');
        resultElement.innerHTML = message;
        resultElement.className = `result-output ${type}`;
    }

    async loadExamples() {
        try {
            const response = await fetch('/examples');
            const examples = await response.json();
            this.displayExamples(examples);
        } catch (error) {
            console.error('Error loading examples:', error);
        }
    }

    displayExamples(examples) {
        const examplesBody = document.getElementById('examplesBody');
        examplesBody.innerHTML = '';
        
        examples.forEach(example => {
            const row = `
                <tr>
                    <td><code>${example.function}</code></td>
                    <td>[${example.lower}, ${example.upper}]</td>
                    <td>${example.description}</td>
                    <td>
                        <button class="example-use-btn" 
                                onclick="calculator.useExample('${example.function}', '${example.lower}', '${example.upper}')">
                            Использовать
                        </button>
                    </td>
                </tr>
            `;
            examplesBody.innerHTML += row;
        });
    }

    useExample(func, lower, upper) {
        document.getElementById('functionInput').value = func;
        document.getElementById('lowerLimit').value = lower;
        document.getElementById('upperLimit').value = upper;
        this.hideExamples();
    }

    toggleExamples() {
        const examplesSection = document.getElementById('examplesSection');
        examplesSection.style.display = examplesSection.style.display === 'block' ? 'none' : 'block';
    }

    hideExamples() {
        document.getElementById('examplesSection').style.display = 'none';
    }

    clear() {
        document.getElementById('functionInput').value = '';
        document.getElementById('lowerLimit').value = '0';
        document.getElementById('upperLimit').value = '1';
        document.getElementById('resultOutput').innerHTML = '<div class="placeholder">Результаты появятся здесь...</div>';
        document.getElementById('resultOutput').className = 'result-output';
        document.getElementById('plotContainer').innerHTML = '<div class="placeholder">График появится здесь...</div>';
        document.getElementById('comparisonPlotContainer').innerHTML = '<div class="placeholder">График сравнения появится здесь...</div>';
        document.getElementById('comparisonSection').style.display = 'none';
        document.getElementById('examplesSection').style.display = 'none';
    }
}

let calculator;
document.addEventListener('DOMContentLoaded', () => {
    calculator = new ComprehensiveIntegralCalculator();
});