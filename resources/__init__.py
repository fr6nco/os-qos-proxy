import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
streamhandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
streamhandler.setFormatter(formatter)
LOGGER.addHandler(streamhandler)