"""
integrations/discord_bot.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Example: Discord bot that exposes roboat functionality as slash commands.
Uses discord.py — install with: pip install discord.py

Commands:
  /user <id>        — Show Roblox user profile
  /game <id>        — Show game stats
  /rap <id>         — Show user's total RAP
  /friends <id>     — Friend count
  /status <id>      — Online presence status
"""

import os
import asyncio
from typing import Optional

try:
    import discord
    from discord import app_commands
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("discord.py not installed. Run: pip install discord.py")

from roboat import AsyncRoboatClient


class RoboatBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.roblox: Optional[AsyncRoboatClient] = None

    async def setup_hook(self):
        self.roblox = AsyncRoboatClient()
        await self.roblox.start()
        await self.tree.sync()
        print(f"Synced slash commands.")

    async def close(self):
        if self.roblox:
            await self.roblox.close()
        await super().close()

    async def on_ready(self):
        print(f"Logged in as {self.user}")


def create_bot() -> RoboatBot:
    bot = RoboatBot()

    @bot.tree.command(name="user", description="Look up a Roblox user by ID")
    @app_commands.describe(user_id="The Roblox user ID")
    async def cmd_user(interaction: discord.Interaction, user_id: int):
        await interaction.response.defer()
        try:
            user = await bot.roblox.users.get_user(user_id)
            friends = await bot.roblox.friends.get_friend_count(user_id)
            followers = await bot.roblox.friends.get_follower_count(user_id)
            avatar_urls = await bot.roblox.thumbnails.get_user_avatars([user_id])

            embed = discord.Embed(
                title=f"{user.display_name}",
                description=f"@{user.name}" + (" ✓" if user.has_verified_badge else ""),
                color=0xE3342F,  # roboat red
            )
            embed.add_field(name="User ID",   value=str(user.id),        inline=True)
            embed.add_field(name="Friends",   value=f"{friends:,}",      inline=True)
            embed.add_field(name="Followers", value=f"{followers:,}",    inline=True)
            if user.description:
                embed.add_field(name="Bio", value=user.description[:200], inline=False)
            if user.is_banned:
                embed.add_field(name="⚠️", value="This account is banned", inline=False)
            if avatar_url := avatar_urls.get(user_id):
                embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text="roboat.pro")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    @bot.tree.command(name="game", description="Look up a Roblox game by universe ID")
    @app_commands.describe(universe_id="The Roblox universe ID")
    async def cmd_game(interaction: discord.Interaction, universe_id: int):
        await interaction.response.defer()
        try:
            game = await bot.roblox.games.get_game(universe_id)
            votes = await bot.roblox.games.get_votes([universe_id])
            icons = await bot.roblox.thumbnails.get_game_icons([universe_id])

            embed = discord.Embed(
                title=game.name,
                description=game.description[:200] if game.description else "",
                color=0xE3342F,
            )
            embed.add_field(name="Visits",    value=f"{game.visits:,}",    inline=True)
            embed.add_field(name="Playing",   value=f"{game.playing:,}",   inline=True)
            embed.add_field(name="Max",       value=f"{game.max_players}", inline=True)
            embed.add_field(name="Creator",   value=game.creator_name,     inline=True)
            embed.add_field(name="Genre",     value=game.genre,            inline=True)
            if votes:
                embed.add_field(name="Likes", value=f"{votes[0].ratio}%", inline=True)
            if icon := icons.get(universe_id):
                embed.set_thumbnail(url=icon)
            embed.set_footer(text="roboat.pro")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    @bot.tree.command(name="status", description="Check a user's online status")
    @app_commands.describe(user_id="The Roblox user ID")
    async def cmd_status(interaction: discord.Interaction, user_id: int):
        await interaction.response.defer()
        try:
            user = await bot.roblox.users.get_user(user_id)
            presence = await bot.roblox.presence.get_presence(user_id)

            status_emoji = {"Offline": "⚫", "Online": "🟡", "In Game": "🟢", "In Studio": "🔧"}
            emoji = status_emoji.get(presence.status, "❓")

            embed = discord.Embed(
                title=f"{emoji} {user.display_name} — {presence.status}",
                color=0xE3342F,
            )
            if presence.last_location:
                embed.add_field(name="Location", value=presence.last_location, inline=False)
            if presence.last_online:
                embed.add_field(name="Last Online", value=presence.last_online[:10], inline=True)
            embed.set_footer(text="roboat.pro")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    return bot


if __name__ == "__main__":
    if not DISCORD_AVAILABLE:
        print("Install discord.py first: pip install discord.py")
    else:
        TOKEN = os.environ.get("DISCORD_TOKEN", "")
        if not TOKEN:
            print("Set DISCORD_TOKEN environment variable")
        else:
            bot = create_bot()
            bot.run(TOKEN)
