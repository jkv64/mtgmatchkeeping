from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# --- Deck schemas ---
class DeckCreate(BaseModel):
    name: str
    format: Optional[str] = None
    colors: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class DeckOut(BaseModel):
    id: str
    name: str
    format: Optional[str] = None
    colors: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Decklist schemas ---
class DecklistCreate(BaseModel):
    deck_id: str
    mainboard: Optional[Any] = None
    sideboard: Optional[Any] = None


class DecklistOut(BaseModel):
    id: str
    deck_id: str
    mainboard: Optional[Any] = None
    sideboard: Optional[Any] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Player schemas ---
class PlayerCreate(BaseModel):
    name: str
    mtgo_usernames: Optional[List[str]] = None
    arena_usernames: Optional[List[str]] = None
    melee_account: Optional[str] = None


class PlayerOut(BaseModel):
    id: str
    name: str
    mtgo_usernames: Optional[List[str]] = None
    arena_usernames: Optional[List[str]] = None
    melee_account: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Match schemas ---
class MatchCreate(BaseModel):
    deck_id: str
    decklist_id: Optional[str] = None
    player_id: Optional[str] = None
    opponent_name: Optional[str] = None
    opponent_archetype: Optional[str] = None
    game_win_array: List[str]  # ["1", "0", "1"] for W/L/W
    mulligan_array: Optional[List[str]] = None
    play_draw_array: Optional[List[str]] = None
    game2_sideboard: Optional[Dict[str, Any]] = None
    game3_sideboard: Optional[Dict[str, Any]] = None


class MatchOut(BaseModel):
    id: str
    deck_id: str
    decklist_id: Optional[str] = None
    player_id: Optional[str] = None
    opponent_name: Optional[str] = None
    opponent_archetype: Optional[str] = None
    game_win_array: Optional[List[str]] = None
    mulligan_array: Optional[List[str]] = None
    play_draw_array: Optional[List[str]] = None
    game2_sideboard: Optional[Dict[str, Any]] = None
    game3_sideboard: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Stats schemas ---
class DeckStats(BaseModel):
    total_matches: int
    total_games: int
    match_winrate: float
    game_winrate: float
    by_play_draw: Dict[str, Optional[float]]
    mulligan_stats: Dict[str, Any]


class WinrateResponse(BaseModel):
    winrate: float
