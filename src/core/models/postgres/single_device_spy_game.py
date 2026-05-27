from datetime import datetime

from sqlalchemy import Column, UUID, String, DateTime, BigInteger, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from src.core.models.postgres.base import PostgresModel


class SingleDeviceSpyGame(PostgresModel):
    """
    Database object which represents a finished single-device spy game.
    """

    __tablename__ = "single_device_spy_games"

    id = Column(UUID(True), primary_key=True, nullable=False)
    """
    UUID.
    """

    host_id = Column(UUID(True), ForeignKey("users.id"), nullable=False, index=True)
    """
    Host ID.
    """

    host_telegram_id = Column(BigInteger(), nullable=False, index=True)
    """
    Host's telegram ID.
    """

    player_count = Column(Integer(), nullable=False)
    """
    Count of players in game.
    """

    secret_word = Column(String(), nullable=False)
    """
    Secret word tag.
    """

    category = Column(String(), nullable=False)
    """
    Secret word category.
    """

    spy_count = Column(String(), nullable=False)
    """
    Count of spies.
    """

    spy_indices = Column(JSON(), nullable=False)
    """
    Indices of spies in game.
    """

    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    """
    User's creation date.
    """

    user = relationship("User", back_populates="single_device_spy_games")
    """
    User object related to the game.
    """
