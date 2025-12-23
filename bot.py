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
APPROVAL_CHANNEL_ID = int(os.getenv("APPROVAL_CHANNEL_ID", "0"))  # Merkez onay kanalı
TEAM_ROLE_ID = int(os.getenv("TEAM_ROLE_ID", "0"))  # Merkez ekip rolü

# Data file paths
SERVERS_FILE = "servers.json"
MESSAGES_FILE = "messages.json"


# ============== Data Functions ==============

def load_servers():
    """Load server configurations from JSON file."""
    if os.path.exists(SERVERS_FILE):
        with open(SERVERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_servers(data):
    """Save server configurations to JSON file."""
    with open(SERVERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_messages():
    """Load messages from JSON file."""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pending": [], "approved": [], "rejected": []}


def save_messages(data):
    """Save messages to JSON file."""
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_server_approved_messages(guild_id: int):
    """Get approved messages for a specific server."""
    data = load_messages()
    return [msg for msg in data["approved"] if msg.get("guild_id") == guild_id]


# ============== Bot Setup ==============

class UnsentBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

    async def on_ready(self):
        print(f"{self.user} is now running!")
        print(f"Approval Channel ID: {APPROVAL_CHANNEL_ID}")
        print(f"Team Role ID: {TEAM_ROLE_ID}")
        print(f"Bot is in {len(self.guilds)} servers:")
        for guild in self.guilds:
            print(f"  - {guild.name} ({guild.id})")


bot = UnsentBot()


# ============== Channel Setup Command ==============

@bot.command(name="kanal")
@commands.has_permissions(administrator=True)
async def setup_channel(ctx, channel: discord.TextChannel = None):
    """Set the channel where approved messages will be displayed."""
    guild = ctx.guild

    # If no channel specified, use current channel
    if channel is None:
        channel = ctx.channel

    # Save server configuration
    servers = load_servers()
    servers[str(guild.id)] = {
        "guild_name": guild.name,
        "messages_channel_id": channel.id,
        "setup_at": datetime.now().isoformat(),
        "setup_by": ctx.author.id
    }
    save_servers(servers)

    embed = discord.Embed(
        title="✅ Kanal Ayarlandı!",
        color=discord.Color.green()
    )
    embed.add_field(
        name="💌 Mesaj Kanalı",
        value=f"{channel.mention}\n\nOnaylanan mesajlar bu kanalda görünecek.",
        inline=False
    )
    embed.add_field(
        name="📋 Komutlar",
        value=(
            "`/mesaj` - Anonim mesaj gönder\n"
            "`/isim <isim>` - İsme göre mesaj ara\n"
            "`/isimler` - Tüm isimleri listele"
        ),
        inline=False
    )
    embed.set_footer(text=f"Ayarlayan: {ctx.author.name}")

    await ctx.send(embed=embed)


@setup_channel.error
async def setup_channel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın!")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("❌ Kanal bulunamadı! Doğru kanal adını yazdığından emin ol.")


# ============== Message Modal ==============

class MessageModal(discord.ui.Modal, title="Gönderilmemiş Mesaj"):
    recipient_name = discord.ui.TextInput(
        label="Kime?",
        placeholder="Mesajı göndermek istediğin kişinin ismi...",
        required=True,
        max_length=100,
    )

    message_content = discord.ui.TextInput(
        label="Mesajın",
        style=discord.TextStyle.paragraph,
        placeholder="Göndermek istediğin mesajı yaz...",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        guild_name = interaction.guild.name
        servers = load_servers()

        # Check if server is set up
        if str(guild_id) not in servers:
            await interaction.response.send_message(
                "❌ Bu sunucuda mesaj kanalı ayarlanmamış!\n"
                "Bir yönetici `!kanal #kanal-adı` yazmalı.",
                ephemeral=True
            )
            return

        # Create message entry
        message_id = f"{guild_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        message_entry = {
            "id": message_id,
            "recipient": self.recipient_name.value.strip(),
            "content": self.message_content.value.strip(),
            "submitted_at": datetime.now().isoformat(),
            "submitted_by": interaction.user.id,
            "guild_id": guild_id,
            "guild_name": guild_name
        }

        # Save to pending
        data = load_messages()
        data["pending"].append(message_entry)
        save_messages(data)

        # Send to central approval channel
        approval_channel = bot.get_channel(APPROVAL_CHANNEL_ID)
        if approval_channel:
            embed = discord.Embed(
                title="📬 Yeni Mesaj Onay Bekliyor",
                color=discord.Color.yellow(),
            )
            embed.add_field(
                name="🏠 Sunucu",
                value=guild_name,
                inline=True,
            )
            embed.add_field(
                name="💌 Kime",
                value=self.recipient_name.value,
                inline=True,
            )
            embed.add_field(
                name="📝 Mesaj",
                value=self.message_content.value,
                inline=False,
            )
            embed.set_footer(text=f"ID: {message_id}")

            # Create approval buttons
            view = ApprovalView(message_id, guild_id)

            # Tag the team role
            team_mention = f"<@&{TEAM_ROLE_ID}>" if TEAM_ROLE_ID else ""

            await approval_channel.send(
                content=f"{team_mention} Yeni bir mesaj onay bekliyor!",
                embed=embed,
                view=view,
            )
        else:
            await interaction.response.send_message(
                "⚠️ Mesajın kaydedildi ama onay kanalına gönderilemedi. "
                "Bot yöneticisine haber ver.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "✅ Mesajın gönderildi! Ekip onayladıktan sonra görünür olacak.",
            ephemeral=True,
        )


# ============== Approval Buttons ==============

class ApprovalView(discord.ui.View):
    def __init__(self, message_id: str, guild_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.guild_id = guild_id

    @discord.ui.button(
        label="Onayla",
        style=discord.ButtonStyle.green,
        emoji="✅",
    )
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_messages()
        servers = load_servers()

        # Find the message in pending
        message_entry = None
        for msg in data["pending"]:
            if msg["id"] == self.message_id:
                message_entry = msg
                break

        if not message_entry:
            await interaction.response.send_message(
                "❌ Bu mesaj bulunamadı veya zaten işlem yapılmış.",
                ephemeral=True,
            )
            return

        # Move to approved
        data["pending"].remove(message_entry)
        message_entry["approved_at"] = datetime.now().isoformat()
        message_entry["approved_by"] = interaction.user.id
        data["approved"].append(message_entry)
        save_messages(data)

        # Post to the server's messages channel
        server_config = servers.get(str(self.guild_id), {})
        messages_channel_id = server_config.get("messages_channel_id")
        messages_channel = bot.get_channel(messages_channel_id) if messages_channel_id else None

        if messages_channel:
            embed = discord.Embed(
                title=f"💌 Sevgili {message_entry['recipient']},",
                description=message_entry["content"],
                color=discord.Color.pink(),
            )
            embed.set_footer(text="Gönderilmemiş Mesajlar 💕")
            await messages_channel.send(embed=embed)
            channel_status = f"✅ {messages_channel.mention} kanalına gönderildi"
        else:
            channel_status = "⚠️ Hedef kanal bulunamadı"

        # Update the approval message
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Mesaj Onaylandı"
        embed.add_field(
            name="👤 Onaylayan",
            value=interaction.user.mention,
            inline=True,
        )
        embed.add_field(
            name="📤 Durum",
            value=channel_status,
            inline=True,
        )

        # Disable buttons
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Reddet",
        style=discord.ButtonStyle.red,
        emoji="❌",
    )
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_messages()

        # Find the message in pending
        message_entry = None
        for msg in data["pending"]:
            if msg["id"] == self.message_id:
                message_entry = msg
                break

        if not message_entry:
            await interaction.response.send_message(
                "❌ Bu mesaj bulunamadı veya zaten işlem yapılmış.",
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
            name="👤 Reddeden",
            value=interaction.user.mention,
            inline=False,
        )

        # Disable buttons
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


# ============== Slash Commands ==============

@bot.tree.command(name="mesaj", description="Gönderilmemiş bir mesaj gönder")
async def mesaj(interaction: discord.Interaction):
    """Open the message submission modal."""
    servers = load_servers()

    if str(interaction.guild_id) not in servers:
        await interaction.response.send_message(
            "❌ Bu sunucuda mesaj kanalı ayarlanmamış!\n"
            "Bir yönetici `!kanal #kanal-adı` yazmalı.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(MessageModal())


@bot.tree.command(name="isim", description="Bir isme gönderilen mesajları ara")
@app_commands.describe(isim="Aramak istediğin isim")
async def isim(interaction: discord.Interaction, isim: str):
    """Search for messages by recipient name."""
    approved_messages = get_server_approved_messages(interaction.guild_id)

    # Search in approved messages (case-insensitive)
    matching_messages = [
        msg for msg in approved_messages
        if isim.lower() in msg["recipient"].lower()
    ]

    if not matching_messages:
        await interaction.response.send_message(
            f"❌ '{isim}' için gönderilmemiş mesaj bulunamadı.",
            ephemeral=True,
        )
        return

    # Create embeds for each message
    embeds = []
    for msg in matching_messages[:10]:  # Limit to 10 messages
        embed = discord.Embed(
            title=f"💌 Sevgili {msg['recipient']},",
            description=msg["content"],
            color=discord.Color.pink(),
        )
        embed.set_footer(text="Gönderilmemiş Mesajlar 💕")
        embeds.append(embed)

    total = len(matching_messages)
    shown = min(total, 10)

    await interaction.response.send_message(
        content=f"🔍 '{isim}' için {total} mesaj bulundu (gösterilen: {shown}):",
        embeds=embeds,
        ephemeral=True,
    )


@bot.tree.command(name="isimler", description="Mesaj gönderilen tüm isimleri listele")
async def isimler(interaction: discord.Interaction):
    """List all recipient names with approved messages."""
    approved_messages = get_server_approved_messages(interaction.guild_id)

    # Get unique names
    names = set(msg["recipient"] for msg in approved_messages)

    if not names:
        await interaction.response.send_message(
            "📭 Henüz onaylanmış mesaj bulunmuyor.",
            ephemeral=True,
        )
        return

    # Sort names alphabetically
    sorted_names = sorted(names, key=str.lower)

    embed = discord.Embed(
        title="💌 Gönderilmemiş Mesajlar",
        description="Aşağıdaki isimlere mesaj gönderilmiş:",
        color=discord.Color.pink(),
    )

    # Split names into chunks if too many
    name_list = "\n".join(f"• {name}" for name in sorted_names[:50])
    embed.add_field(name="📋 İsimler", value=name_list or "Yok", inline=False)

    if len(sorted_names) > 50:
        embed.set_footer(text=f"...ve {len(sorted_names) - 50} isim daha")
    else:
        embed.set_footer(text=f"Toplam {len(sorted_names)} isim")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="istatistik", description="Mesaj istatistiklerini göster")
@app_commands.default_permissions(administrator=True)
async def istatistik(interaction: discord.Interaction):
    """Show message statistics (admin only)."""
    data = load_messages()

    # Global stats
    total_pending = len(data["pending"])
    total_approved = len(data["approved"])
    total_rejected = len(data["rejected"])

    # Server-specific stats
    server_approved = len(get_server_approved_messages(interaction.guild_id))
    server_pending = len([m for m in data["pending"] if m.get("guild_id") == interaction.guild_id])

    embed = discord.Embed(
        title="📊 Mesaj İstatistikleri",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="🏠 Bu Sunucu",
        value=f"⏳ Bekleyen: {server_pending}\n✅ Onaylanan: {server_approved}",
        inline=True,
    )
    embed.add_field(
        name="🌍 Toplam (Tüm Sunucular)",
        value=f"⏳ Bekleyen: {total_pending}\n✅ Onaylanan: {total_approved}\n❌ Reddedilen: {total_rejected}",
        inline=True,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ============== Help Command ==============

@bot.command(name="yardim")
async def yardim(ctx):
    """Show help message."""
    embed = discord.Embed(
        title="💌 Gönderilmemiş Mesajlar Bot",
        description="Anonim mesaj gönderme sistemi",
        color=discord.Color.pink()
    )
    embed.add_field(
        name="👑 Yönetici Komutları",
        value="`!kanal #kanal` - Mesajların görüneceği kanalı ayarla",
        inline=False
    )
    embed.add_field(
        name="👤 Kullanıcı Komutları",
        value=(
            "`/mesaj` - Anonim mesaj gönder\n"
            "`/isim <isim>` - İsme göre mesaj ara\n"
            "`/isimler` - Tüm isimleri listele\n"
            "`/istatistik` - İstatistikleri göster"
        ),
        inline=False
    )
    embed.add_field(
        name="❓ Nasıl Çalışır?",
        value=(
            "1. Yönetici `!kanal #kanal` ile mesaj kanalını ayarlar\n"
            "2. Üyeler `/mesaj` ile anonim mesaj gönderir\n"
            "3. Merkez ekip mesajları onaylar veya reddeder\n"
            "4. Onaylanan mesajlar ayarlanan kanalda görünür"
        ),
        inline=False
    )
    await ctx.send(embed=embed)


# ============== Run Bot ==============

if __name__ == "__main__":
    if not TOKEN:
        print("=" * 50)
        print("HATA: DISCORD_TOKEN bulunamadi!")
        print("Lutfen .env dosyasini kontrol edin.")
        print("=" * 50)
        exit(1)

    if not APPROVAL_CHANNEL_ID:
        print("=" * 50)
        print("HATA: APPROVAL_CHANNEL_ID bulunamadi!")
        print("Merkez onay kanalinin ID'sini .env dosyasina ekleyin.")
        print("=" * 50)
        exit(1)

    print("Bot baslatiliyor...")
    bot.run(TOKEN)
