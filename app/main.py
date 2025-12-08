from fastapi import FastAPI, HTTPException, Depends, Query
from . import database, models, schemas, crud
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import uvicorn
from typing import Optional
from datetime import datetime
from .database import AsyncSessionLocal, engine
from sqlalchemy.exc import NoResultFound
import json

app = FastAPI(title="MTG Matchkeeping API")

# Dependency for async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Startup: create tables (simple approach) ---
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # NOTE: in production use Alembic instead of create_all
        await conn.run_sync(models.Base.metadata.create_all)

# --- Deck endpoints ---
@app.post("/deck", response_model=schemas.DeckOut)
async def create_deck(deck_in: schemas.DeckCreate, db: AsyncSession = Depends(get_db)):
    deck = await crud.create_deck(db, deck_in)
    return deck

@app.get("/deck/{deck_id}", response_model=schemas.DeckOut)
async def get_deck(deck_id: str, db: AsyncSession = Depends(get_db)):
    deck = await crud.get_deck(db, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

# decklist create (not in original minimal spec but useful)
@app.post("/decklist", response_model=schemas.DecklistOut)
async def create_decklist(decklist_in: schemas.DecklistCreate, db: AsyncSession = Depends(get_db)):
    dl = await crud.create_decklist(db, decklist_in)
    return dl

@app.get("/deck/{deck_id}/stats", response_model=schemas.DeckStats)
async def deck_stats(deck_id: str, db: AsyncSession = Depends(get_db)):
    matches = await crud.get_matches_for_deck(db, deck_id)
    stats = crud.compute_deck_stats(matches)
    return schemas.DeckStats(
        total_matches=stats["total_matches"],
        total_games=stats["total_games"],
        match_winrate=stats["match_winrate"],
        game_winrate=stats["game_winrate"],
        by_play_draw=stats["by_play_draw"],
        mulligan_stats=stats["mulligan_stats"]
    )

# winrate endpoint with query filtering
@app.get("/deck/{deck_id}/winrate", response_model=schemas.WinrateResponse)
async def deck_winrate(
    deck_id: str,
    time_from: Optional[str] = Query(None, description="ISO datetime"),
    time_to: Optional[str] = Query(None, description="ISO datetime"),
    game: Optional[int] = Query(None, description="which game (1-based). if omitted, match winrate is used"),
    player_mulligan_lte: Optional[int] = Query(None),
    opponent_mulligan_lte: Optional[int] = Query(None),
    play_draw: Optional[str] = Query(None, description="play/draw/neither"),
    db: AsyncSession = Depends(get_db)
):
    # load matches
    from dateutil import parser
    tf = parser.isoparse(time_from) if time_from else None
    tt = parser.isoparse(time_to) if time_to else None

    matches = await crud.get_matches_for_deck(db, deck_id, time_from=tf, time_to=tt)

    # filtering
    filtered = []
    for m in matches:
        ok = True
        # mulligan filters: compare totals or per-game? I'll apply to first game's mulligan when provided
        if player_mulligan_lte is not None and m.mulligan_array:
            # check if any game exceed threshold
            if any(int(x) > player_mulligan_lte for x in m.mulligan_array):
                ok = False
        if opponent_mulligan_lte is not None:
            # No explicit opponent mulligan field in schema: skipping unless provided separately (we did not store opponent mulligans)
            pass

        # play/draw filter: check if any game matches the play_draw param
        if play_draw and m.play_draw_array:
            normalized = [ (p.lower()[0] if p else "n") for p in m.play_draw_array ]
            # If the user requested 'play' ensure the match had at least one game where play/draw == play
            if play_draw.lower().startswith("p"):
                if not any(p=='p' for p in normalized):
                    ok = False
            elif play_draw.lower().startswith("d"):
                if not any(p=='d' for p in normalized):
                    ok = False
            else:
                # neither: matches that didn't play nor draw anywhere
                if any(p in ('p','d') for p in normalized):
                    ok = False

        if not ok:
            continue
        filtered.append(m)

    # Compute winrate depending on `game` param
    if game is None:
        # default: match winrate
        match_wins = 0
        for m in filtered:
            games = m.game_win_array or []
            if sum(int(g) for g in games) >= 2:
                match_wins += 1
        total = len(filtered)
        winrate = (match_wins/total) if total>0 else 0.0
    else:
        # game-specific winrate: game param is 1-based
        idx = game - 1
        total = 0
        wins = 0
        for m in filtered:
            games = m.game_win_array or []
            if idx < len(games):
                total += 1
                wins += int(games[idx])
        winrate = (wins/total) if total>0 else 0.0

    return schemas.WinrateResponse(winrate=winrate)

# --- Player endpoints ---
@app.post("/player", response_model=schemas.PlayerOut)
async def create_player(player_in: schemas.PlayerCreate, db: AsyncSession = Depends(get_db)):
    p = await crud.create_player(db, player_in)
    return p

# --- Match endpoints ---
@app.post("/match", response_model=schemas.MatchOut)
async def create_match(match_in: schemas.MatchCreate, db: AsyncSession = Depends(get_db)):
    # basic validation: at least one game in game_win_array
    if not match_in.game_win_array or len(match_in.game_win_array) == 0:
        raise HTTPException(status_code=400, detail="game_win_array must have at least one element")
    m = await crud.create_match(db, match_in)
    return m

@app.get("/")
async def root():
    return {"status": "ok"}
