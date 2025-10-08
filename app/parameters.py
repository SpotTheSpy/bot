class Parameters:
    MIN_PLAYER_AMOUNT: int = 3
    MAX_PLAYER_AMOUNT: int = 8
    DEFAULT_PLAYER_AMOUNT: int = 4

    DEFAULT_API_RETRY_CYCLES: int = 3
    DEFAULT_API_RETRY_TIMEOUT: int = 1

    TELEGRAM_BOT_START_URL: str = "https://t.me/SpotTheSpyBot?start={payload}"
    DEFAULT_REDIS_KEY: str = "spotthespy"
    DEFAULT_BLURRED_QR_CODE_KEY: str = "blurred"
