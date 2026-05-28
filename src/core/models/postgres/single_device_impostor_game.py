from datetime import datetime

from sqlalchemy import Column, UUID, String, DateTime, BigInteger, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from src.core.models.postgres.base import PostgresModel


class SingleDeviceImpostorGame(PostgresModel):
    """
    Database object which represents a finished single-device impostor game.
    """

    __tablename__ = "single_device_impostor_games"

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

    real_question = Column(String(), nullable=False)
    """
    Real question in game.
    """

    impostor_question = Column(String(), nullable=False)
    """
    Question given to impostors in game.
    """

    impostor_count = Column(String(), nullable=False)
    """
    Count of impostors.
    """

    impostor_indices = Column(JSON(), nullable=False)
    """
    Indices of impostors in game.
    """

    answers = Column(JSON(), nullable=False)
    """
    Answers given by players.
    """

    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    """
    User's creation date.
    """

    user = relationship("User", back_populates="single_device_impostor_games")
    """
    User object related to the game.
    """
