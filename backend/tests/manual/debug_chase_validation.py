import asyncio
import os
import sys
import json
from datetime import datetime

# Add path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import get_session_direct, BotPipelineProcess, BotSignal
from app.services.pipeline_engine.actions import AdaptiveOTOScalingAction
from app.core.exchange import exchange_manager
from app.core.logger import logger

async def debug_chase_flow():
    print("\n--- INICIANDO DEBUG DE CHASE (ENTORNO REAL) ---")
    symbol = "1000PEPEUSDC"
    trade_amount_usd = 5.02  # Mínimo notional + margen
    
    # 1. Limpiar cualquier proceso previo colgado para este símbolo
    with get_session_direct() as session:
        session.query(BotPipelineProcess).filter(BotPipelineProcess.symbol == symbol).delete()
        session.commit()
    
    # 2. Obtener precio actual
    ticker = await exchange_manager.fetch_ticker(symbol)
    current_price = ticker.get('last')
    print(f"[*] Precio Actual {symbol}: {current_price}")
    
    # 3. Trigger de la Acción Chase
    action = AdaptiveOTOScalingAction()
    params = {
        "side": "buy", 
        "amount": trade_amount_usd,
        "pipeline_id": 999,
        "cooldown": 1,
        "threshold": 0.00001
    }
    context = {"current_price": current_price}
    
    print(f"[*] Ejecutando AdaptiveOTOScalingAction...")
    res = await action.execute(symbol, params, context)
    
    if not res.get("success"):
        print(f"[!] Error al iniciar Chase: {res.get('error')}")
        return

    process_id = res.get("process_id")
    print(f"[+] Chase iniciado. Process ID: {process_id}")
    
    # 4. Monitoreo en bucle
    print("\n[ ] Monitoreando estado (presiona Ctrl+C para detener)...")
    try:
        start_time = datetime.utcnow()
        while True:
            with get_session_direct() as session:
                process = session.query(BotPipelineProcess).filter(BotPipelineProcess.id == process_id).first()
                
                if not process:
                    print("\n🏁 El proceso ha terminado (posiblemente se llenó y se creó el TP).")
                    break
                
                # Buscar señales recientes
                signals = session.query(BotSignal).filter(
                    BotSignal.symbol == symbol,
                    BotSignal.created_at > start_time
                ).order_by(BotSignal.created_at.desc()).limit(3).all()
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {process.status} | Order: {process.entry_order_id} | Price: {process.last_order_price}")
                for s in signals:
                    print(f"   -> Señal: {s.rule_triggered} | Resp: {s.action_taken}")
                
                await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error durante el monitoreo: {e}")

if __name__ == "__main__":
    asyncio.run(debug_chase_flow())
