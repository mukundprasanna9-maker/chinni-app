import uvicorn
import os
import sys
from backend.repositories.database import init_db

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting Cadence API Server (chinni-app)")
    print("=" * 60)
    try:
        init_db()
        print("[Database] Schema initialized successfully.")
    except Exception as e:
        print(f"[Database Warning] {e}")

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    print(f"[Server] Listening at http://{host}:{port}")
    print(f"[Docs] Swagger UI available at http://{host}:{port}/docs")
    print("=" * 60)

    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
