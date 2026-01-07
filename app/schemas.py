from pydantic import BaseModel, field_validator
import re
from typing import Optional, List, Dict, Any
from datetime import datetime


# --- Deck schemas ---
class DeckCreate(BaseModel):
    name: str
    format: Optional[str] = None
    colors: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("Colors must be a string")
        if not re.match(r"^[WUBRGCwubrgc]+$", v):
            raise ValueError("Invalid deck colors. Use WUBRGC with lowercase letters to represent a splash")
        return v


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

    @field_validator('mainboard', 'sideboard', mode='before')
    @classmethod
    def validate_card_lines(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("Mainboard and sideboard must be strings")
        # Regex: Start, 1-4 digit, space, anything else
        pattern = re.compile(r"^(\d+)\s+(.+)$")
        cards = []
        for line in v.splitlines():
            line = line.strip()
            if not line:
                continue
            match = pattern.match(line)
            if not match:
                raise ValueError(f"Line '{line}' does not match format: count, space, card name")
            
            quantity = int(match.group(1))
            name = match.group(2)
            cards.append({"name": name, "quantity": quantity})
        return cards


class DecklistOut(BaseModel):
    id: str
    deck_id: str
    mainboard: Optional[List[Dict[str, Any]]] = None
    sideboard: Optional[List[Dict[str, Any]]] = None
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
    opponent_deck_id: Optional[str] = None
    opponent_decklist_id: Optional[str] = None
    opponent_player_id: Optional[str] = None
    game_win_array: List[int]  # [1, 0, 1] for W/L/W
    mulligan_array: Optional[List[int]] = None
    play_draw_array: Optional[List[str]] = None
    opponent_mulligan_array: Optional[List[int]] = None
    game2_sideboard: Optional[Dict[str, List[str]]] = None
    game3_sideboard: Optional[Dict[str, List[str]]] = None


class MatchOut(BaseModel):
    id: str
    deck_id: str
    decklist_id: Optional[str] = None
    player_id: Optional[str] = None
    opponent_name: Optional[str] = None
    opponent_deck_id: Optional[str] = None
    opponent_decklist_id: Optional[str] = None
    opponent_player_id: Optional[str] = None
    game_win_array: List[int]
    mulligan_array: Optional[List[int]] = None
    play_draw_array: Optional[List[str]] = None
    opponent_mulligan_array: Optional[List[int]] = None
    game2_sideboard: Optional[Dict[str, List[str]]] = None
    game3_sideboard: Optional[Dict[str, List[str]]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Stats schemas ---
class DeckStats(BaseModel):
    total_matches: int
    total_games: int
    match_winrate: float
    game_winrate: float
    by_play_draw: Dict[str, Optional[float]]
    mulligan_stats: Dict[str, Optional[float]]


class WinrateResponse(BaseModel):
    winrate: float
