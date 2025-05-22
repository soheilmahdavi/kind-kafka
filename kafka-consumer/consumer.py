from kafka import KafkaConsumer
from config import get_logger


class Consumer:
    def __init__(self, config: dict):
        self.__config = config
        self.__logger = get_logger()

    def run(self):
        self.__logger.info("Connecting to kafka...")

        consumer = KafkaConsumer(
            self.__config['KAFKA_TOPIC'],
            group_id=self.__config['KAFKA_CONSUMER_GROUP'],
            bootstrap_servers=[self.__config['KAFKA_BOOTSTRAP_SERVER']],
            sasl_plain_username=self.__config['KAFKA_USERNAME'],
            sasl_plain_password=self.__config['KAFKA_PASSWORD'],
            security_protocol=self.__config['KAFKA_SECURITY_PROTOCOL'],
            sasl_mechanism=self.__config['KAFKA_SASL_MECHANISM'],
            api_version=(3, 5, 1),
            auto_offset_reset='earliest')

        if not consumer.bootstrap_connected():
            self.__logger.error("Error: connection could not established.")
            return
        self.__logger.info("Connected. Consuming messages...")

        for msg in consumer:
            self.__logger.info(msg)
