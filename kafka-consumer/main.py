from config import config, get_logger
from consumer import Consumer

logger = get_logger()

if __name__ == "__main__":
    logger.info(f"Start consumer. Topic: {config['KAFKA_TOPIC']}")
    Consumer(config).run()
