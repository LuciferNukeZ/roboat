# Changelog

All notable changes to roboat are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] — 2024-06-01

### Added
- `marketplace.py` — `LimitedData`, `ResaleProfit`, `RAPTracker`, profit estimator, underpriced limited scanner
- `social.py` — `SocialGraph` with mutual friends, follow analysis, presence snapshots, friend-of-friend suggestions
- `notifications.py` — Experience push notifications via Open Cloud
- `publish.py` — Asset upload via Open Cloud Assets API (images, audio, 3D models)
- `moderation.py` — Abuse reports, block/unblock, account standing, chat filter
- Team Create management, plugin metadata, ordered DataStores, subscriptions
- `@retry` decorator now supports custom exception tuples
- `Paginator.first(n)` — get first N items without loading all pages
- Terminal: `watch`, `cache`, `rap`, `owns`, `universe` commands

### Changed
- Auth is now OAuth 2.0 — cookie-based auth removed
- Session terminal enforces `start <userid>` before any data command
- All 120-second OAuth flows show live countdown

### Fixed
- `accept_all_join_requests` pagination loop termination
- `TTLCache` eviction under high concurrency
- CSRF rotation on sequential 403 responses

---

## [2.0.0] — 2024-04-15

### Added
- `async_client.py` — full async mirror via aiohttp
- `opencloud.py` — `RoboatCloudClient` with datastores, messaging, bans
- `develop.py` — universe/place management, game stats, DataStore CRUD
- `trades.py` — full trade management
- `messages.py` — private messages + chat
- `inventory.py` — collectibles, ownership checks, `get_total_rap()`
- `events.py` — background polling with callbacks
- `analytics.py` — parallel report aggregation
- `oauth.py` — `OAuthManager` with browser launch, 120s timeout
- `database.py` — SQLite persistence layer
- `session.py` — full interactive REPL with 25+ commands
- `ClientBuilder` — fluent builder pattern
- Typed exceptions per HTTP status

### Changed
- All API responses return typed dataclass models
- `Page` generic wrapper for all paginated results
- `thumbnails.py` returns `{id: url}` dicts

---

## [1.0.0] — 2024-02-01

### Added
- Initial release
- `RoboatClient` sync client
- Users, Games, Catalog, Groups, Friends, Thumbnails, Badges, Economy, Presence, Avatar APIs
- Typed models for all responses
- CSRF auto-rotation

---

## [0.1.0] — 2024-01-10

### Added
- Project scaffolding
- Basic HTTP client
- Core user and game endpoints
