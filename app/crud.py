from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from typing import Optional, List, Dict, Any
import datetime

async def create_deck(db: AsyncSession, deck_in: schemas.DeckCreate) -> models.Deck:
    deck = models.Deck(
        name=deck_in.name,
        format=deck_in.format,
        colors=deck_in.colors,
        raw_data=deck_in.raw_data,
    )
    db.add(deck)
    await db.commit()
    await db.refresh(deck)
    return deck

async def create_decklist(db: AsyncSession, dl_in: schemas.DecklistCreate) -> models.Decklist:
    dl = models.Decklist(
        deck_id=dl_in.deck_id,
        mainboard=dl_in.mainboard,
        sideboard=dl_in.sideboard,
    )
    db.add(dl)
    await db.commit()
    await db.refresh(dl)
    return dl

async def create_player(db: AsyncSession, player_in: schemas.PlayerCreate) -> models.Player:
    p = models.Player(
        name=player_in.name,
        mtgo_usernames=player_in.mtgo_usernames,
        arena_usernames=player_in.arena_usernames,
        melee_account=player_in.melee_account,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p

async def create_match(db: AsyncSession, match_in: schemas.MatchCreate) -> models.Match:
    m = models.Match(
        deck_id=match_in.deck_id,
        decklist_id=match_in.decklist_id,
        player_id=match_in.player_id,
        opponent_name=match_in.opponent_name,
        opponent_deck_id=match_in.opponent_deck_id,
        opponent_decklist_id=match_in.opponent_decklist_id,
        opponent_player_id=match_in.opponent_player_id,
        game_win_array=match_in.game_win_array,
        mulligan_array=match_in.mulligan_array,
        opponent_mulligan_array=match_in.opponent_mulligan_array,
        play_draw_array=match_in.play_draw_array,
        game2_sideboard=match_in.game2_sideboard,
        game3_sideboard=match_in.game3_sideboard
    )
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m

async def get_deck(db: AsyncSession, deck_id: str) -> Optional[models.Deck]:
    res = await db.get(models.Deck, deck_id)
    return res

async def get_decklist(db: AsyncSession, decklist_id: str) -> Optional[models.Decklist]:
    res = await db.get(models.Decklist, decklist_id)
    return res

# async def get_decks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Deck]:
#     q = select(models.Deck).offset(skip).limit(limit)
#     res = await db.execute(q)
#     return res.scalars().all()

# async def get_players(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Player]:
#     q = select(models.Player).offset(skip).limit(limit)
#     res = await db.execute(q)
#     return res.scalars().all()

async def get_matches_for_deck(db: AsyncSession, deck_id: str, time_from: Optional[datetime.datetime]=None, time_to: Optional[datetime.datetime]=None) -> List[models.Match]:
    q = select(models.Match).where(models.Match.deck_id == deck_id)
    if time_from:
        q = q.where(models.Match.created_at >= time_from)
    if time_to:
        q = q.where(models.Match.created_at <= time_to)
    res = await db.execute(q)
    return res.scalars().all()

# -- stats computation helper (in crud for now) --
def compute_deck_stats(matches):
    # input: list of Match ORM objects
    total_matches = len(matches)
    total_games = 0
    match_wins = 0
    game_wins = 0

    by_play_draw = {"play": {"wins":0,"games":0}, "draw": {"wins":0,"games":0}, "neither":{"wins":0,"games":0}}

    mulligan_counts = []

    for m in matches:
        # game array - assume 1 for win, 0 for loss
        games = m.game_win_array or []
        total_games += len(games)
        # match win: if any game wins >= 2 (best of 3) treat as match win; fallback: majority
        if len(games) > 0:
            if sum(int(g) for g in games) >= 2:
                match_wins += 1
        # game wins
        game_wins += sum(int(g) for g in games)

        # play/draw breakdown
        pd = m.play_draw_array or []
        for idx, outcome in enumerate(games):
            pd_val = None
            if idx < len(pd):
                val = pd[idx]
                if val is None:
                    pd_val = "neither"
                else:
                    v = val.lower()
                    if v.startswith("p"):
                        pd_val = "play"
                    elif v.startswith("d"):
                        pd_val = "draw"
                    else:
                        pd_val = "neither"
            else:
                pd_val = "neither"

            by_play_draw[pd_val]["games"] += 1
            if int(outcome) == 1:
                by_play_draw[pd_val]["wins"] += 1

        # mulligans
        if m.mulligan_array:
            mulligan_counts.extend([int(x) for x in m.mulligan_array])

    match_winrate = (match_wins / total_matches) if total_matches > 0 else 0.0
    game_winrate = (game_wins / total_games) if total_games > 0 else 0.0

    # compute by_play_draw percentages
    bpd_pct = {}
    for k,v in by_play_draw.items():
        games = v["games"]
        wins = v["wins"]
        bpd_pct[k] = (wins / games) if games > 0 else None

    mulligan_stats = {}
    if mulligan_counts:
        mulligan_stats["avg_mulligans_per_game"] = sum(mulligan_counts)/len(mulligan_counts)
        mulligan_stats["max_mulligans"] = max(mulligan_counts)
        mulligan_stats["min_mulligans"] = min(mulligan_counts)

    return {
        "total_matches": total_matches,
        "total_games": total_games,
        "match_winrate": match_winrate,
        "game_winrate": game_winrate,
        "by_play_draw": bpd_pct,
        "mulligan_stats": mulligan_stats
    }
