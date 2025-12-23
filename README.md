# Gonderilmemis Mesajlar Discord Bot

Discord uzerinde calisan bir "Unsent Project" benzeri bot. Kullanicilar anonim mesajlar gonderebilir, ekip onayladiktan sonra mesajlar gorunur olur.

## Ozellikler

- `/mesaj` - Anonim mesaj gondermek icin form acar
- `/isim <isim>` - Belirtilen isme gonderilen onaylanmis mesajlari gosterir
- `/isimler` - Mesaj gonderilen tum isimleri listeler
- `/istatistik` - Mesaj istatistiklerini gosterir (yalnizca yoneticiler)

## Kurulum

### 1. Discord Bot Olusturma

1. [Discord Developer Portal](https://discord.com/developers/applications)'a gidin
2. "New Application" butonuna tiklayin
3. Bot'a bir isim verin ve olusturun
4. Sol menuden "Bot" sekmesine gidin
5. "Reset Token" butonuna tiklayip tokeni kopyalayin
6. "MESSAGE CONTENT INTENT" secenegini aktif edin

### 2. Bot'u Sunucuya Ekleme

1. Sol menuden "OAuth2" > "URL Generator" sekmesine gidin
2. Scopes: `bot`, `applications.commands`
3. Bot Permissions:
   - Send Messages
   - Embed Links
   - Use Slash Commands
   - Mention Everyone (rol etiketlemek icin)
4. Olusturulan URL ile botu sunucunuza ekleyin

### 3. Sunucu Ayarlari

1. Discord'da Kullanici Ayarlari > Gelismis > Gelistirici Modu'nu acin
2. Onay kanali olusturun (sadece ekibin gorecegi)
3. Onaylanan mesajlar kanali olusturun (herkesin gorecegi)
4. Ekip rolu olusturun veya mevcut rolu kullanin
5. Kanal ve rol ID'lerini kopyalayin (sag tik > ID'yi Kopyala)

### 4. Bot Yapilandirmasi

```bash
# Repoyu klonlayin
git clone <repo-url>
cd Gonderilmemis-Mesajlar

# Sanal ortam olusturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Gereksinimleri yukleyin
pip install -r requirements.txt

# .env dosyasini olusturun
cp .env.example .env
```

`.env` dosyasini duzenleyin:

```env
DISCORD_TOKEN=your_bot_token_here
APPROVAL_CHANNEL_ID=123456789012345678
APPROVED_CHANNEL_ID=123456789012345678
TEAM_ROLE_ID=123456789012345678
```

### 5. Bot'u Calistirma

```bash
python bot.py
```

## Kullanim

### Mesaj Gonderme
1. Herhangi bir kanalda `/mesaj` yazin
2. Acilan formda alicinin adini ve mesajinizi yazin
3. Mesaj ekip onayina gonderilir

### Mesaj Onaylama (Ekip)
1. Onay kanalinda yeni mesaj bildirimi alin
2. Yesil "Onayla" veya kirmizi "Reddet" butonuna tiklayin
3. Onaylanan mesajlar otomatik olarak onaylanan mesajlar kanalina gonderilir

### Mesaj Arama
1. `/isim Ahmet` yazarak "Ahmet" ismine gonderilen mesajlari gorun
2. `/isimler` yazarak tum isimleri listeleyin

## Dosya Yapisi

```
Gonderilmemis-Mesajlar/
├── bot.py              # Ana bot kodu
├── requirements.txt    # Python gereksinimleri
├── .env.example        # Ornek yapilandirma
├── .env                # Gercek yapilandirma (git'e eklenmez)
├── messages.json       # Mesaj veritabani (git'e eklenmez)
└── README.md           # Bu dosya
```

## Lisans

MIT
