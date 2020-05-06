import argparse
import asyncio

import discord
import toml
from pydantic import BaseModel


class Config(BaseModel):
    channel: int
    token: str
    delay: int = 15


class MeuMeu(discord.Client):
    def __init__(self, cfg):
        self.cfg = cfg
        super().__init__()

    def run(self):
        super().run(self.cfg.token)

    async def on_ready(self):
        print(f"I'm {self.user}")
        self.updates_channel = self.get_channel(self.cfg.channel)

    async def on_voice_state_update(self, member, before, after):
        if member.guild == self.updates_channel.guild:
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
                message = await self.updates_channel.send(
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

    with open(args.config, "r") as f:
        config = toml.load(f)

    cfg = Config(**config)

    client = MeuMeu(cfg)
    client.run()
