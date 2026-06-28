"""Verdin background worker."""

import signal
import sys
import time

import structlog

logger = structlog.get_logger(__name__)

running = True


def handle_shutdown(signum: int, _frame: object) -> None:
    global running
    logger.info("shutdown_signal_received", signal=signum)
    running = False


def main() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
    )

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    logger.info("worker_started", version="4.2.0")

    while running:
        logger.debug("worker_heartbeat")
        time.sleep(30)

    logger.info("worker_stopped")
    sys.exit(0)


if __name__ == "__main__":
    main()
