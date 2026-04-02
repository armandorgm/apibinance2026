import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.db.database import ExchangeLog, get_session_direct

class ExchangeLogger:
    """
    Service responsible for logging all exchange interactions (SOLID: SRP).
    """
    
    @classmethod
    def log_request(
        cls, 
        method: str, 
        parameters: Dict[str, Any], 
        response: Optional[Any] = None, 
        error_message: Optional[str] = None
    ):
        try:
            # Serialize parameters and response to JSON strings securely
            def default_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return str(obj)

            param_str = json.dumps(parameters, default=default_serializer) if parameters else None
            resp_str = json.dumps(response, default=default_serializer) if response else None

            log_entry = ExchangeLog(
                method=method,
                parameters=param_str,
                response=resp_str,
                is_error=bool(error_message),
                error_message=error_message,
            )
            
            with get_session_direct() as session:
                session.add(log_entry)
                session.commit()
        except Exception as e:
            print(f"[ExchangeLogger] Failed to log interaction: {e}")
