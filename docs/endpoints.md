# Roblox API Endpoint Reference

All Roblox API endpoints covered by roboat, grouped by domain.

---

## users.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/users/{userId}` | `client.users.get_user(uid)` |
| GET | `/v1/users/authenticated` | `client.users.get_authenticated_user()` |
| POST | `/v1/users` | `client.users.get_users_by_ids(ids)` |
| POST | `/v1/usernames/users` | `client.users.get_users_by_usernames(names)` |
| GET | `/v1/users/search` | `client.users.search_users(kw)` |
| GET | `/v1/users/{userId}/username-history` | `client.users.get_username_history(uid)` |

---

## games.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/games` | `client.games.get_games(ids)` |
| GET | `/v1/games/list` | `client.games.search_games(kw)` |
| GET | `/v1/games/votes` | `client.games.get_votes(ids)` |
| GET | `/v1/games/{universeId}/favorites/count` | `client.games.get_favorite_count(uid)` |
| GET | `/v1/games/{universeId}/votes/user` | `client.games.get_user_vote(uid)` |
| GET | `/v1/games/{placeId}/servers/{type}` | `client.games.get_servers(pid)` |
| GET | `/v1/games/{universeId}/game-passes` | `client.games.get_game_passes(uid)` |
| GET | `/v2/users/{userId}/games` | `client.games.get_user_games(uid)` |
| GET | `/v2/groups/{groupId}/games` | `client.games.get_group_games(gid)` |
| GET | `/v1/games/recommendations/game/{id}` | `client.games.get_recommended_games(uid)` |
| GET | `/v1/games/multiget-place-details` | `client.games.get_place_details(ids)` |

---

## catalog.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/search/items` | `client.catalog.search(...)` |
| POST | `/v1/catalog/items/details` | `client.catalog.get_item_details(items)` |
| GET | `/v1/bundles/{bundleId}/details` | `client.catalog.get_bundle(id)` |
| GET | `/v1/users/{userId}/bundles` | `client.catalog.get_user_bundles(uid)` |
| GET | `/v1/favorites/assets/{assetId}/count` | `client.catalog.get_asset_favorite_count(id)` |

---

## groups.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/groups/{groupId}` | `client.groups.get_group(gid)` |
| GET | `/v1/groups/{groupId}/roles` | `client.groups.get_roles(gid)` |
| GET | `/v1/groups/{groupId}/users` | `client.groups.get_members(gid)` |
| GET | `/v1/groups/{groupId}/roles/{roleId}/users` | `client.groups.get_members(gid, role_id)` |
| PATCH | `/v1/groups/{groupId}/users/{userId}` | `client.groups.set_member_role(...)` |
| DELETE | `/v1/groups/{groupId}/users/{userId}` | `client.groups.kick_member(...)` |
| GET | `/v1/groups/{groupId}/join-requests` | `client.groups.get_join_requests(gid)` |
| POST | `/v1/groups/{groupId}/join-requests/users/{userId}` | `client.groups.accept_join_request(...)` |
| DELETE | `/v1/groups/{groupId}/join-requests/users/{userId}` | `client.groups.decline_join_request(...)` |
| GET | `/v1/groups/{groupId}/wall/posts` | `client.groups.get_wall(gid)` |
| POST | `/v1/groups/{groupId}/wall/posts` | `client.groups.post_to_wall(...)` |
| DELETE | `/v1/groups/{groupId}/wall/posts/{postId}` | `client.groups.delete_wall_post(...)` |
| PATCH | `/v1/groups/{groupId}/status` | `client.groups.post_shout(...)` |
| POST | `/v1/groups/{groupId}/payouts` | `client.groups.pay_out(...)` |
| POST | `/v1/groups/{groupId}/payouts/recurring` | `client.groups.set_recurring_payouts(...)` |
| GET | `/v1/groups/{groupId}/audit-log` | `client.groups.get_audit_log(gid)` |
| GET | `/v1/groups/{groupId}/relationships/allies` | `client.groups.get_allies(gid)` |
| GET | `/v1/groups/{groupId}/relationships/enemies` | `client.groups.get_enemies(gid)` |
| GET | `/v1/groups/search` | `client.groups.search(kw)` |
| GET | `/v1/groups/{groupId}/settings` | `client.groups.get_settings(gid)` |
| PATCH | `/v1/groups/{groupId}/settings` | `client.groups.update_settings(...)` |
| GET | `/v2/users/{userId}/groups/roles` | `client.groups.get_user_groups(uid)` |

---

## friends.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/users/{userId}/friends` | `client.friends.get_friends(uid)` |
| GET | `/v1/users/{userId}/friends/count` | `client.friends.get_friend_count(uid)` |
| GET | `/v1/users/{userId}/followers` | `client.friends.get_followers(uid)` |
| GET | `/v1/users/{userId}/followers/count` | `client.friends.get_follower_count(uid)` |
| GET | `/v1/users/{userId}/followings` | `client.friends.get_followings(uid)` |
| GET | `/v1/users/{userId}/followings/count` | `client.friends.get_following_count(uid)` |
| GET | `/v1/my/friends/requests` | `client.friends.get_friend_requests()` |
| POST | `/v1/users/{userId}/request-friendship` | `client.friends.send_friend_request(uid)` |
| POST | `/v1/users/{userId}/unfriend` | `client.friends.unfriend(uid)` |
| POST | `/v1/users/{userId}/accept-friend-request` | `client.friends.accept_friend_request(uid)` |
| POST | `/v1/users/{userId}/decline-friend-request` | `client.friends.decline_friend_request(uid)` |

---

## thumbnails.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/users/avatar` | `client.thumbnails.get_user_avatars(ids)` |
| GET | `/v1/users/avatar-headshot` | `client.thumbnails.get_user_headshots(ids)` |
| GET | `/v1/games/icons` | `client.thumbnails.get_game_icons(ids)` |
| GET | `/v1/games/multiget/thumbnails` | `client.thumbnails.get_game_thumbnails(ids)` |
| GET | `/v1/assets` | `client.thumbnails.get_asset_thumbnails(ids)` |
| GET | `/v1/groups/icons` | `client.thumbnails.get_group_icons(ids)` |

---

## badges.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/badges/{badgeId}` | `client.badges.get_badge(id)` |
| GET | `/v1/universes/{universeId}/badges` | `client.badges.get_universe_badges(uid)` |
| GET | `/v1/users/{userId}/badges` | `client.badges.get_user_badges(uid)` |
| GET | `/v1/users/{userId}/badges/awarded-dates` | `client.badges.get_awarded_dates(uid, ids)` |

---

## economy.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/users/{userId}/currency` | `client.economy.get_robux_balance(uid)` |
| GET | `/v1/assets/{assetId}/resale-data` | `client.economy.get_asset_resale_data(id)` |
| GET | `/v1/assets/{assetId}/resellers` | `client.economy.get_asset_resellers(id)` |
| GET | `/v1/groups/{groupId}/currency` | `client.economy.get_group_funds(gid)` |
| GET | `/v2/users/{userId}/transaction-totals` | `client.economy.get_transactions(uid)` |

---

## presence.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| POST | `/v1/presence/users` | `client.presence.get_presences(ids)` |
| POST | `/v1/presence/register-app-presence` | `client.presence.register_app_presence(...)` |

---

## avatar.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/users/{userId}/avatar` | `client.avatar.get_user_avatar(uid)` |
| GET | `/v1/avatar` | `client.avatar.get_authenticated_avatar()` |
| GET | `/v1/avatar-rules` | `client.avatar.get_avatar_rules()` |
| GET | `/v1/outfits/{outfitId}/details` | `client.avatar.get_outfit(id)` |
| GET | `/v1/users/{userId}/outfits` | `client.avatar.get_user_outfits(uid)` |

---

## trades.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/trades/{tradeType}` | `client.trades.get_trades(type)` |
| GET | `/v1/trades/{tradeId}` | `client.trades.get_trade_details(id)` |
| GET | `/v1/trades/{tradeType}/count` | `client.trades.get_trade_count(type)` |
| POST | `/v1/trades/{tradeId}/accept` | `client.trades.accept_trade(id)` |
| POST | `/v1/trades/{tradeId}/decline` | `client.trades.decline_trade(id)` |
| POST | `/v1/trades/send` | `client.trades.send_trade(...)` |
| GET | `/v1/users/{userId}/can-trade-with` | `client.trades.can_trade_with(uid)` |

---

## privatemessages.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/messages` | `client.messages.get_messages(...)` |
| GET | `/v1/messages/{messageId}` | `client.messages.get_message(id)` |
| POST | `/v1/messages/send` | `client.messages.send_message(...)` |
| GET | `/v1/messages/unread/count` | `client.messages.get_unread_count()` |
| POST | `/v1/messages/mark-read` | `client.messages.mark_read(ids)` |
| POST | `/v1/messages/mark-unread` | `client.messages.mark_unread(ids)` |
| POST | `/v1/messages/archive` | `client.messages.archive(ids)` |

---

## inventory.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/users/{userId}/assets/collectibles` | `client.inventory.get_collectibles(uid)` |
| GET | `/v1/users/{userId}/items/1/{assetId}/is-owned` | `client.inventory.owns_asset(uid, aid)` |

---

## develop.roblox.com

| Method | Endpoint | roboat |
|---|---|---|
| GET | `/v1/user/universes` | `client.develop.get_universes_by_user(uid)` |
| GET | `/v1/groups/{groupId}/universes` | `client.develop.get_universes_by_group(gid)` |
| GET | `/v1/universes/{universeId}` | `client.develop.get_universe(uid)` |
| GET | `/v1/universes/{universeId}/configuration` | `client.develop.get_universe_settings(uid)` |
| PATCH | `/v1/universes/{universeId}/configuration` | `client.develop.update_universe_settings(...)` |
| POST | `/v1/universes/{universeId}/activate` | `client.develop.activate_universe(uid)` |
| POST | `/v1/universes/{universeId}/deactivate` | `client.develop.deactivate_universe(uid)` |
| GET | `/v1/universes/{universeId}/places` | `client.develop.get_places(uid)` |
| GET | `/v1/universes/{universeId}/stats` | `client.develop.get_game_stats(uid, ...)` |
| GET | `/v1/universes/{universeId}/teamcreate` | `client.develop.get_team_create_settings(uid)` |
| PATCH | `/v1/universes/{universeId}/teamcreate` | `client.develop.update_team_create(uid, ...)` |
| GET | `/v1/universes/{universeId}/teamcreate/memberships` | `client.develop.get_team_create_members(uid)` |
| POST | `/v1/universes/{universeId}/teamcreate/memberships` | `client.develop.add_team_create_member(...)` |
| GET | `/v1/plugins` | `client.develop.get_plugins(ids)` |
| PATCH | `/v1/plugins/{pluginId}` | `client.develop.update_plugin(...)` |

---

## Open Cloud — apis.roblox.com

| Service | Method | roboat |
|---|---|---|
| DataStores | list stores | `client.develop.list_datastores(uid, key)` |
| DataStores | get entry | `client.develop.get_datastore_entry(...)` |
| DataStores | set entry | `client.develop.set_datastore_entry(...)` |
| DataStores | increment | `client.develop.increment_datastore_entry(...)` |
| DataStores | delete | `client.develop.delete_datastore_entry(...)` |
| DataStores | list keys | `client.develop.list_datastore_keys(...)` |
| DataStores | list versions | `client.develop.list_datastore_versions(...)` |
| Ordered DS | list | `client.develop.list_ordered_datastore(...)` |
| Ordered DS | set | `client.develop.set_ordered_datastore_entry(...)` |
| Ordered DS | increment | `client.develop.increment_ordered_datastore(...)` |
| Messaging | publish | `client.develop.publish_message(...)` |
| Messaging | announce | `client.develop.announce(...)` |
| Messaging | shutdown | `client.develop.broadcast_shutdown(...)` |
| User Restrictions | ban | `client.develop.ban_user(...)` |
| User Restrictions | unban | `client.develop.unban_user(...)` |
| User Restrictions | check | `client.develop.get_ban_status(...)` |
| User Restrictions | list | `client.develop.list_bans(...)` |
| Assets | upload | `PublishAPI.upload_image/audio/model(...)` |
| Notifications | send | `NotificationsAPI.send(...)` |
