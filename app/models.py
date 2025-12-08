from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    format = Column(String)
    colors = Column(String)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    decklists = relationship("Decklist", back_populates="deck")
    matches = relationship("Match", back_populates="deck")


class Decklist(Base):
    __tablename__ = "decklists"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    deck_id = Column(String, ForeignKey("decks.id"), nullable=False)
    mainboard = Column(JSON)
    sideboard = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deck = relationship("Deck", back_populates="decklists")
    matches = relationship("Match", back_populates="decklist")


class Player(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    mtgo_usernames = Column(ARRAY(String))
    arena_usernames = Column(ARRAY(String))
    melee_account = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    matches = relationship("Match", back_populates="player")


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    deck_id = Column(String, ForeignKey("decks.id"), nullable=False)
    decklist_id = Column(String, ForeignKey("decklists.id"))
    player_id = Column(String, ForeignKey("players.id"))
    opponent_name = Column(String)
    opponent_archetype = Column(String)
    game_win_array = Column(ARRAY(String))  # ["1", "0", "1"] for W/L/W
    mulligan_array = Column(ARRAY(String))  # ["0", "1", "2"] mulligans per game
    play_draw_array = Column(ARRAY(String))  # ["play", "draw", "play"]
    game2_sideboard = Column(JSON)
    game3_sideboard = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deck = relationship("Deck", back_populates="matches")
    decklist = relationship("Decklist", back_populates="matches")
    player = relationship("Player", back_populates="matches")
