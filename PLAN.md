# PLAN.md

## Producto
Scanner premium de setups cripto, sin ejecución automática.

## Usuario objetivo
1. uso interno para operar mejor
2. posible producto para traders que quieran alertas filtradas

## Qué reutilizar del scalper
Del trabajo ya hecho en `luca123` conviene reutilizar ideas, no copiar todo ciegamente:
- score de setup
- stretch respecto de VWAP
- zscore
- RSI 5m
- RSI de contexto 15m
- lógica de descarte explícito

## Qué NO traer en la primera versión
- ejecución de órdenes
- manejo de posiciones
- trailing / TP / SL automáticos
- base de datos compleja
- multiusuario

## MVP técnico
### módulos
- `config.py`
- `data_fetcher.py`
- `indicators.py`
- `signal_engine.py`
- `report.py`
- `main.py`

### salida mínima
Cada ciclo debe producir:
- mejores setups
- activos descartados con motivo
- score
- dirección
- métricas base

## Criterio de éxito del MVP
El scanner sirve si al usarlo durante varios días:
- reduce ruido
- detecta pocas oportunidades pero legibles
- explica por qué una señal existe
- permite revisar qué se descartó y por qué

## Próximo paso recomendado
Armar el esqueleto del proyecto y dejar corriendo una primera versión local que escanee un universo chico.
