# scanner

Scanner de oportunidades cripto orientado a setups de alta calidad.

## Objetivo
Construir una herramienta que no ejecute órdenes, sino que:
- escanee mercado en intervalos regulares
- detecte setups relevantes
- explique por qué una oportunidad entra o se descarta
- rankee activos por calidad de señal
- entregue salidas útiles para uso propio y futura monetización

## Primera dirección del proyecto
La primera versión va a enfocarse en un **scanner de reversión** inspirado en el trabajo del scalper, pero separado de la lógica de ejecución. La idea es reutilizar lo que ya funciona del research y convertirlo en inteligencia de mercado.

## MVP propuesto
### Entrada
- OHLCV de múltiples símbolos
- timeframes 5m y 15m
- universo inicial chico y líquido

### Proceso
- cálculo de stretch
- cálculo de zscore
- RSI de corto plazo y RSI de contexto
- score de calidad por setup
- descarte explícito con motivo

### Salida
- top setups detectados
- dirección sugerida
- score
- entry zone sugerida
- invalidación
- objetivo orientativo
- motivo de aceptación o descarte

## Formato de salida inicial
La primera versión útil puede generar:
- reporte en consola
- archivo markdown o texto
- json estructurado

Más adelante:
- dashboard web
- canal Discord o Telegram
- histórico de señales

## Principios del proyecto
- primero utilidad real, después producto bonito
- primero explicabilidad, después complejidad
- primero pocas señales buenas, después cobertura amplia
- no prometer resultados de trading, sino inteligencia de mercado

## Roadmap corto
### Fase 1
- scaffold del proyecto
- config de símbolos y timeframes
- fetch básico de datos
- indicadores base

### Fase 2
- motor de scoring
- razones de descarte
- ranking de oportunidades

### Fase 3
- reportes legibles
- export json / markdown
- histórico simple

### Fase 4
- dashboard o canal de alertas
- métricas de calidad de señales
- refinamiento de producto
