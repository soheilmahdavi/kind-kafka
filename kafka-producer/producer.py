from kafka import KafkaProducer
from kafka.errors import KafkaError
import gzip
from config import get_logger
import time


class Producer:

    def __init__(self, config: dict):
        self.__config = config
        self.__logger = get_logger()

    def run(self) -> bool:
        self.__logger.info("Connecting to kafka...")

        producer = KafkaProducer(
            bootstrap_servers=self.__config['KAFKA_BOOTSTRAP_SERVER'],
            sasl_plain_username=self.__config['KAFKA_USERNAME'],
            sasl_plain_password=self.__config['KAFKA_PASSWORD'],
            security_protocol=self.__config['KAFKA_SECURITY_PROTOCOL'],
            sasl_mechanism=self.__config['KAFKA_SASL_MECHANISM'],
            api_version=(3, 6, 0),
            ssl_check_hostname=False)

        time.sleep(1)
        if not producer.bootstrap_connected():
            self.__logger.error("Error: connection could not established.")
            return False
        self.__logger.info("Connecting to kafka...done.")
        self.__publish_jsons(producer)
        return True

    def __publish_jsons(self, producer: KafkaProducer):

        for i in range(20):
            future_record_meta = producer.send(
                self.__config['KAFKA_TOPIC'],
                value=b'{"dev": true}',
                key=b'{"keys_key": "keys-value"}')

            try:
                # 'synchronous' sends
                future_record_meta.get(timeout=10)
            except KafkaError as ke:
                self.__logger.error(ke)
                continue
            self.__logger.info(f"send msg {i}: {future_record_meta.is_done}")

    def __publish_gzipped(self, producer: KafkaProducer):
        for _ in range(3):
            filename = "sample_file.xml"
            with open(f"data/{filename}", 'r', encoding='utf-8') as xml_file:
                producer.send(
                    self.__config['KAFKA_TOPIC'],
                    value=gzip.compress(xml_file.read().encode()),
                    key=gzip.compress(filename.encode()))
        print("done.")
