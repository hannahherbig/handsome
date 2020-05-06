import asyncio

import discord
import toml


class MyClient(discord.Client):
    async def __init__(self, updates_channel):
        self.updates_channel_id = updates_channel
        super().__init__()

    async def on_ready(self):
        print(f"I'm {self.user}")
        self.updates_channel = self.get_channel(self.updates_channel_id)

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
                await message.delete(delay=10)


def main():
    with open("config.toml", "r") as f:
        config = toml.load(f)

    client = MyClient(config["channel"])
    client.run(config["token"])
