import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Transformador:

    def transformar_precios(self, raw_data, symbol):
        """Normaliza TIME_SERIES_DAILY a DataFrame estructurado"""
        try:
            ts = raw_data.get('Time Series (Daily)', {})
            records = []
            for fecha, valores in ts.items():
                records.append({
                    'symbol': symbol,
                    'fecha':  fecha,
                    'open':   float(valores['1. open']),
                    'high':   float(valores['2. high']),
                    'low':    float(valores['3. low']),
                    'close':  float(valores['4. close']),
                    'volume': int(valores['5. volume'])
                })
            df = pd.DataFrame(records)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha').reset_index(drop=True)
            # Calcular variacion diaria
            df['daily_return'] = df['close'].pct_change() * 100
            # Calcular rango (volatilidad intradiaria)
            df['price_range']  = df['high'] - df['low']
            logger.info(f'Precios {symbol}: {len(df)} registros transformados')
            return df
        except Exception as e:
            logger.error(f'Error transformando precios {symbol}: {e}')
            return None

    def transformar_rsi(self, raw_data, symbol):
        """Normaliza RSI a DataFrame"""
        try:
            ts = raw_data.get('Technical Analysis: RSI', {})
            records = [{'symbol': symbol, 'fecha': f, 'rsi': float(v['RSI'])}
                       for f, v in ts.items()]
            df = pd.DataFrame(records)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df.sort_values('fecha').reset_index(drop=True)
        except Exception as e:
            logger.error(f'Error transformando RSI {symbol}: {e}')
            return None

    def transformar_macd(self, raw_data, symbol):
        """Normaliza MACD a DataFrame"""
        try:
            ts = raw_data.get('Technical Analysis: MACD', {})
            records = [{
                'symbol':      symbol,
                'fecha':       f,
                'macd':        float(v['MACD']),
                'macd_signal': float(v['MACD_Signal']),
                'macd_hist':   float(v['MACD_Hist'])
            } for f, v in ts.items()]
            df = pd.DataFrame(records)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df.sort_values('fecha').reset_index(drop=True)
        except Exception as e:
            logger.error(f'Error transformando MACD {symbol}: {e}')
            return None

    def transformar_bollinger(self, raw_data, symbol):
        """Normaliza Bollinger Bands a DataFrame"""
        try:
            ts = raw_data.get('Technical Analysis: BBANDS', {})
            records = [{
                'symbol':    symbol,
                'fecha':     f,
                'bb_upper':  float(v['Real Upper Band']),
                'bb_middle': float(v['Real Middle Band']),
                'bb_lower':  float(v['Real Lower Band'])
            } for f, v in ts.items()]
            df = pd.DataFrame(records)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df.sort_values('fecha').reset_index(drop=True)
        except Exception as e:
            logger.error(f'Error transformando Bollinger {symbol}: {e}')
            return None

    def combinar_datasets(self, precios, rsi, macd, bollinger, sma_20, sma_50):
        """Une todos los DataFrames en uno maestro por fecha"""
        df = precios.copy()
        for df_ind, sufijo in [(rsi, None), (macd, None),
                               (bollinger, None), (sma_20, 'sma20'),
                               (sma_50, 'sma50')]:
            if df_ind is not None:
                cols_merge = [c for c in df_ind.columns if c not in ['symbol']]
                df = df.merge(df_ind[['fecha'] + [c for c in cols_merge if c != 'fecha']],
                              on='fecha', how='left')
        df = df.dropna().reset_index(drop=True)
        logger.info(f'Dataset combinado: {len(df)} filas, {len(df.columns)} columnas')
        return df
