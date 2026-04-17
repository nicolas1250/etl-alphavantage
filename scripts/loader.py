import pandas as pd
import logging
from sqlalchemy import text
from database import engine

logger = logging.getLogger(__name__)

class Loader:

    def insertar_accion(self, symbol, nombre='', sector=''):
        """Inserta o actualiza una accion en la tabla acciones"""
        with engine.connect() as conn:
            result = conn.execute(text(
                'INSERT INTO acciones (symbol, nombre, sector) VALUES (:s, :n, :sec) '
                'ON CONFLICT (symbol) DO UPDATE SET nombre=EXCLUDED.nombre '
                'RETURNING id'
            ), {'s': symbol, 'n': nombre, 'sec': sector})
            conn.commit()
            return result.fetchone()[0]

    def cargar_precios(self, df, accion_id):
        """Carga DataFrame de precios en precios_diarios"""
        df_load = df[['fecha','open','high','low','close','volume']].copy()
        df_load['accion_id'] = accion_id
        df_load.to_sql('precios_diarios', engine, if_exists='append',
                        index=False, method='multi')
        logger.info(f'Cargados {len(df_load)} precios para accion_id={accion_id}')

    def cargar_indicadores(self, df, accion_id):
        """Carga indicadores tecnicos en indicadores_tecnicos"""
        cols = ['fecha','rsi','macd','macd_signal','sma_20','sma_50',
                'bb_upper','bb_lower','bb_middle']
        cols_disponibles = [c for c in cols if c in df.columns]
        df_ind = df[cols_disponibles].copy()
        df_ind['accion_id'] = accion_id
        df_ind.to_sql('indicadores_tecnicos', engine, if_exists='append',
                       index=False, method='multi')
        logger.info(f'Cargados {len(df_ind)} indicadores para accion_id={accion_id}')
