#!/usr/bin/env python3
"""
Script para obtener y gestionar Take Profit / Stop Loss pendientes en Binance Futures

Uso:
    python3 get_tp_sl.py --symbol BTCUSDT --action list
    python3 get_tp_sl.py --symbol ETHUSDT --action tp
    python3 get_tp_sl.py --symbol SOLUSDT --action sl
    python3 get_tp_sl.py --action all
"""

import requests
import time
import hmac
import hashlib
import json
import argparse
from typing import List, Dict, Optional
from datetime import datetime
from tabulate import tabulate  # pip install tabulate

class BinanceFuturesTPSL:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Inicializa la clase para obtener TP/SL de Binance Futures
        
        Args:
            api_key: Tu API Key de Binance
            api_secret: Tu API Secret de Binance
            testnet: Usar testnet de Binance (por defecto False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
    
    def _get_signature(self, query_string: str) -> str:
        """Genera firma HMAC SHA256"""
        return hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """
        Realiza una solicitud autenticada a la API de Binance
        
        Args:
            method: GET, POST, DELETE, PUT
            endpoint: Ruta del endpoint (ej: /fapi/v1/openAlgoOrders)
            params: Parámetros de la solicitud
        
        Returns:
            Respuesta JSON de la API
        """
        if params is None:
            params = {}
        
        # Agregar timestamp
        params["timestamp"] = int(time.time() * 1000)
        
        # Crear query string
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # Firmar
        params["signature"] = self._get_signature(query_string)
        
        # Headers
        headers = {"X-MBX-APIKEY": self.api_key}
        
        # URL completa
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, params=params, headers=headers)
            elif method == "PUT":
                response = requests.put(url, params=params, headers=headers)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la solicitud: {e}")
            if hasattr(e.response, 'text'):
                print(f"Respuesta: {e.response.text}")
            raise
    
    def get_pending_tp_sl(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Obtiene todos los TP/SL pendientes (órdenes algo abiertas)
        
        Args:
            symbol: Símbolo específico (ej: BTCUSDT) o None para todos
        
        Returns:
            Lista de órdenes algo pendientes
        """
        params = {}
        
        if symbol:
            params["symbol"] = symbol
        
        return self._request("GET", "/fapi/v1/openAlgoOrders", params)
    
    def get_take_profits(self, symbol: Optional[str] = None) -> List[Dict]:
        """Obtiene solo los Take Profits pendientes"""
        orders = self.get_pending_tp_sl(symbol)
        return [
            o for o in orders 
            if o['orderType'] in ['TAKE_PROFIT', 'TAKE_PROFIT_MARKET']
        ]
    
    def get_stop_losses(self, symbol: Optional[str] = None) -> List[Dict]:
        """Obtiene solo los Stop Loss pendientes"""
        orders = self.get_pending_tp_sl(symbol)
        return [
            o for o in orders 
            if o['orderType'] in ['STOP_MARKET', 'STOP']
        ]
    
    def cancel_tp_sl(self, algo_id: int) -> Dict:
        """
        Cancela un TP o SL específico
        
        Args:
            algo_id: ID del algo order a cancelar
        
        Returns:
            Respuesta de la API
        """
        params = {"algoId": algo_id}
        return self._request("DELETE", "/fapi/v1/algoOrder", params)
    
    def cancel_all_tp_sl(self, symbol: str) -> Dict:
        """
        Cancela todos los TP/SL de un símbolo
        
        Args:
            symbol: Símbolo del par (ej: BTCUSDT)
        
        Returns:
            Respuesta de la API
        """
        params = {"symbol": symbol}
        return self._request("DELETE", "/fapi/v1/algoOrdersAll", params)
    
    def format_order(self, order: Dict) -> Dict:
        """Formatea un orden para presentación"""
        return {
            "Símbolo": order['symbol'],
            "Tipo": "TP" if 'TAKE_PROFIT' in order['orderType'] else "SL",
            "Lado": order['side'],
            "Cantidad": float(order['quantity']),
            "Trigger Price": float(order['triggerPrice']),
            "Precio": float(order['price']) if order['price'] else "N/A",
            "Estado": order['algoStatus'],
            "Algo ID": order['algoId'],
            "Creado": datetime.fromtimestamp(order['createTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def print_table(self, orders: List[Dict]):
        """Imprime los órdenes en formato tabla"""
        if not orders:
            print("❌ No hay órdenes para mostrar")
            return
        
        formatted = [self.format_order(o) for o in orders]
        
        print("\n" + "=" * 140)
        print(tabulate(formatted, headers="keys", tablefmt="grid"))
        print("=" * 140 + "\n")
    
    def print_summary(self, symbol: Optional[str] = None):
        """Imprime un resumen detallado de TP/SL"""
        orders = self.get_pending_tp_sl(symbol)
        
        if not orders:
            print(f"\n✅ No hay TP/SL pendientes en {symbol or 'TODOS LOS PARES'}")
            return
        
        print("\n" + "=" * 100)
        print(f"RESUMEN DE TP/SL PENDIENTES - {symbol.upper() if symbol else 'TODOS LOS PARES'}")
        print("=" * 100)
        
        # Agrupar por símbolo
        by_symbol = {}
        for order in orders:
            sym = order['symbol']
            if sym not in by_symbol:
                by_symbol[sym] = {"TP": [], "SL": []}
            
            if 'TAKE_PROFIT' in order['orderType']:
                by_symbol[sym]["TP"].append(order)
            else:
                by_symbol[sym]["SL"].append(order)
        
        for sym, orders_data in sorted(by_symbol.items()):
            print(f"\n📊 {sym}")
            print("-" * 100)
            
            if orders_data["TP"]:
                print(f"  🎯 TAKE PROFITS ({len(orders_data['TP'])})")
                for tp in orders_data["TP"]:
                    print(f"    • Trigger: {tp['triggerPrice']} | Cantidad: {tp['quantity']} | " +
                          f"Lado: {tp['side']} | Estado: {tp['algoStatus']} | ID: {tp['algoId']}")
            
            if orders_data["SL"]:
                print(f"  🛑 STOP LOSS ({len(orders_data['SL'])})")
                for sl in orders_data["SL"]:
                    print(f"    • Trigger: {sl['triggerPrice']} | Cantidad: {sl['quantity']} | " +
                          f"Lado: {sl['side']} | Estado: {sl['algoStatus']} | ID: {sl['algoId']}")
        
        print("\n" + "=" * 100 + "\n")
    
    def print_json(self, data):
        """Imprime datos en formato JSON"""
        print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    """Función principal con argumentos CLI"""
    parser = argparse.ArgumentParser(
        description="Obtener y gestionar TP/SL pendientes en Binance Futures"
    )
    
    parser.add_argument(
        "--api-key",
        required=True,
        help="Tu API Key de Binance"
    )
    
    parser.add_argument(
        "--api-secret",
        required=True,
        help="Tu API Secret de Binance"
    )
    
    parser.add_argument(
        "--symbol",
        help="Símbolo específico (ej: BTCUSDT, opcional)"
    )
    
    parser.add_argument(
        "--action",
        choices=["list", "tp", "sl", "all", "summary", "json"],
        default="summary",
        help="Acción a realizar (default: summary)"
    )
    
    parser.add_argument(
        "--cancel",
        type=int,
        help="Cancelar un TP/SL específico por algo_id"
    )
    
    parser.add_argument(
        "--testnet",
        action="store_true",
        help="Usar testnet de Binance"
    )
    
    parser.add_argument(
        "--no-table",
        action="store_true",
        help="No usar tabla (útil si tabulate no está instalado)"
    )
    
    args = parser.parse_args()
    
    # Inicializar API
    api = BinanceFuturesTPSL(args.api_key, args.api_secret, args.testnet)
    
    try:
        # Cancelar TP/SL si se especifica
        if args.cancel:
            print(f"\n⚠️  Cancelando algo order ID: {args.cancel}...")
            result = api.cancel_tp_sl(args.cancel)
            print("✅ Cancelado correctamente")
            print(json.dumps(result, indent=2))
            return
        
        # Obtener y mostrar datos
        if args.action == "summary":
            api.print_summary(args.symbol)
        
        elif args.action == "list":
            orders = api.get_pending_tp_sl(args.symbol)
            if args.no_table or not orders:
                api.print_json(orders)
            else:
                api.print_table(orders)
        
        elif args.action == "tp":
            orders = api.get_take_profits(args.symbol)
            if args.no_table or not orders:
                api.print_json(orders)
            else:
                api.print_table(orders)
        
        elif args.action == "sl":
            orders = api.get_stop_losses(args.symbol)
            if args.no_table or not orders:
                api.print_json(orders)
            else:
                api.print_table(orders)
        
        elif args.action == "all":
            orders = api.get_pending_tp_sl()
            if args.no_table or not orders:
                api.print_json(orders)
            else:
                api.print_table(orders)
        
        elif args.action == "json":
            orders = api.get_pending_tp_sl(args.symbol)
            api.print_json(orders)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
