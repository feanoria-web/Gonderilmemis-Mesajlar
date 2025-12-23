# Gönderilmemiş Mesajlar Discord Bot

Discord üzerinde çalışan bir "Unsent Project" benzeri bot. Kullanıcılar anonim mesajlar gönderebilir, ekip onayladıktan sonra mesajlar görünür olur.

**Çoklu sunucu desteği:** Bot birden fazla Discord sunucusunda çalışabilir. Her sunucu kendi kanallarına ve mesajlarına sahip olur.

## Özellikler

| Komut | Açıklama |
|-------|----------|
| `!kanal` | Sistemi otomatik kur (kanallar + roller) |
| `!yardim` | Yardım mesajını göster |
| `/mesaj` | Anonim mesaj gönder |
| `/isim <isim>` | İsme göre mesaj ara |
| `/isimler` | Tüm isimleri listele |
| `/istatistik` | İstatistikleri göster |

## Hızlı Kurulum (Windows)

### Adım 1: Python Kur

1. https://www.python.org/downloads/ adresine git
2. "Download Python" butonuna tıkla
3. İndirilen dosyayı çalıştır
4. **ÖNEMLİ:** "Add Python to PATH" kutusunu işaretle ✅
5. "Install Now" tıkla

### Adım 2: Discord Bot Oluştur

1. https://discord.com/developers/applications adresine git
2. Sağ üstte "New Application" tıkla
3. İsim ver → Create
4. Sol menüden "Bot" sekmesine git
5. "Reset Token" tıkla → Tokeni kopyala ve sakla
6. Aşağı kaydır:
   - "MESSAGE CONTENT INTENT" → AÇ
   - "SERVER MEMBERS INTENT" → AÇ
7. "Save Changes" tıkla

### Adım 3: Bot'u Sunuculara Ekle

1. Sol menüden "OAuth2" → "URL Generator" git
2. SCOPES bölümünden seç:
   - ✅ `bot`
   - ✅ `applications.commands`
3. BOT PERMISSIONS bölümünden seç:
   - ✅ `Administrator` (en kolay yol)

   Ya da tek tek:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Manage Channels
   - ✅ Manage Roles
   - ✅ Mention Everyone

4. En alttaki URL'yi kopyala
5. Bu URL ile istediğin kadar sunucuya ekle

### Adım 4: Bot'u Çalıştır

1. Bot klasörüne git: `C:\Users\gurka\Desktop\Gonderilmemis-Mesajlar-claude-discord-unsent-messages-bot-lDlmR`

2. `.env.example` dosyasını kopyala ve adını `.env` yap

3. `.env` dosyasını Not Defteri ile aç:
```
DISCORD_TOKEN=buraya_tokenini_yapistir
```

4. Klasörde adres çubuğuna `cmd` yaz, Enter'a bas

5. Şu komutları çalıştır:
```cmd
pip install -r requirements.txt
python bot.py
```

6. "Bot is now running!" görünce hazır!

### Adım 5: Sunucuda Kur

1. Bot'un ekli olduğu herhangi bir Discord sunucusuna git
2. Herhangi bir kanalda `!kanal` yaz
3. Bot otomatik olarak şunları oluşturur:
   - 📁 "Gönderilmemiş Mesajlar" kategorisi
   - 🔒 #onay-bekleyenler kanalı (sadece ekip görür)
   - 💌 #gönderilmemiş-mesajlar kanalı (herkes görür)
   - 👥 "Mesaj Ekibi" rolü

4. Mesajları onaylayacak kişilere "Mesaj Ekibi" rolünü ver

## Nasıl Çalışır?

```
Kullanıcı                    Ekip                      Herkes
   │                          │                          │
   │ /mesaj                   │                          │
   │ "Ahmet'e: Seni özledim"  │                          │
   ▼                          │                          │
   ──────────────────────────►│                          │
                              │ #onay-bekleyenler        │
                              │ [Onayla] [Reddet]        │
                              │                          │
                              │ ✅ Onayla                │
                              ▼                          │
                              ──────────────────────────►│
                                                         │ #gönderilmemiş-mesajlar
                                                         │ 💌 Sevgili Ahmet,
                                                         │ Seni özledim
```

## Dosya Yapısı

```
📁 Gonderilmemis-Mesajlar/
├── 📄 bot.py              # Ana bot kodu
├── 📄 requirements.txt    # Python gereksinimleri
├── 📄 .env.example        # Örnek ayar dosyası
├── 📄 .env                # Gerçek ayarlar (git'e eklenmez)
├── 📄 servers.json        # Sunucu ayarları (otomatik oluşur)
├── 📄 messages.json       # Mesajlar (otomatik oluşur)
└── 📄 README.md           # Bu dosya
```

## Sorun Giderme

**"python bulunamadı" hatası:**
- Python'u yeniden kur, "Add to PATH" işaretli olsun

**Bot çalışıyor ama komutlar görünmüyor:**
- 1-2 dakika bekle, slash komutları yükleniyor
- Discord'u kapat aç

**"Bot'un yeterli yetkisi yok" hatası:**
- Bot'u sunucuya eklerken "Administrator" yetkisini ver
- Ya da "Manage Channels" ve "Manage Roles" yetkilerini ver

**Butonlar çalışmıyor:**
- Bot'u yeniden başlat
- Bot çevrimdışıyken butonlar çalışmaz

## Lisans

MIT
