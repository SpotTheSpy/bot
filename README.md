# SpotTheSpy Bot

A Telegram-based social deduction game built with Python and aiogram. SpotTheSpy is a "pass-and-play" party game designed for a single device — players take turns viewing their secret roles on one phone, then discuss and try to figure out who the spy is.

**Key features:**
- Single-device multiplayer (3–8 players)
- Six secret word categories
- Configurable spy count (single, double, or random)
- Multilingual support (English, Ukrainian, Russian)
- Persistent game history
- Smart word queue that guarantees 30 unique words before repeating

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Guide](#setup-guide)
- [Game Flow](#game-flow)
- [Core Components — The Dispatcher Factory](#core-components--the-dispatcher-factory)
- [Enums](#enums)
- [Models](#models)
- [Controllers](#controllers)
- [Actions](#actions)
- [Keyboards](#keyboards)
- [Middlewares](#middlewares)
- [Scenes](#scenes)
- [License](#license)

---

## Tech Stack

| Technology | Role |
|---|---|
| **Python 3.14** | Runtime |
| **aiogram 3.x** | Async Telegram bot framework — handles updates, FSM, scenes |
| **PostgreSQL** | Persistent storage for users, settings, and game history |
| **Redis** | Session cache, FSM state storage, active game state |
| **RabbitMQ + Celery** | Message queue and task runner for background jobs |
| **SQLAlchemy 2.x** | Async ORM for PostgreSQL |
| **Pydantic 2.x** | Data validation and settings management |
| **aiogram-i18n + Fluent** | Internationalization using Mozilla's Fluent format |

---

## Project Structure

```
spotthespy_bot/
├── polling.py                  # Entry point — long polling mode
├── webhook.py                  # Entry point — webhook mode
├── config.py                   # Pydantic settings (env vars, game params)
├── compose-local.yaml          # Docker Compose for local services
├── alembic.ini                 # Database migration config
├── locales/                    # Translation files (en, uk, ru)
│   └── {locale}/*.ftl
├── migrations/                 # Alembic migration versions
│
└── src/
    ├── bot/                    # Application layer (Telegram-facing)
    │   ├── dispatcher.py       # Dispatcher factory — wires everything together
    │   ├── locale_manager.py   # Locale persistence manager
    │   ├── logger.py           # Logger setup
    │   ├── routes/             # Command handlers (/start)
    │   ├── scenes/             # FSM scenes (game states)
    │   ├── actions/            # Callback data classes (button payloads)
    │   ├── keyboards/          # Inline keyboard builders
    │   ├── middlewares/        # Request interceptors (user, error)
    │   └── exceptions/         # Custom exception types
    │
    └── core/                   # Domain layer (business logic)
        ├── enums/              # Game and app enumerations
        ├── models/
        │   ├── postgres/       # SQLAlchemy ORM models
        │   └── redis/          # Pydantic cache/session models
        ├── controllers/        # Data access (Postgres sessions, Redis CRUD)
        └── assets/             # Game data (secret words JSON)
```

---

## Setup Guide

### Prerequisites

- **Python 3.14+**
- **Poetry** (dependency manager)
- **Docker & Docker Compose** (for Postgres, Redis, RabbitMQ)
- A **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_DSN` | Yes | PostgreSQL connection string, e.g. `postgresql+psycopg://user:pass@localhost:5433/spotthespy` |
| `REDIS_DSN` | Yes | Redis connection string, e.g. `redis://localhost:6379` |
| `RABBITMQ_DSN` | Yes | RabbitMQ connection string, e.g. `amqp://user:pass@localhost:5672//` |
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from BotFather |
| `TELEGRAM_SECRET` | Webhook only | Secret for authenticating Telegram webhook requests |
| `WEBHOOK_URL` | Webhook only | Public URL where Telegram sends updates |
| `WEBHOOK_PATH` | Webhook only | URL path for the webhook endpoint |

### 3. Start Local Services

```bash
docker compose -f compose-local.yaml up -d
```

This starts PostgreSQL (port 5433), Redis (port 6379), and RabbitMQ (ports 5672/5673).

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Launch the Bot

**Polling mode** (recommended for development):

```bash
python polling.py
```

**Webhook mode** (for production — starts an aiohttp server on port 8080):

```bash
python webhook.py
```

---

## Game Flow

SpotTheSpy follows a single-device pass-and-play model: one person holds the phone, views their role privately, then passes it to the next player. After everyone has seen their role, the group discusses who the spy might be.

```mermaid
flowchart TD
    A["/start — Greeting"] --> B{Choose}
    B -->|"Play Spy Game"| C["Tutorial"]
    B -->|"Change Language"| D["Language Selection"]
    D -->|"Back"| A
    C -->|"Got It"| E["Setup Menu"]
    E -->|"Configure"| F["Player Count / Category / Spy Count"]
    F -->|"Back"| E
    E -->|"Play"| G["Player 1: View Role"]

    G --> H["Show Role & Secret Word"]
    H -->|"Proceed"| I{More players?}
    I -->|"Yes"| J["Next Player: View Role"]
    J --> H
    I -->|"No"| K["Discussion Phase"]

    K -->|"Finish"| L["Results — Reveal Spies"]
    L -->|"Play Again"| G
    L -->|"Back"| A
```

**How roles work:** When a game starts, the bot randomly assigns spy indices based on the selected spy count mode. Each player taps "View Role" to see whether they are a **Citizen** (who sees the secret word) or a **Spy** (who does not know the word and must bluff). After all roles are revealed, players discuss and vote to identify the spy.

---

## Core Components — The Dispatcher Factory

The heart of the bot is `create_dispatcher()` in `src/bot/dispatcher.py`. This factory function assembles the entire bot pipeline in one place:

1. **Database connections** — creates a `PostgresController` and an async `Redis` client from the configured DSNs.
2. **Dispatcher** — initializes aiogram's `Dispatcher` with Redis-backed FSM storage using `FSMStrategy.GLOBAL_USER` (state is scoped per user, not per chat).
3. **Dependency injection** — attaches all controllers to the dispatcher as keyword arguments. Every scene and middleware receives these automatically through aiogram's data propagation.
4. **Middleware chain** — registers `UserMiddleware`, `I18nMiddleware`, and `ErrorMiddleware` as outer middlewares (they run on every update, in order).
5. **Routes and scenes** — includes the `/start` command router and registers all five scenes into the `SceneRegistry`.

The result is a fully configured dispatcher ready to be passed to either `start_polling()` or the webhook handler.

```python
# Simplified view of what the factory produces
dispatcher = Dispatcher(
    storage=RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True)),
    fsm_strategy=FSMStrategy.GLOBAL_USER,
    postgres=postgres,
    redis=redis,
    user_controller=RedisController[User](redis),
    telegram_user_controller=RedisController[TelegramUser](redis),
    single_device_spy_game_controller=RedisController[SingleDeviceSpyGame](redis),
    secret_word_controller=RedisController[SecretWordQueue](redis),
)
```

Controllers, the config object, and database clients are all injected here and become available to every handler in the app through aiogram's built-in dependency injection.

---

## Enums

Enums live in `src/core/enums/` and define the fixed choices used throughout the game.

| Enum | Values | Purpose |
|---|---|---|
| `Locale` | `EN`, `UK`, `RU` | Supported languages. Defaults to `EN` for unrecognized codes. |
| `SpyCategory` | `GENERAL`, `FOOD`, `NATURE`, `ANIMALS`, `PLACES`, `CELEBRITIES` | Categories for secret word selection. Each maps to a list of words in `secret_words.json`. |
| `SpyCount` | `SINGLE`, `DOUBLE`, `RANDOM` | How many spies are in the game. |
| `SpyPlayerRole` | `CITIZEN`, `SPY` | The two possible roles a player can have. |
| `SpyGameParameter` | `PLAYER_COUNT`, `CATEGORY`, `SPY_COUNT` | Identifies which setup parameter is being configured. |
| `TimeStamp` | `SECOND(1)`, `MINUTE(60)`, `HOUR(3600)`, `DAY(86400)` | TTL constants used for Redis key expiration. |

### SpyCount and Random Mode

`SpyCount` has a `get_indices()` method that generates randomized spy assignments. In `RANDOM` mode, the outcome is weighted:

| Outcome | Probability |
|---|---|
| 1 spy | 40% |
| 2 spies | 40% |
| 0 spies (no spy!) | 15% |
| All players are spies | 5% |

This creates unpredictable rounds where sometimes nobody is a spy — or everyone is.

---

## Models

Models are split between two storage layers, each serving a different purpose.

### PostgreSQL Models — Persistent Data

These live in `src/core/models/postgres/` and use SQLAlchemy's declarative ORM.

| Model | Table | What It Stores |
|---|---|---|
| `User` | `users` | Telegram ID, first name, timestamps. Has a one-to-one relationship with `UserSettings` and one-to-many with game records. |
| `UserSettings` | `user_settings` | User preferences — currently just their locale choice. Linked to `User` by foreign key. |
| `SingleDeviceSpyGame` | `single_device_spy_games` | Completed game records: who hosted it, how many players, the secret word, category, spy count mode, and which player indices were spies. Saved when a game finishes. |

### Redis Models — Session & Game State

These live in `src/core/models/redis/` and are Pydantic models serialized to JSON.

| Model | Key Pattern | TTL | What It Caches |
|---|---|---|---|
| `User` | `spotthespy:user:{id}` | 1 day | Active session data: telegram ID, name, locale, current message reference, and active game IDs. The nested `Message` object tracks the current `chat_id` and `message_id` so the bot can edit messages in place. |
| `TelegramUser` | `spotthespy:telegram_user:{telegram_id}` | 1 day | A lightweight mapping from Telegram ID to internal UUID. Lets the middleware quickly find the cached user without hitting Postgres. |
| `SingleDeviceSpyGame` | `spotthespy:single_device_spy_game:{id}` | 1 hour | The live game instance: player count, secret word, category, spy count mode, and the spy indices. Exists only while a game is in progress. |
| `SecretWordQueue` | `spotthespy:secret_words_queue:{user_id}` | 1 day | Tracks the last 30 secret words a user has seen. When picking a new word, `get_unique_word()` draws from the category's word list while skipping any word in this queue. |

**The message-editing pattern:** The bot operates by editing a single message per user rather than sending new ones. The `User.message` object stores the current `chat_id` and `message_id`. When a handler calls `user.message.edit(...)`, it updates that message in the chat. If the message ID changes (e.g., because the old message was deleted), the middleware persists the updated user back to Redis.

---

## Controllers

Controllers in `src/core/controllers/` provide the data access layer between the bot logic and the databases.

### RedisController

`RedisController[T]` is a generic class that can manage any Redis model type. You parameterize it with a model class, and it handles serialization, key generation, and CRUD operations automatically.

```python
# Creating a controller for User models
user_controller = RedisController[User](redis)

# Basic operations
await user_controller.set(user, expire=TimeStamp.DAY)
user = await user_controller.get(user_id)
exists = await user_controller.exists(user_id)
await user_controller.remove(user_id)
all_users = await user_controller.all(limit=50)
```

**Key format:** Every key is composed as `{default_key}:{model_key}:{primary_key}`, e.g. `spotthespy:user:550e8400-...`. The `default_key` comes from the config (defaults to `"spotthespy"`), and each model class defines its own `model_key` via a `key()` class method.

### PostgresController

`PostgresController` manages SQLAlchemy async sessions. It wraps the session lifecycle in an async context manager with automatic connection recovery — if the database connection drops, it recreates the session transparently.

```python
async with postgres.session() as session:
    result = await session.execute(select(User).filter_by(telegram_id=12345))
    user = result.scalar_one_or_none()
```

The controller is created once via `PostgresController.from_dsn()` during dispatcher setup and reused for the lifetime of the application.

---

## Actions

Actions are aiogram `CallbackData` subclasses that define the payload attached to inline keyboard buttons. When a user taps a button, aiogram routes the callback to the correct handler based on the action's prefix.

Each action class inherits from `BaseAction` (which extends `CallbackData`) and declares a unique `prefix`. Some carry data fields, others are just signals.

### Global Actions

| Action | Prefix | Fields | Purpose |
|---|---|---|---|
| `BackAction` | `back` | — | Navigate to the previous scene in the history stack |
| `HomeAction` | `home` | — | Jump back to the start scene |
| `SwitchSceneAction` | `switch` | `scene: str` | Navigate to a named scene |
| `SwitchLanguageAction` | `switch_language` | `locale: str` | Change the user's language |

### Spy Game Actions

| Action | Prefix | Fields | Purpose |
|---|---|---|---|
| `SpyGameSetupAction` | `spy_game_setup` | `game_parameter` | Open a setup sub-menu (player count, category, or spy count) |
| `SpyGameSetupPlayerAmountAction` | `spy_game_setup_player_count` | `player_count: int` | Set the number of players |
| `SpyGameSetupCategoryAction` | `spy_game_setup_category` | `category` | Set the word category |
| `SpyGameSetupSpyCountAction` | `spy_game_setup_spy_count` | `spy_count` | Set the spy count mode |
| `SpyGamePlayAction` | `spy_game_play` | — | Start the game |
| `SingleDeviceSpyGameViewRoleAction` | `single_device_spy_game_view_role` | — | Reveal the current player's role |
| `SingleDeviceSpyGameProceedAction` | `single_device_spy_game_proceed` | — | Advance to the next player |
| `SingleDeviceSpyGameFinishAction` | `single_device_spy_game_finish` | — | End discussion and show results |
| `SingleDeviceSpyGamePlayAgainAction` | `single_device_spy_game_play_again` | — | Start a new game with the same settings |

**How routing works:** Each action's `prefix` is encoded into the callback data string stored in the button. When a callback comes in, aiogram matches it against registered `CallbackData.filter()` patterns in the scene handlers. This means button presses are automatically dispatched to the correct handler without manual string parsing.

---

## Keyboards

Keyboards in `src/bot/keyboards/` are builder functions that construct aiogram `InlineKeyboardMarkup` objects. Each function creates a keyboard for a specific screen, embedding the appropriate actions into button callback data.

### Main Keyboards

- **`greeting_keyboard()`** — The home screen. Two buttons: "Play Spy Game" (switches to the tutorial scene) and "Change Language" (switches to the language scene).
- **`language_keyboard()`** — Shows one button per supported locale with the language name translated into that language. Includes a back button.
- **`tutorial_keyboard()`** — "Got It" (proceeds to setup) and "Back" buttons.

### Setup Keyboards

- **`spy_game_setup_keyboard()`** — The main setup menu. Shows the current value of each parameter (player count, category, spy count) as button labels. Includes "Play" and "Back" buttons.
- **`spy_game_setup_player_count_keyboard()`** — A grid of numbers from 3 to 8. The currently selected count is visually marked.
- **`spy_game_setup_category_keyboard()`** — A grid of six categories. The selected category is marked.
- **`spy_game_setup_spy_count_keyboard()`** — Three options (Single, Double, Random). The selected mode is marked.

### Gameplay Keyboards

- **`single_device_spy_game_view_role_keyboard()`** — Single "View Role" button.
- **`single_device_spy_game_proceed_keyboard()`** — Single "Proceed" button (pass the phone).
- **`single_device_spy_game_discuss_keyboard()`** — Single "Finish" button (end the discussion).
- **`single_device_spy_game_results_keyboard()`** — "Play Again" and "Back" buttons.

**Selected indicator pattern:** In the setup sub-menus (player count, category, spy count), the currently selected option is marked with a visual indicator in the button text. This lets the user see their current selection at a glance before changing it.

---

## Middlewares

Middlewares intercept every incoming update before it reaches scene handlers. They're registered as outer middlewares in the dispatcher, meaning they run on the raw `Update` object.

### Middleware Execution Order

```
Update → UserMiddleware → I18nMiddleware → ErrorMiddleware → Scene Handler
```

### UserMiddleware

The user middleware (`src/bot/middlewares/user.py`) ensures every handler receives a fully loaded `User` object. It follows a tiered lookup strategy:

1. **Redis fast path** — Look up the user's internal UUID via the `TelegramUser` mapping in Redis. If found, load the full `User` object from Redis. This is the hot path for returning users.
2. **Postgres fallback** — If Redis doesn't have the user (cache expired or first request after restart), query PostgreSQL by telegram ID.
3. **Create new user** — If the user doesn't exist anywhere, create a new `User` and `UserSettings` in PostgreSQL, then cache them in Redis.

After the handler runs, if the message ID changed (because the bot sent or edited a message), the middleware persists the updated user back to Redis so the next request has the correct message reference.

### ErrorMiddleware

The error middleware (`src/bot/middlewares/error.py`) wraps handler execution in a try/catch for `BotError` exceptions. When a game error occurs (e.g., missing game state), it sends a localized error message to the user instead of crashing silently.

---

## Scenes

Scenes are aiogram's implementation of finite state machines (FSM). Each scene represents a distinct screen or phase of interaction. The bot uses scenes to manage the conversation flow — from greeting to game setup to active gameplay.

### Scene Registry

```mermaid
flowchart LR
    Start["StartScene"] -->|"Spy Game"| Tutorial["TutorialScene"]
    Start -->|"Language"| Language["LanguageScene"]
    Language -->|"Back"| Start
    Tutorial -->|"Got It"| Setup["SetupScene"]
    Setup -->|"Play"| Play["PlayScene"]
    Play -->|"Back / Finish"| Start
    Play -->|"Play Again"| Play
    Setup -->|"Back"| Tutorial
    Tutorial -->|"Back"| Start
```

| Scene | State Name | Resets History | Purpose |
|---|---|---|---|
| `StartScene` | `start` | Yes | Landing screen. Cleans up any abandoned games from the user's previous session. |
| `LanguageScene` | `language` | No | Language picker. Saves the selected locale to both Redis and PostgreSQL on exit. |
| `SingleDeviceSpyGameTutorialScene` | `single_device_spy_game_tutorial` | No | Shows game rules. Single "Got It" button to proceed. |
| `SingleDeviceSpyGameSetupScene` | `single_device_spy_game_setup` | No | Game configuration. Manages three parameters in FSM context: player count (default 4), category (default General), and spy count (default Single). |
| `SingleDeviceSpyGamePlayScene` | `single_device_spy_game_play` | No | Active gameplay. Creates the game on entry, walks through each player's role reveal, handles discussion, shows results, and supports replaying. Cleans up Redis state on exit. |

### BaseScene

All scenes inherit from `BaseScene` (`src/bot/scenes/base.py`), which provides two shared behaviors:

- **Back navigation** — Handles `BackAction` callbacks by calling `wizard.back()`, which returns to the previous scene in the history stack (unless already at the start scene).
- **Scene switching** — Handles `SwitchSceneAction` callbacks by calling `wizard.goto(scene_name)`, which navigates to any scene by its state name.

### How the Play Scene Works

The play scene is the most complex scene. It manages the full game lifecycle:

- **`on_enter`** — Creates a new `SingleDeviceSpyGame` in Redis, fetches a unique secret word from the queue, tracks the game ID in the user's active games, and shows the first player's "View Role" prompt.
- **`on_view_role`** — Checks the current player index against the spy indices. Shows "Spy" or "Citizen" with the secret word (citizens see it, spies see a message indicating they're the spy).
- **`on_proceed`** — Increments the player index. If more players remain, shows the next "View Role" prompt. If all players have seen their role, transitions to the discussion phase.
- **`on_finish`** — Reveals who the spies were and the secret word. Saves the completed game to PostgreSQL for history.
- **`on_play_again`** — Removes the old game from Redis, creates a fresh one with the same settings but a new secret word, and restarts the role reveal loop.
- **`on_leave`** — Cleans up the game from Redis and clears the user's active game reference.

---

## License

This repository is published for viewing and reference purposes only.

No permission is granted to use, copy, modify, merge, publish, distribute, sublicense, or sell any part of this code, in whole or in part, without explicit written permission from the author.

You are welcome to read the code and discuss it, but please do not reuse it in your own projects.
