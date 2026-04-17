#!/usr/bin/env python3
"""Pipeline ETL completo: Alpha Vantage -> PostgreSQL"""
import json, logging
from extractor  import AlphaVantageExtractor
from transformador import Transformador
from loader     import Loader
from database   import test_connection

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/etl.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def run():
    logger.info('=== INICIANDO PIPELINE ETL ===')
    test_connection()

    extractor    = AlphaVantageExtractor()
    transformador = Transformador()
    loader       = Loader()

    datos_raw = extractor.ejecutar_extraccion_completa()

    for symbol, datos in datos_raw.items():
        logger.info(f'--- Procesando {symbol} ---')

        if not datos['precios']:
            logger.warning(f'Sin precios para {symbol}, saltando.')
            continue

        # TRANSFORM
        df_precios   = transformador.transformar_precios(datos['precios'], symbol)
        df_rsi       = transformador.transformar_rsi(datos['rsi'], symbol) if datos['rsi'] else None
        df_macd      = transformador.transformar_macd(datos['macd'], symbol) if datos['macd'] else None
        df_bb        = transformador.transformar_bollinger(datos['bollinger'], symbol) if datos['bollinger'] else None

        df_maestro   = transformador.combinar_datasets(
            df_precios, df_rsi, df_macd, df_bb, None, None
        )

        # LOAD
        accion_id = loader.insertar_accion(symbol, nombre=symbol, sector='Technology')
        loader.cargar_precios(df_maestro, accion_id)
        loader.cargar_indicadores(df_maestro, accion_id)

        # Guardar CSV local tambien
        df_maestro.to_csv(f'data/{symbol}_maestro.csv', index=False)
        logger.info(f'CSV guardado: data/{symbol}_maestro.csv')

    logger.info('=== PIPELINE ETL COMPLETADO ===')

if __name__ == '__main__':
    run()
