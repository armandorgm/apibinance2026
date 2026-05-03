import asyncio
import ccxt.async_support as ccxt
import os
from json import dumps

async def main():
    exchange = ccxt.binance()
    # Ver la definición de la API en CCXT
    # Esto nos dirá qué endpoints están mapeados
    print(dumps(exchange.api['fapi']['private']['get'], indent=2))
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
