"""
roboat.games
~~~~~~~~~~~~~~~
Games API — games.roblox.com
"""

from typing import List, Optional
from .models import Game, GameVotes, GameServer, Page


class GamesAPI:
    BASE  = "https://games.roblox.com/v1"
    BASE2 = "https://games.roblox.com/v2"

    def __init__(self, client):
        self._c = client

    # ------------------------------------------------------------------ #
    #  Game info                                                           #
    # ------------------------------------------------------------------ #

    def get_games(self, universe_ids: List[int]) -> List[Game]:
        """Get full game details for one or more universe IDs."""
        data = self._c._get(
            f"{self.BASE}/games",
            params={"universeIds": ",".join(str(i) for i in universe_ids)},
        )
        return [Game.from_dict(g) for g in data.get("data", [])]

    def get_game(self, universe_id: int) -> Game:
        """Get details for a single game by universe ID."""
        games = self.get_games([universe_id])
        if not games:
            from .exceptions import GameNotFoundError
            raise GameNotFoundError(f"No game found for universe {universe_id}")
        return games[0]

    def get_universe_from_place(self, place_id: int) -> int:
        """Resolve a place ID to its universe ID."""
        data = self._c._get(
            f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
        )
        return data["universeId"]

    def get_game_from_place(self, place_id: int) -> Game:
        """Get a Game by place ID (resolves universe automatically)."""
        uid = self.get_universe_from_place(place_id)
        return self.get_game(uid)

    # ------------------------------------------------------------------ #
    #  Visits / stats                                                      #
    # ------------------------------------------------------------------ #

    def get_visits(self, universe_ids: List[int]) -> dict:
        """
        Return a mapping of {universe_id: visit_count} for given IDs.
        """
        games = self.get_games(universe_ids)
        return {g.id: g.visits for g in games}

    def get_game_stats(self, universe_id: int,
                       stat_type: str = "Visits",
                       granularity: str = "Daily",
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None) -> list:
        """
        Time-series stats for a game.

        stat_type options: "Visits", "Revenue", "Favorites",
                           "PlayerHours", "ConcurrentPlayers"
        granularity: "Hourly", "Daily", "Monthly"

        Returns list of {value, date} dicts.
        """
        params = {
            "universeId": universe_id,
            "type": stat_type,
            "granularity": granularity,
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        data = self._c._get(
            f"https://develop.roblox.com/v1/universes/{universe_id}/stats",
            params=params,
        )
        return data.get("data", [])

    # ------------------------------------------------------------------ #
    #  Discovery / lists                                                   #
    # ------------------------------------------------------------------ #

    def get_games_page(self, genre: str = "All", limit: int = 6,
                       sort_token: Optional[str] = None) -> dict:
        """
        Fetch the public games discovery page (like Roblox home).
        Returns raw sorts[] each containing games[].
        """
        params = {
            "genre": genre,
            "GameFilter": "All",
            "countryRegionId": 1,
        }
        if sort_token:
            params["sortToken"] = sort_token
        return self._c._get(f"{self.BASE}/games/list", params=params)

    def search_games(self, keyword: str, limit: int = 10,
                     cursor: Optional[str] = None) -> Page:
        """Search games by keyword."""
        params = {"keyword": keyword, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(f"{self.BASE}/games/list", params=params)
        games = [Game.from_dict(g) for g in data.get("games", [])]
        return Page(
            data=games,
            next_cursor=data.get("nextPageCursor"),
            previous_cursor=data.get("previousPageCursor"),
        )

    def get_recommended_games(self, universe_id: int, limit: int = 10) -> List[Game]:
        """Get games recommended based on a given universe."""
        data = self._c._get(
            f"{self.BASE}/games/recommendations/game/{universe_id}",
            params={"maxRows": limit},
        )
        return [Game.from_dict(g) for g in data.get("games", [])]

    def get_user_games(self, user_id: int, limit: int = 50,
                       cursor: Optional[str] = None) -> Page:
        """Get games created by a user."""
        params = {"accessFilter": "Public", "limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(f"{self.BASE2}/users/{user_id}/games", params=params)
        return Page.from_dict(data, Game)

    def get_group_games(self, group_id: int, limit: int = 50,
                        cursor: Optional[str] = None) -> Page:
        """Get games created by a group."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(f"{self.BASE2}/groups/{group_id}/games", params=params)
        return Page.from_dict(data, Game)

    # ------------------------------------------------------------------ #
    #  Servers                                                             #
    # ------------------------------------------------------------------ #

    def get_servers(self, place_id: int, server_type: str = "Public",
                    limit: int = 10, cursor: Optional[str] = None) -> Page:
        """
        List active servers for a place.
        server_type: "Public" or "Friend"
        """
        params = {"serverType": server_type, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/games/{place_id}/servers/{server_type}",
            params=params,
        )
        servers = [GameServer.from_dict(s) for s in data.get("data", [])]
        return Page(
            data=servers,
            next_cursor=data.get("nextPageCursor"),
            previous_cursor=data.get("previousPageCursor"),
        )

    # ------------------------------------------------------------------ #
    #  Votes & favourites                                                  #
    # ------------------------------------------------------------------ #

    def get_votes(self, universe_ids: List[int]) -> List[GameVotes]:
        """Get upvote / downvote counts for universes."""
        data = self._c._get(
            f"{self.BASE}/games/votes",
            params={"universeIds": ",".join(str(i) for i in universe_ids)},
        )
        return [GameVotes.from_dict(v) for v in data.get("data", [])]

    def get_user_vote(self, universe_id: int) -> dict:
        """Get the authenticated user's vote for a game. Requires auth."""
        self._c.require_auth("get_user_vote")
        return self._c._get(f"{self.BASE}/games/{universe_id}/votes/user")

    def get_favorite_count(self, universe_id: int) -> int:
        """Get how many users have favorited a game."""
        data = self._c._get(f"{self.BASE}/games/{universe_id}/favorites/count")
        return data.get("favoritesCount", 0)

    # ------------------------------------------------------------------ #
    #  Game passes                                                         #
    # ------------------------------------------------------------------ #

    def get_game_passes(self, universe_id: int, limit: int = 10,
                        cursor: Optional[str] = None) -> Page:
        """Get game passes for a universe."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._c._get(
            f"{self.BASE}/games/{universe_id}/game-passes",
            params=params,
        )
        return Page.from_dict(data)

    # ------------------------------------------------------------------ #
    #  Place details                                                       #
    # ------------------------------------------------------------------ #

    def get_place_details(self, place_ids: List[int]) -> list:
        """Get details for one or more places."""
        return self._c._get(
            f"{self.BASE}/games/multiget-place-details",
            params={"placeIds": ",".join(str(i) for i in place_ids)},
        ).get("data", [])
