# MTG Matchkeeping API

A FastAPI-based service for tracking Magic: The Gathering match results, deck performance, and game statistics.

Authored by Jack Vogel powered by Cursor

## Table of Contents

- [Database Structure](#database-structure)
- [API Endpoints](#api-endpoints)
- [Usage Guide](#usage-guide)
- [Deployment](#deployment)

---

## Database Structure

The service uses PostgreSQL with the following data models:

### Deck

Represents a deck archetype you want to track.

| Field      | Type   | Description                                      |
|------------|--------|--------------------------------------------------|
| `id`       | UUID   | Primary key (auto-generated)                     |
| `name`     | String | Deck name (e.g., "Izzet Phoenix")                |
| `format`   | String | MTG format (e.g., "Modern", "Standard", "Legacy")|
| `colors`   | String | Color identity (e.g., "UR", "WUB")               |
| `raw_data` | JSON   | Optional additional metadata                     |

### Decklist

A specific 75-card configuration linked to a deck.

| Field       | Type   | Description                              |
|-------------|--------|------------------------------------------|
| `id`        | UUID   | Primary key (auto-generated)             |
| `deck_id`   | UUID   | Foreign key to Deck                      |
| `mainboard` | JSON   | List of mainboard cards                  |
| `sideboard` | JSON   | List of sideboard cards                  |

### Player

Represents a player profile with linked gaming accounts.

| Field            | Type       | Description                          |
|------------------|------------|--------------------------------------|
| `id`             | UUID       | Primary key (auto-generated)         |
| `name`           | String     | Display name                         |
| `mtgo_usernames` | String[]   | List of MTGO usernames               |
| `arena_usernames`| String[]   | List of MTG Arena usernames          |
| `melee_account`  | String     | Melee.gg account identifier          |

### Match

Records individual match results with detailed game-by-game data.

| Field               | Type       | Description                                                    |
|---------------------|------------|----------------------------------------------------------------|
| `id`                | UUID       | Primary key (auto-generated)                                   |
| `deck_id`           | UUID       | Foreign key to Deck                                            |
| `decklist_id`       | UUID       | Foreign key to Decklist (optional)                             |
| `player_id`         | UUID       | Foreign key to Player (optional)                               |
| `opponent_name`     | String     | Opponent's name/username                                       |
| `opponent_archetype`| String     | Opponent's deck archetype                                      |
| `game_win_array`    | Integer[]  | Per-game results: `[1, 0, 1]` = Win G1, Lose G2, Win G3        |
| `mulligan_array`    | Integer[]  | Cards mulliganed per game: `[0, 1, 2]` = kept 7, 6, 5          |
| `play_draw_array`   | String[]   | Play/draw per game: `["play", "draw", "play"]`                 |
| `game2_sideboard`   | JSON       | Sideboard changes for game 2                                   |
| `game3_sideboard`   | JSON       | Sideboard changes for game 3                                   |
| `created_at`        | DateTime   | Timestamp when match was recorded                              |

---

## API Endpoints

### Health Check

```
GET /
```

Returns `{"status": "ok"}` if the service is running.

### Deck Management

#### Create a Deck

```
POST /deck
```

**Request Body:**
```json
{
  "name": "Izzet Phoenix",
  "format": "Modern",
  "colors": "UR",
  "raw_data": {}
}
```

#### Get a Deck

```
GET /deck/{deck_id}
```

#### Get Deck Statistics

```
GET /deck/{deck_id}/stats
```

**Response:**
```json
{
  "total_matches": 50,
  "total_games": 127,
  "match_winrate": 0.62,
  "game_winrate": 0.58,
  "by_play_draw": {
    "play": 0.65,
    "draw": 0.52,
    "neither": null
  },
  "mulligan_stats": {
    "avg_mulligans_per_game": 0.4,
    "max_mulligans": 3,
    "min_mulligans": 0
  }
}
```

#### Get Filtered Winrate

```
GET /deck/{deck_id}/winrate
```

**Query Parameters:**

| Parameter            | Type   | Description                                      |
|----------------------|--------|--------------------------------------------------|
| `time_from`          | String | ISO datetime filter start                        |
| `time_to`            | String | ISO datetime filter end                          |
| `game`               | Int    | Specific game number (1-3). Omit for match WR    |
| `player_mulligan_lte`| Int    | Filter: max mulligans per game                   |
| `play_draw`          | String | Filter: `"play"`, `"draw"`, or `"neither"`       |

**Example:**
```
GET /deck/abc123/winrate?play_draw=play&time_from=2024-01-01T00:00:00Z
```

### Decklist Management

#### Create a Decklist

```
POST /decklist
```

**Request Body:**
```json
{
  "deck_id": "uuid-of-deck",
  "mainboard": "4 Ocelot Pride\n4 Guide of Souls\n4 Galvanic Discharge\n",
  "sideboard": "2 Blood Moon\n"
}
```

### Player Management

#### Create a Player

```
POST /player
```

**Request Body:**
```json
{
  "name": "PlayerOne",
  "mtgo_usernames": ["mtgo_handle1", "mtgo_handle2"],
  "arena_usernames": ["Arena#12345"],
  "melee_account": "melee_username"
}
```

### Match Recording

#### Record a Match

```
POST /match
```

**Request Body:**
```json
{
  "deck_id": "uuid-of-deck",
  "decklist_id": "uuid-of-decklist",
  "player_id": "uuid-of-player",
  "opponent_name": "OpponentUsername",
  "opponent_deck_id": "uuid-of-opp-deck",
  "opponent_decklist_id": "uuid-of-opp-decklist",
  "opponent_player_id": "uuid-of-opponent",
  "game_win_array": [1, 0, 1],
  "mulligan_array": [0, 1, 0],
  "play_draw_array": ["play", "draw", "play"],
  "game2_sideboard": {
    "in": ["Blood Moon", "Blood Moon"],
    "out": ["Opt", "Opt"]
  },
  "game3_sideboard": {}
}
```

**Notes:**
- `game_win_array` is required and must have at least one element
- Values: `1` = win, `0` = loss
- A match win is determined by having 2+ game wins (Best of 3)

---

## Usage Guide

### Typical Workflow

1. **Create a Deck** to represent the archetype you're playing
2. **Create a Decklist** (optional) to track specific 75-card configurations
3. **Create a Player** profile to link your gaming accounts
4. **Record Matches** after each game session
5. **Query Statistics** to analyze your performance

### Example: Recording a League

```bash
# 1. Create your deck
curl -X POST http://localhost:8000/deck \
  -H "Content-Type: application/json" \
  -d '{"name": "Golgari Yawgmoth", "format": "Modern", "colors": "BG"}'

# Response: {"id": "deck-uuid-here", ...}

# 2. Record match 1 (2-1 win)
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{
    "deck_id": "deck-uuid-here",
    "opponent_name": "Opponent1",
    "opponent_archetype": "Burn",
    "game_win_array": [1, 0, 1],
    "mulligan_array": [0, 0, 1],
    "play_draw_array": ["draw", "play", "draw"]
  }'

# 3. Check your stats
curl http://localhost:8000/deck/deck-uuid-here/stats
```

### Understanding Statistics

- **Match Winrate**: Percentage of matches won (2+ games in a Bo3)
- **Game Winrate**: Percentage of individual games won
- **Play/Draw Winrate**: Performance breakdown when on the play vs draw
- **Mulligan Stats**: Average cards mulliganed, useful for evaluating deck consistency

---

## Deployment

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd mtg-matchkeeping
   ```

2. **Start the PostgreSQL database**
   ```bash
   docker-compose up -d
   ```

3. **Create a `.env` file**
   ```bash
   echo "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/mtg" > .env
   ```
   > **Note**: The Docker container maps to port 5433 to avoid conflicts with any local PostgreSQL installation on port 5432.

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - OpenAPI Schema: http://localhost:8000/openapi.json

### Environment Variables

| Variable       | Description                          | Example                                              |
|----------------|--------------------------------------|------------------------------------------------------|
| `DATABASE_URL` | Async PostgreSQL connection string   | `postgresql+asyncpg://user:pass@host:5433/dbname`    |

### Production Deployment

For production, consider:

1. **Use Alembic for migrations** instead of `create_all()`:
   ```bash
   pip install alembic
   alembic init alembic
   # Configure and create migrations
   ```

2. **Add the API to Docker Compose**:
   ```yaml
   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/mtg
       depends_on:
         - db
     db:
       image: postgres:15
       # ... existing config
   ```

3. **Create a Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

4. **Use proper secrets management** for database credentials

5. **Add a reverse proxy** (nginx/traefik) for SSL termination

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U postgres mtg > backup.sql

# Restore
docker-compose exec -T db psql -U postgres mtg < backup.sql
```

---

## License

MIT

