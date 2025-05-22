import logging
import os

from dotenv import dotenv_values

# load environment
config = {
    **dotenv_values(".env.shared"),  # load shared dev variables
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with env variables
}

config["DEBUG"] = config.get("DEBUG", "False").lower() in ("true", "1", "t")


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
        logger.propagate = False
        logger.setLevel(logging.DEBUG if config["DEBUG"] else logging.INFO)

    return logger
