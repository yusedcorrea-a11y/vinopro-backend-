import logging
import os
from app import app
import uvicorn

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # 0.0.0.0 = aceptar conexiones desde la red (móvil por WiFi). 127.0.0.1 = solo este PC.
    host = os.environ.get("HOST", "0.0.0.0").strip()
    port = int(os.environ.get("PORT", "8001"))
    print("Iniciando backend VinoPro en http://{}:{} ...".format(host, port))
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
