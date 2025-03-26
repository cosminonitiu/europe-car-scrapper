import logging

def setup_logger(logger_name, log_file):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

logger = setup_logger('myapp.ideals', 'ideals.log')