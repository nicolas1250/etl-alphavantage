import os, time, requests, json, logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlphaVantageExtractor:
    def __init__(self):
        self.api_key  = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = os.getenv('ALPHA_VANTAGE_BASE_URL')
        self.symbols  = os.getenv('SYMBOLS').split(',')
        if not self.api_key:
            raise ValueError('ALPHA_VANTAGE_API_KEY no configurada')

    def _get(self, params):
        """Realiza una peticion GET a la API con manejo de errores"""
        try:
            params['apikey'] = self.api_key
            r = requests.get(self.base_url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            if 'Error Message' in data or 'Note' in data:
                logger.warning(f'Respuesta API: {data}')
                return None
            return data
        except Exception as e:
            logger.error(f'Error en peticion: {e}')
            return None

    def extraer_precios(self, symbol):
        """Extrae TIME_SERIES_DAILY para un simbolo"""
        logger.info(f'Extrayendo precios: {symbol}')
        return self._get({
            'function': 'TIME_SERIES_DAILY',
            'symbol':   symbol,
            'outputsize': 'compact'  # ultimos 100 dias
        })

    def extraer_rsi(self, symbol):
        """Extrae RSI diario para un simbolo"""
        logger.info(f'Extrayendo RSI: {symbol}')
        return self._get({
            'function':   'RSI',
            'symbol':     symbol,
            'interval':   'daily',
            'time_period': 14,
            'series_type': 'close'
        })

    def extraer_macd(self, symbol):
        """Extrae MACD diario para un simbolo"""
        logger.info(f'Extrayendo MACD: {symbol}')
        return self._get({
            'function':    'MACD',
            'symbol':      symbol,
            'interval':    'daily',
            'series_type': 'close'
        })

    def extraer_bollinger(self, symbol):
        """Extrae Bollinger Bands diarias"""
        logger.info(f'Extrayendo Bollinger Bands: {symbol}')
        return self._get({
            'function':    'BBANDS',
            'symbol':      symbol,
            'interval':    'daily',
            'time_period': 20,
            'series_type': 'close'
        })

    def extraer_sma(self, symbol, period=20):
        """Extrae SMA (Simple Moving Average)"""
        logger.info(f'Extrayendo SMA-{period}: {symbol}')
        return self._get({
            'function':    'SMA',
            'symbol':      symbol,
            'interval':    'daily',
            'time_period': period,
            'series_type': 'close'
        })

    def ejecutar_extraccion_completa(self):
        """Extrae todos los datos para todos los simbolos."""
        resultados = {}
        for symbol in self.symbols:
            logger.info(f'--- Procesando {symbol} ---')
            resultados[symbol] = {
                'precios':   self.extraer_precios(symbol),
                'rsi':       self.extraer_rsi(symbol),
                'macd':      self.extraer_macd(symbol),
                'bollinger': self.extraer_bollinger(symbol),
                'sma_20':    self.extraer_sma(symbol, 20),
                'sma_50':    self.extraer_sma(symbol, 50),
            }
            # IMPORTANTE: respetar limite de 5 req/min del plan Free
            logger.info(f'Esperando 15 segundos (limite API)...')
            time.sleep(15)
        return resultados