import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
import pytz

# Definir end_date al inicio del script con UTC
end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.UTC)

def get_data(ticker):
    data = yf.Ticker(ticker)
    return data.info

def get_historical_data(ticker):
    global end_date
    start_date = end_date - timedelta(days=50)
    
    data = yf.Ticker(ticker)
    return data.history(start=start_date, end=end_date, interval='15m')

# Obtener datos de los últimos 50 días
datos_btc = get_historical_data('BTC-USD')

# Variables para la simulación
capital_inicial = 100000
capital_actual = capital_inicial
operaciones_realizadas = []

# Procesar cada día por separado
for dia in range(50):
    fecha_inicio = (end_date - timedelta(days=50-dia)).astimezone(pytz.UTC)
    fecha_fin = (fecha_inicio + timedelta(days=1)).astimezone(pytz.UTC)
    datos_dia = datos_btc[
        (datos_btc.index >= fecha_inicio) & 
        (datos_btc.index < fecha_fin)
    ]
    
    if len(datos_dia) == 0:
        continue

    tendencia_anterior = None
    expected_values = []
    
    # Calcular regresiones y tendencias
    for i in range(0, len(datos_dia)-1, 4):
        datos_intervalo = datos_dia.iloc[i:i+4]
        
        if len(datos_intervalo) > 1:
            X = np.arange(len(datos_intervalo)).reshape(-1, 1)
            y = datos_intervalo['Close'].values
            
            modelo = LinearRegression()
            modelo.fit(X, y)
            
            pendiente_actual = modelo.coef_[0]
            tendencia_actual = 'positiva' if pendiente_actual > 0 else 'negativa'
            
            if tendencia_anterior is not None:
                precio_entrada = datos_intervalo['Close'].iloc[0]
                
                # Decisión de trading basada en la tendencia anterior
                if tendencia_anterior == 'negativa':
                    # Invertimos cuando detectamos tendencia positiva
                    # y mantenemos hasta el final del intervalo
                    precio_salida = datos_intervalo['Close'].iloc[-1]
                    rendimiento_porcentual = ((precio_salida - precio_entrada) / precio_entrada) * 100
                    
                    # Aplicamos el rendimiento al capital (sea positivo o negativo)
                    ganancia = capital_actual * (rendimiento_porcentual / 100)
                    capital_actual += ganancia
                    
                    operaciones_realizadas.append({
                        'fecha': datos_intervalo.index[0],
                        'rendimiento': rendimiento_porcentual,
                        'capital_antes': capital_actual - ganancia,
                        'capital_despues': capital_actual,
                        'precio_entrada': precio_entrada,
                        'precio_salida': precio_salida,
                        'tendencia_detectada': tendencia_anterior,
                        'pendiente_decision': pendiente_anterior
                    })
            
            tendencia_anterior = tendencia_actual
            pendiente_anterior = pendiente_actual

# Imprimir resultados finales
retorno_total = ((capital_actual - capital_inicial) / capital_inicial) * 100
print(f"\nSimulación de Trading con ${capital_inicial} iniciales:")
print(f"Capital final: ${capital_actual:.2f}")
print(f"Retorno total: {retorno_total:.2f}%")
print(f"Número de operaciones: {len(operaciones_realizadas)}")

# Log detallado de operaciones
print("\nLog de operaciones:")
print("-" * 120)
print(f"{'Fecha':25} {'Capital Inicial':>15} {'Capital Final':>15} {'Diferencia':>12} {'Rendimiento':>12} {'Precio Entrada':>12} {'Precio Salida':>12} {'Pendiente':>10}")
print("-" * 120)

for op in operaciones_realizadas:
    fecha = op['fecha'].strftime('%Y-%m-%d %H:%M')
    capital_antes = op['capital_antes']
    capital_despues = op['capital_despues']
    diferencia = capital_despues - capital_antes
    rendimiento = op['rendimiento']
    precio_entrada = op['precio_entrada']
    precio_salida = op['precio_salida']
    pendiente = op['pendiente_decision']
    
    print(f"{fecha:<25} ${capital_antes:>14.2f} ${capital_despues:>14.2f} ${diferencia:>11.2f} {rendimiento:>11.2f}% ${precio_entrada:>11.2f} ${precio_salida:>11.2f} {pendiente:>10.2f}")

print("-" * 120)

# Estadísticas adicionales
ganancias_totales = sum(op['capital_despues'] - op['capital_antes'] for op in operaciones_realizadas if op['capital_despues'] > op['capital_antes'])
perdidas_totales = sum(op['capital_despues'] - op['capital_antes'] for op in operaciones_realizadas if op['capital_despues'] < op['capital_antes'])
operaciones_ganadoras = sum(1 for op in operaciones_realizadas if op['capital_despues'] > op['capital_antes'])
operaciones_perdedoras = sum(1 for op in operaciones_realizadas if op['capital_despues'] < op['capital_antes'])

print(f"\nEstadísticas adicionales:")
print(f"Ganancias totales: ${ganancias_totales:.2f}")
print(f"Pérdidas totales: ${perdidas_totales:.2f}")
print(f"Operaciones ganadoras: {operaciones_ganadoras}")
print(f"Operaciones perdedoras: {operaciones_perdedoras}")
if operaciones_ganadoras > 0:
    print(f"Ganancia promedio por operación exitosa: ${ganancias_totales/operaciones_ganadoras:.2f}")
if operaciones_perdedoras > 0:
    print(f"Pérdida promedio por operación perdedora: ${perdidas_totales/operaciones_perdedoras:.2f}")