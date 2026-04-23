import ccxt
exchange = ccxt.binance()
target = 'fapiprivate_get_openalgoorders'
match = [m for m in dir(exchange) if target in m.lower()]
print(f"Buscando '{target}':")
for m in match:
    print(f" - {m}")

# Listar todos los que empiecen por fapiprivate_get
print("\nListando todos los 'fapiprivate_get_':")
fapi_gets = [m for m in dir(exchange) if m.startswith('fapiPrivateGet') or m.startswith('fapi_private_get')]
for m in fapi_gets[:20]: # Mostrar algunos
    print(f" - {m}")
