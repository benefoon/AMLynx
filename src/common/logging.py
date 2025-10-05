import sys, json, os
from loguru import logger

def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO")

    # Remove default and add JSON sink
    logger.remove()

    def _serialize(record):
        r = {
            "level": record["level"].name,
            "time": record["time"].isoformat(),
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        # include context (request_id, etc.)
        r.update(record["extra"])
        return json.dumps(r, ensure_ascii=False)

    logger.add(sys.stdout, level=level, serialize=False, format=_serialize)
    logger.info("Logging initialized")

setup_logging()
