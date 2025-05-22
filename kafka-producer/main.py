from config import config, get_logger
from producer import Producer

logger = get_logger()

if __name__ == "__main__":
    logger.info(f"Start producer. Topic: {config['KAFKA_TOPIC']}")
    Producer(config).run()
