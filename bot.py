import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
APPROVAL_CHANNEL_ID = int(os.getenv("APPROVAL_CHANNEL_ID", "0"))
APPROVED_CHANNEL_ID = int(os.getenv("APPROVED_CHANNEL_ID", "0"))
TEAM_ROLE_ID = int(os.getenv("TEAM_ROLE_ID", "0"))

# Data file path
DATA_FILE = "messages.json"


def load_messages():
    """Load messages from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pending": [], "approved": [], "rejected": []}


def save_messages(data):
    """Save messages to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class UnsentBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

    async def on_ready(self):
        print(f"{self.user} is now running!")
        print(f"Approval Channel ID: {APPROVAL_CHANNEL_ID}")
        print(f"Approved Channel ID: {APPROVED_CHANNEL_ID}")
        print(f"Team Role ID: {TEAM_ROLE_ID}")


bot = UnsentBot()


# Modal for submitting messages
class MessageModal(discord.ui.Modal, title="Gonderilmemis Mesaj"):
    recipient_name = discord.ui.TextInput(
        label="Kime?",
        placeholder="Mesaji gondermek istedigin kisinin ismi...",
        required=True,
        max_length=100,
    )

    message_content = discord.ui.TextInput(
        label="Mesajin",
        style=discord.TextStyle.paragraph,
        placeholder="Gondermek istedigin mesaji yaz...",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Create message entry
        message_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        message_entry = {
            "id": message_id,
            "recipient": self.recipient_name.value.strip(),
            "content": self.message_content.value.strip(),
            "submitted_at": datetime.now().isoformat(),
            "submitted_by": interaction.user.id,
        }

        # Save to pending
        data = load_messages()
        data["pending"].append(message_entry)
        save_messages(data)

        # Send to approval channel
        approval_channel = bot.get_channel(APPROVAL_CHANNEL_ID)
        if approval_channel:
            embed = discord.Embed(
                title="Yeni Mesaj Onay Bekliyor",
                color=discord.Color.yellow(),
            )
            embed.add_field(
                name="Kime",
                value=self.recipient_name.value,
                inline=False,
            )
            embed.add_field(
                name="Mesaj",
                value=self.message_content.value,
                inline=False,
            )
            embed.set_footer(text=f"ID: {message_id}")

            # Create approval buttons
            view = ApprovalView(message_id)

            # Tag the team role
            team_mention = f"<@&{TEAM_ROLE_ID}>" if TEAM_ROLE_ID else ""
            await approval_channel.send(
                content=f"{team_mention} Yeni bir mesaj onay bekliyor!",
                embed=embed,
                view=view,
            )

        await interaction.response.send_message(
            "Mesajin gonderildi! Ekip onayladiktan sonra gorunur olacak.",
            ephemeral=True,
        )


# Approval buttons
class ApprovalView(discord.ui.View):
    def __init__(self, message_id: str):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(
        label="Onayla",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="approve_button",
    )
    async def approve(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = load_messages()

        # Find the message in pending
        message_entry = None
        for msg in data["pending"]:
            if msg["id"] == self.message_id:
                message_entry = msg
                break

        if not message_entry:
            await interaction.response.send_message(
                "Bu mesaj bulunamadi veya zaten islem yapilmis.",
                ephemeral=True,
            )
            return

        # Move to approved
        data["pending"].remove(message_entry)
        message_entry["approved_at"] = datetime.now().isoformat()
        message_entry["approved_by"] = interaction.user.id
        data["approved"].append(message_entry)
        save_messages(data)

        # Post to approved channel
        approved_channel = bot.get_channel(APPROVED_CHANNEL_ID)
        if approved_channel:
            embed = discord.Embed(
                title=f"Sevgili {message_entry['recipient']},",
                description=message_entry["content"],
                color=discord.Color.pink(),
            )
            embed.set_footer(text="Gonderilmemis Mesajlar")
            await approved_channel.send(embed=embed)

        # Update the approval message
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Mesaj Onaylandi"
        embed.add_field(
            name="Onaylayan",
            value=interaction.user.mention,
            inline=False,
        )

        # Disable buttons
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Reddet",
        style=discord.ButtonStyle.red,
        emoji="❌",
        custom_id="reject_button",
    )
    async def reject(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = load_messages()

        # Find the message in pending
        message_entry = None
        for msg in data["pending"]:
            if msg["id"] == self.message_id:
                message_entry = msg
                break

        if not message_entry:
            await interaction.response.send_message(
                "Bu mesaj bulunamadi veya zaten islem yapilmis.",
                ephemeral=True,
            )
            return

        # Move to rejected
        data["pending"].remove(message_entry)
        message_entry["rejected_at"] = datetime.now().isoformat()
        message_entry["rejected_by"] = interaction.user.id
        data["rejected"].append(message_entry)
        save_messages(data)

        # Update the approval message
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ Mesaj Reddedildi"
        embed.add_field(
            name="Reddeden",
            value=interaction.user.mention,
            inline=False,
        )

        # Disable buttons
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


# Slash command to submit a message
@bot.tree.command(name="mesaj", description="Gonderilmemis bir mesaj gonder")
async def mesaj(interaction: discord.Interaction):
    """Open the message submission modal."""
    await interaction.response.send_modal(MessageModal())


# Slash command to search messages by name
@bot.tree.command(name="isim", description="Bir isme gonderilen mesajlari ara")
@app_commands.describe(isim="Aramak istedigin isim")
async def isim(interaction: discord.Interaction, isim: str):
    """Search for messages by recipient name."""
    data = load_messages()

    # Search in approved messages (case-insensitive)
    matching_messages = [
        msg
        for msg in data["approved"]
        if isim.lower() in msg["recipient"].lower()
    ]

    if not matching_messages:
        await interaction.response.send_message(
            f"'{isim}' icin gonderilmemis mesaj bulunamadi.",
            ephemeral=True,
        )
        return

    # Create embeds for each message
    embeds = []
    for msg in matching_messages[:10]:  # Limit to 10 messages
        embed = discord.Embed(
            title=f"Sevgili {msg['recipient']},",
            description=msg["content"],
            color=discord.Color.pink(),
        )
        embed.set_footer(text="Gonderilmemis Mesajlar")
        embeds.append(embed)

    await interaction.response.send_message(
        content=f"'{isim}' icin {len(matching_messages)} mesaj bulundu:",
        embeds=embeds,
        ephemeral=True,
    )


# Slash command to list all names with messages
@bot.tree.command(
    name="isimler", description="Mesaj gonderilen tum isimleri listele"
)
async def isimler(interaction: discord.Interaction):
    """List all recipient names with approved messages."""
    data = load_messages()

    # Get unique names
    names = set(msg["recipient"] for msg in data["approved"])

    if not names:
        await interaction.response.send_message(
            "Henuz onaylanmis mesaj bulunmuyor.",
            ephemeral=True,
        )
        return

    # Sort names alphabetically
    sorted_names = sorted(names, key=str.lower)

    embed = discord.Embed(
        title="Gonderilmemis Mesajlar",
        description="Asagidaki isimlere mesaj gonderilmis:",
        color=discord.Color.pink(),
    )

    # Split names into chunks if too many
    name_list = "\n".join(f"• {name}" for name in sorted_names[:50])
    embed.add_field(name="Isimler", value=name_list or "Yok", inline=False)

    if len(sorted_names) > 50:
        embed.set_footer(text=f"...ve {len(sorted_names) - 50} isim daha")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# Admin command to view stats
@bot.tree.command(name="istatistik", description="Mesaj istatistiklerini goster")
@app_commands.default_permissions(administrator=True)
async def istatistik(interaction: discord.Interaction):
    """Show message statistics (admin only)."""
    data = load_messages()

    embed = discord.Embed(
        title="Mesaj Istatistikleri",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="Bekleyen Mesajlar",
        value=str(len(data["pending"])),
        inline=True,
    )
    embed.add_field(
        name="Onaylanan Mesajlar",
        value=str(len(data["approved"])),
        inline=True,
    )
    embed.add_field(
        name="Reddedilen Mesajlar",
        value=str(len(data["rejected"])),
        inline=True,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
        exit(1)

    bot.run(TOKEN)
