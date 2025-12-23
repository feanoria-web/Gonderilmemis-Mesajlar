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
    return {}


def save_messages(data):
    """Save messages to JSON file."""
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_server_messages(guild_id: int):
    """Get messages for a specific server."""
    data = load_messages()
    guild_key = str(guild_id)
    if guild_key not in data:
        data[guild_key] = {"pending": [], "approved": [], "rejected": []}
        save_messages(data)
    return data[guild_key]


def save_server_messages(guild_id: int, server_data):
    """Save messages for a specific server."""
    data = load_messages()
    data[str(guild_id)] = server_data
    save_messages(data)


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
        print(f"Bot is in {len(self.guilds)} servers")
        for guild in self.guilds:
            print(f"  - {guild.name} ({guild.id})")


bot = UnsentBot()


# ============== Channel Setup Command ==============

@bot.command(name="kanal")
@commands.has_permissions(administrator=True)
async def setup_channels(ctx):
    """Set up channels for the unsent messages system."""
    guild = ctx.guild

    await ctx.send("🔧 Kanallar ve roller oluşturuluyor...")

    try:
        # Create the team role
        team_role = discord.utils.get(guild.roles, name="Mesaj Ekibi")
        if not team_role:
            team_role = await guild.create_role(
                name="Mesaj Ekibi",
                color=discord.Color.purple(),
                reason="Gönderilmemiş Mesajlar bot kurulumu"
            )
            await ctx.send(f"✅ '{team_role.name}' rolü oluşturuldu!")
        else:
            await ctx.send(f"ℹ️ '{team_role.name}' rolü zaten var.")

        # Create category
        category = discord.utils.get(guild.categories, name="Gönderilmemiş Mesajlar")
        if not category:
            category = await guild.create_category(
                name="Gönderilmemiş Mesajlar",
                reason="Gönderilmemiş Mesajlar bot kurulumu"
            )
            await ctx.send(f"✅ '{category.name}' kategorisi oluşturuldu!")
        else:
            await ctx.send(f"ℹ️ '{category.name}' kategorisi zaten var.")

        # Create approval channel (only team and admins can see)
        approval_channel = discord.utils.get(guild.text_channels, name="onay-bekleyenler")
        if not approval_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                team_role: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    embed_links=True
                )
            }
            approval_channel = await guild.create_text_channel(
                name="onay-bekleyenler",
                category=category,
                overwrites=overwrites,
                topic="Mesajlar burada onaylanır veya reddedilir. Sadece ekip görebilir.",
                reason="Gönderilmemiş Mesajlar bot kurulumu"
            )
            await ctx.send(f"✅ #{approval_channel.name} kanalı oluşturuldu! (Sadece ekip görebilir)")
        else:
            await ctx.send(f"ℹ️ #{approval_channel.name} kanalı zaten var.")

        # Create public messages channel
        messages_channel = discord.utils.get(guild.text_channels, name="gönderilmemiş-mesajlar")
        if not messages_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=False,
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    embed_links=True
                )
            }
            messages_channel = await guild.create_text_channel(
                name="gönderilmemiş-mesajlar",
                category=category,
                overwrites=overwrites,
                topic="Onaylanmış gönderilmemiş mesajlar burada paylaşılır. /mesaj yazarak mesaj gönderebilirsin!",
                reason="Gönderilmemiş Mesajlar bot kurulumu"
            )
            await ctx.send(f"✅ #{messages_channel.name} kanalı oluşturuldu! (Herkes görebilir)")
        else:
            await ctx.send(f"ℹ️ #{messages_channel.name} kanalı zaten var.")

        # Save server configuration
        servers = load_servers()
        servers[str(guild.id)] = {
            "guild_name": guild.name,
            "approval_channel_id": approval_channel.id,
            "messages_channel_id": messages_channel.id,
            "team_role_id": team_role.id,
            "setup_at": datetime.now().isoformat(),
            "setup_by": ctx.author.id
        }
        save_servers(servers)

        # Send success message
        embed = discord.Embed(
            title="✅ Kurulum Tamamlandı!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Oluşturulan Kanallar",
            value=f"📁 Kategori: **{category.name}**\n"
                  f"🔒 Onay Kanalı: {approval_channel.mention}\n"
                  f"💌 Mesaj Kanalı: {messages_channel.mention}",
            inline=False
        )
        embed.add_field(
            name="Oluşturulan Rol",
            value=f"👥 Ekip Rolü: {team_role.mention}\n\n"
                  f"Bu rolü mesajları onaylayacak kişilere verin!",
            inline=False
        )
        embed.add_field(
            name="Nasıl Kullanılır?",
            value="• Üyeler `/mesaj` yazarak anonim mesaj gönderebilir\n"
                  "• Mesajlar onay kanalına düşer\n"
                  "• Ekip onaylarsa mesaj kanalında yayınlanır\n"
                  "• `/isim Ahmet` ile mesaj aranabilir",
            inline=False
        )
        await ctx.send(embed=embed)

        # Give the command user the team role
        if team_role not in ctx.author.roles:
            await ctx.author.add_roles(team_role)
            await ctx.send(f"ℹ️ {ctx.author.mention}, sana **{team_role.name}** rolü verildi!")

    except discord.Forbidden:
        await ctx.send("❌ Hata: Bot'un yeterli yetkisi yok! Bot'a 'Rolleri Yönet' ve 'Kanalları Yönet' izinlerini verin.")
    except Exception as e:
        await ctx.send(f"❌ Bir hata oluştu: {str(e)}")


@setup_channels.error
async def setup_channels_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın!")


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
        servers = load_servers()

        # Check if server is set up
        if str(guild_id) not in servers:
            await interaction.response.send_message(
                "❌ Bu sunucuda sistem kurulmamış! Bir yönetici `!kanal` yazmalı.",
                ephemeral=True
            )
            return

        server_config = servers[str(guild_id)]

        # Create message entry
        message_id = f"{guild_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        message_entry = {
            "id": message_id,
            "recipient": self.recipient_name.value.strip(),
            "content": self.message_content.value.strip(),
            "submitted_at": datetime.now().isoformat(),
            "submitted_by": interaction.user.id,
            "guild_id": guild_id
        }

        # Save to pending
        server_messages = get_server_messages(guild_id)
        server_messages["pending"].append(message_entry)
        save_server_messages(guild_id, server_messages)

        # Send to approval channel
        approval_channel = bot.get_channel(server_config["approval_channel_id"])
        if approval_channel:
            embed = discord.Embed(
                title="📬 Yeni Mesaj Onay Bekliyor",
                color=discord.Color.yellow(),
            )
            embed.add_field(
                name="💌 Kime",
                value=self.recipient_name.value,
                inline=False,
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
            team_role_id = server_config.get("team_role_id")
            team_mention = f"<@&{team_role_id}>" if team_role_id else ""

            await approval_channel.send(
                content=f"{team_mention} Yeni bir mesaj onay bekliyor!",
                embed=embed,
                view=view,
            )

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
        server_messages = get_server_messages(self.guild_id)
        servers = load_servers()

        # Find the message in pending
        message_entry = None
        for msg in server_messages["pending"]:
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
        server_messages["pending"].remove(message_entry)
        message_entry["approved_at"] = datetime.now().isoformat()
        message_entry["approved_by"] = interaction.user.id
        server_messages["approved"].append(message_entry)
        save_server_messages(self.guild_id, server_messages)

        # Post to approved channel
        server_config = servers.get(str(self.guild_id), {})
        messages_channel = bot.get_channel(server_config.get("messages_channel_id"))

        if messages_channel:
            embed = discord.Embed(
                title=f"💌 Sevgili {message_entry['recipient']},",
                description=message_entry["content"],
                color=discord.Color.pink(),
            )
            embed.set_footer(text="Gönderilmemiş Mesajlar 💕")
            await messages_channel.send(embed=embed)

        # Update the approval message
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Mesaj Onaylandı"
        embed.add_field(
            name="👤 Onaylayan",
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
    )
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        server_messages = get_server_messages(self.guild_id)

        # Find the message in pending
        message_entry = None
        for msg in server_messages["pending"]:
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
        server_messages["pending"].remove(message_entry)
        message_entry["rejected_at"] = datetime.now().isoformat()
        message_entry["rejected_by"] = interaction.user.id
        server_messages["rejected"].append(message_entry)
        save_server_messages(self.guild_id, server_messages)

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
            "❌ Bu sunucuda sistem kurulmamış! Bir yönetici `!kanal` yazmalı.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(MessageModal())


@bot.tree.command(name="isim", description="Bir isme gönderilen mesajları ara")
@app_commands.describe(isim="Aramak istediğin isim")
async def isim(interaction: discord.Interaction, isim: str):
    """Search for messages by recipient name."""
    server_messages = get_server_messages(interaction.guild_id)

    # Search in approved messages (case-insensitive)
    matching_messages = [
        msg
        for msg in server_messages["approved"]
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
    server_messages = get_server_messages(interaction.guild_id)

    # Get unique names
    names = set(msg["recipient"] for msg in server_messages["approved"])

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
    server_messages = get_server_messages(interaction.guild_id)

    embed = discord.Embed(
        title="📊 Mesaj İstatistikleri",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="⏳ Bekleyen",
        value=str(len(server_messages["pending"])),
        inline=True,
    )
    embed.add_field(
        name="✅ Onaylanan",
        value=str(len(server_messages["approved"])),
        inline=True,
    )
    embed.add_field(
        name="❌ Reddedilen",
        value=str(len(server_messages["rejected"])),
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
        name="📋 Komutlar",
        value=(
            "`!kanal` - Sistemi kur (sadece yöneticiler)\n"
            "`!yardim` - Bu mesajı göster\n"
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
            "1. Yönetici `!kanal` yazarak sistemi kurar\n"
            "2. Üyeler `/mesaj` ile anonim mesaj gönderir\n"
            "3. Ekip mesajları onaylar veya reddeder\n"
            "4. Onaylanan mesajlar herkese açık kanalda paylaşılır"
        ),
        inline=False
    )
    await ctx.send(embed=embed)


# ============== Run Bot ==============

if __name__ == "__main__":
    if not TOKEN:
        print("=" * 50)
        print("HATA: DISCORD_TOKEN bulunamadi!")
        print("Lutfen .env dosyasi olusturun ve bot tokeninizi ekleyin.")
        print("=" * 50)
        exit(1)

    print("Bot baslatiliyor...")
    bot.run(TOKEN)
