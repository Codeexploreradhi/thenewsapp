import logging

logger = logging.getLogger('speciousnews')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s: %(levelname)s/%(name)s] %(message)s')
ch.setFormatter(formatter)

fileHandler = logging.FileHandler("lastRun.log", mode='w')
fileHandler.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fileHandler)


def get_logger():
    return logger