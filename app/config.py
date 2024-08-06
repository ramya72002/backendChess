import os

class Config:
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1
    MONGO_URI = os.getenv('MONGO_URI')

config = Config()
