import discord
import os
from keep import keep_alive
from discord import (
    Interaction,
    Intents,
    Client,
    Message,
    Embed,
    ui,
    ButtonStyle,
    ChannelType    
)
import discord
from discord.app_commands import CommandTree
import pprint


class MyClient(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self) -> None:
        await super().setup_hook()
        synced_commands = await self.tree.sync()
        pprint.pprint(synced_commands)

    async def on_ready(self):
        print(f"Logged in as {client.user} (ID: {client.user.id})")
        print("------")


intents = Intents.default()
client = MyClient(intents=intents)

class SendChannelView(ui.View):
    def __init__(self, embed: Embed, url_view: ui.View):
        super().__init__()
        self.send_embed = embed
        self.send_url_view = url_view

    @ui.select(
        cls=ui.ChannelSelect,
        placeholder="select channel",
        channel_types=[ChannelType.text],
    )
    async def set_channel(self, interaction: Interaction, select: ui.ChannelSelect):

        self.send_button.disabled = False
        self.send_button.style = ButtonStyle.green

        self.fav_channel = await select.values[0].fetch()

    @ui.button(label="Send")
    async def send_button(self, interaction: Interaction, button: ui.Button):

        for item in self.children:
            item.disabled = True
            self.send_button.style = ButtonStyle.gray
            await interaction.response.edit_message(view=self)
            await self.fav_channel.send(embed=self.send_embed, view=self.send_url_view)
            await interaction.delete_original_response()

@client.tree.context_menu()
async def message_forward(interaction: Interaction, message: Message):
    embed = discord.Embed(title=None)
    if message.content:
        embed.description = message.content
        embed.timestamp = message.created_at

        embed.set_author(
            name=message.author.display_name, 
            icon_url=message.author.display_avatar.url,
            ).set_footer(
                text=f"forwarded from {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url,
                )

        url_view = ui.View()
        url_view.add_item(
            ui.Button(
                label="Go to Message", style=ButtonStyle.url, url=message.jump_url
            )
        )

        send_channel_view = SendChannelView(embed=embed, url_view=url_view)

        await interaction.response.send_message("embed", embed=embed, view=url_view)
        await interaction.followup.send(view=send_channel_view)

keep_alive()
try:
    client.run(os.environ['DISCORD_TOKEN'])
except:
    os.system("kill")


