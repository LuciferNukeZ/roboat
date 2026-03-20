"""
integrations/flask_api.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: Expose roboat as a REST API using Flask.
Install: pip install flask

Endpoints:
  GET /user/<id>           — User profile
  GET /game/<id>           — Game stats
  GET /game/<id>/votes     — Vote data
  GET /group/<id>          — Group info
  GET /presence/<id>       — User presence
  GET /thumbnail/user/<id> — Avatar URL
"""

try:
    from flask import Flask, jsonify, abort
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from roboat import RoboatClient
from roboat.exceptions import (
    UserNotFoundError, GameNotFoundError,
    GroupNotFoundError, RoboatAPIError,
)

app    = Flask(__name__) if FLASK_AVAILABLE else None
client = RoboatClient()


def _handle(fn):
    """Error-handling wrapper for route handlers."""
    try:
        return jsonify(fn())
    except UserNotFoundError:
        abort(404, description="User not found")
    except GameNotFoundError:
        abort(404, description="Game not found")
    except GroupNotFoundError:
        abort(404, description="Group not found")
    except RoboatAPIError as e:
        abort(500, description=str(e))


if FLASK_AVAILABLE:
    @app.route("/user/<int:user_id>")
    def get_user(user_id: int):
        return _handle(lambda: {
            "id":              client.users.get_user(user_id).id,
            "name":            client.users.get_user(user_id).name,
            "displayName":     client.users.get_user(user_id).display_name,
            "description":     client.users.get_user(user_id).description,
            "isBanned":        client.users.get_user(user_id).is_banned,
            "hasVerifiedBadge":client.users.get_user(user_id).has_verified_badge,
            "friendCount":     client.friends.get_friend_count(user_id),
            "followerCount":   client.friends.get_follower_count(user_id),
        })

    @app.route("/game/<int:universe_id>")
    def get_game(universe_id: int):
        g = client.games.get_game(universe_id)
        return _handle(lambda: {
            "id":           g.id,
            "name":         g.name,
            "description":  g.description,
            "visits":       g.visits,
            "playing":      g.playing,
            "maxPlayers":   g.max_players,
            "creatorName":  g.creator_name,
            "creatorType":  g.creator_type,
            "genre":        g.genre,
            "favoritedCount": g.favorited_count,
        })

    @app.route("/game/<int:universe_id>/votes")
    def get_votes(universe_id: int):
        votes = client.games.get_votes([universe_id])
        if not votes:
            abort(404)
        v = votes[0]
        return jsonify({"upVotes": v.up_votes, "downVotes": v.down_votes, "ratio": v.ratio})

    @app.route("/group/<int:group_id>")
    def get_group(group_id: int):
        g = client.groups.get_group(group_id)
        return jsonify({
            "id":          g.id,
            "name":        g.name,
            "description": g.description,
            "ownerName":   g.owner_name,
            "memberCount": g.member_count,
            "isPublic":    g.is_public,
        })

    @app.route("/presence/<int:user_id>")
    def get_presence(user_id: int):
        p = client.presence.get_presence(user_id)
        return jsonify({
            "userId":       p.user_id,
            "status":       p.status,
            "lastLocation": p.last_location,
            "lastOnline":   p.last_online,
        })

    @app.route("/thumbnail/user/<int:user_id>")
    def get_thumbnail(user_id: int):
        urls = client.thumbnails.get_user_avatars([user_id])
        return jsonify({"url": urls.get(user_id)})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not FLASK_AVAILABLE:
        print("Install Flask: pip install flask")
    else:
        print("roboat Flask API running on http://localhost:5000")
        app.run(debug=True, port=5000)
