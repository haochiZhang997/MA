import logging

# Setup logger
def setup_logger(level=logging.DEBUG):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s  - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(level)
    all_handler = logging.FileHandler('app_all_logs.log', mode='w')
    all_handler.setLevel(logging.DEBUG)  
    no_debug_handler = logging.FileHandler('app_no_debug_logs.log', mode='w')
    no_debug_handler.setLevel(logging.INFO) 
    all_handler.setFormatter(formatter)
    no_debug_handler.setFormatter(formatter)
    
    # clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(all_handler)
    logger.addHandler(no_debug_handler)
    return logger
   
logger = setup_logger()