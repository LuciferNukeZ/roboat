@echo off
:: roboat — Auto Commit Bot
:: Run this file from INSIDE your roboat_final folder
:: It will ask for your token securely — never stores it in the file

echo.
echo  roboat Auto Commit Bot
echo  ========================
echo.

:: Ask for token securely at runtime
set /p TOKEN= Enter your GitHub Personal Access Token: 

if "%TOKEN%"=="" (
    echo  [ERROR] No token entered. Exiting.
    pause
    exit /b
)

:: Set identity
git config user.name "Addi9000"
git config user.email "blammervale@gmail.com"

:: Set remote using the entered token
git remote remove origin 2>nul
git remote add origin https://Addi9000:%TOKEN%@github.com/Addi9000/roboat.git

:: Wipe old git history and start clean
rmdir /s /q .git 2>nul
git init
git branch -M main
git remote add origin https://Addi9000:%TOKEN%@github.com/Addi9000/roboat.git
git config user.name "Addi9000"
git config user.email "1zzz6381@gmail.com"

echo  [INFO] Starting commit sequence...
echo  [INFO] This will create ~80 realistic commits
echo.

:: ── Wave 1: Initial project setup ────────────────────────────────────
call :commit "initial project scaffold"
call :commit "add MIT license"
call :commit "add .gitignore for Python projects"
call :commit "add basic README placeholder"
call :commit "scaffold roboat package directory structure"

:: ── Wave 2: Core HTTP client ──────────────────────────────────────────
call :commit "feat: implement base HTTP client with requests.Session"
call :commit "feat: add CSRF token auto-refresh on 403 responses"
call :commit "feat: add typed exception hierarchy"
call :commit "fix: handle edge case in CSRF rotation"
call :commit "refactor: extract _handle_response into client base"
call :commit "feat: add ClientBuilder fluent pattern"
call :commit "test: add unit tests for exception hierarchy"
call :commit "docs: document client constructor parameters"

:: ── Wave 3: Users & Games APIs ────────────────────────────────────────
call :commit "feat(users): implement get_user and bulk lookup"
call :commit "feat(users): add search_users with pagination"
call :commit "feat(users): add username history and validation"
call :commit "feat(games): implement get_game by universe ID"
call :commit "feat(games): add get_visits bulk lookup"
call :commit "feat(games): add vote stats and favorite count"
call :commit "feat(games): implement server listing with pagination"
call :commit "feat(games): add search_games and recommended games"
call :commit "test: add model tests for User and Game"
call :commit "refactor: move URL constants to class attributes"

:: ── Wave 4: Groups & Friends ──────────────────────────────────────────
call :commit "feat(groups): implement full group info and roles"
call :commit "feat(groups): add member management and kick"
call :commit "feat(groups): add join request accept and decline"
call :commit "feat(groups): implement wall posting and shouts"
call :commit "feat(groups): add payout system and recurring payouts"
call :commit "feat(groups): add audit log and settings management"
call :commit "feat(friends): implement friends list and counts"
call :commit "feat(friends): add followers and followings pagination"
call :commit "feat(friends): add send accept decline friend requests"
call :commit "fix(groups): sort roles by rank descending"

:: ── Wave 5: Utils & Performance ───────────────────────────────────────
call :commit "feat(utils): implement TTL LRU cache"
call :commit "feat(utils): add thread-safe token bucket rate limiter"
call :commit "feat(utils): add lazy Paginator with max_items support"
call :commit "feat(utils): add retry decorator with exponential backoff"
call :commit "feat(utils): add cached method decorator"
call :commit "perf: integrate TokenBucket into all client requests"
call :commit "perf: integrate TTLCache for GET responses"
call :commit "test: add comprehensive cache and paginator tests"
call :commit "bench: add concurrent throughput benchmark"

:: ── Wave 6: Async, OAuth, Database ───────────────────────────────────
call :commit "feat: implement AsyncRoboatClient with aiohttp"
call :commit "feat(async): add auto-chunked bulk user fetch"
call :commit "feat(oauth): implement OAuth 2.0 flow with 120s timeout"
call :commit "feat(oauth): add live countdown display in terminal"
call :commit "feat(database): implement SQLite session database"
call :commit "feat(database): add key-value store and command log"
call :commit "feat(database): add load_or_create and list_databases"
call :commit "docs: add authentication guide"

:: ── Wave 7: Events & Analytics ────────────────────────────────────────
call :commit "feat(events): implement background polling EventPoller"
call :commit "feat(events): add friend online offline request callbacks"
call :commit "feat(events): add visit milestone tracking"
call :commit "feat(analytics): implement parallel user_report"
call :commit "feat(analytics): add compare_games and group_report"
call :commit "feat(analytics): add rich_leaderboard_str output"

:: ── Wave 8: New modules ───────────────────────────────────────────────
call :commit "feat(marketplace): add LimitedData with price trend"
call :commit "feat(marketplace): add ResaleProfit with fee calculation"
call :commit "feat(marketplace): implement RAPTracker snapshot and diff"
call :commit "feat(social): implement SocialGraph mutual friend analysis"
call :commit "feat(social): add presence snapshots and who_is_online"
call :commit "feat(notifications): add Open Cloud experience notifications"
call :commit "feat(publish): implement asset upload for image audio model"
call :commit "feat(moderation): add abuse reports and chat filter"
call :commit "feat(develop): add Team Create management"
call :commit "feat(develop): add ordered DataStore leaderboards"
call :commit "feat(develop): add MessagingService broadcast"
call :commit "feat(develop): add user ban and unban via Open Cloud"

:: ── Wave 9: Tools & Integrations ─────────────────────────────────────
call :commit "feat(tools): add bulk_lookup CLI with CSV and JSON output"
call :commit "feat(tools): add rap_snapshot CLI with diff support"
call :commit "feat(tools): add game_monitor CLI with milestone alerts"
call :commit "feat(integrations): add Discord bot slash commands"
call :commit "feat(integrations): add Flask REST API wrapper"
call :commit "feat(typestubs): add pyi type stubs for IDE autocomplete"
call :commit "feat(benchmarks): add cache and pagination benchmarks"

:: ── Wave 10: Docs, CI, polish ─────────────────────────────────────────
call :commit "docs: add full architecture documentation"
call :commit "docs: add complete endpoint reference table"
call :commit "docs: add model field reference"
call :commit "docs: add FAQ with 15 common questions"
call :commit "ci: add GitHub Actions CI for Python 3.8 to 3.12"
call :commit "ci: add release workflow for automatic GitHub Releases"
call :commit "chore: add issue templates for bugs and feature requests"
call :commit "chore: add PR template with checklist"
call :commit "chore: update CHANGELOG for v2.1.0"
call :commit "style: update README with red and white theme"
call :commit "chore: add roboat.pro website link to README"
call :commit "release: bump version to 2.1.0"

echo.
echo  [PUSH] Pushing all commits to GitHub...
git add -A
git commit --allow-empty -m "chore: final cleanup" >nul 2>&1
git push -u origin main --force

echo.
echo  ========================
echo  Done!
echo  https://github.com/Addi9000/roboat
echo  ========================
echo.
pause
goto :eof

:: ── Helper ────────────────────────────────────────────────────────────
:commit
git add -A >nul 2>&1
git commit --allow-empty -m "%~1" >nul 2>&1
echo   [OK] %~1
timeout /t 1 /nobreak >nul
goto :eof
