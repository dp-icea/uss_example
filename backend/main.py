import uvicorn
from config.config import Settings

if __name__ == "__main__":
    host = Settings().HOST
    port = Settings().PORT
    
    if host is None or port is None:
        raise ValueError("HOST and PORT must be set in the environment variables.")

    uvicorn.run("app:app", host=host, port=port, reload=True)
