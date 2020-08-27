import argparse
import asyncio
from typing import List

import aioredis
import discord
import toml
from devtools import debug
from pydantic import BaseModel


class Config(BaseModel):
    text: List[int]
    token: str
    delay: int = 15


class MeuMeu(discord.Client):
    def __init__(self, cfg: Config):
        self.cfg: Config = cfg
        self.redis = None
        super().__init__()

    def run(self):
        super().run(self.cfg.token)

    async def connect_redis(self):
        if self.redis is None or self.redis.closed:
            self.redis = await aioredis.create_connection("redis://localhost")

    async def on_ready(self):
        debug(self.user)

    #     self.owner = self.get_user(self.cfg.owner)
    #     debug(self.owner)
    #     await self.connect_redis()

    # async def on_message(self, message):
    #     if message.author != self.user and self.user.mentioned_in(message) and

    async def on_voice_state_update(self, member, before, after):
        content = None
        if before.channel is None:
            content = f":arrow_right: {member.mention} joined **{after.channel}**"
        elif after.channel is None:
            content = f":arrow_left: {member.mention} left **{before.channel}**"
        elif before.channel != after.channel:
            if after.channel.position > before.channel.position:
                emoji = ":arrow_down:"
            else:
                emoji = ":arrow_up:"
            content = f"{emoji} {member.mention} moved from **{before.channel}** to **{after.channel}**"
        if content:
            for channel_id in self.cfg.text:
                channel = self.get_channel(channel_id)
                if channel.guild == member.guild:
                    break
            else:
                channel = None

            message = await channel.send(
                content,
                allowed_mentions=discord.AllowedMentions(
                    everyone=False, users=False, roles=False
                ),
            )
            await message.delete(delay=self.cfg.delay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", default="config.toml")
    args = parser.parse_args()

    with open(args.config) as f:
        config = toml.load(f)

    cfg = Config(**config)
    debug(cfg)

    client = MeuMeu(cfg)
    client.run()
