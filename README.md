# Gönderilmemiş Mesajlar Discord Bot

Discord üzerinde çalışan bir "Unsent Project" benzeri bot.

## Nasıl Çalışır?

```
┌─────────────────────────────────────────────────────────────────┐
│                         MERKEZ SUNUCU                           │
│                    (Senin kontrol sunucun)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  #onay-bekleyenler                                       │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │ 📬 Yeni Mesaj Onay Bekliyor                     │    │   │
│  │  │ 🏠 Sunucu: Arkadaş Grubu                        │    │   │
│  │  │ 💌 Kime: Ahmet                                  │    │   │
│  │  │ 📝 Mesaj: Seni çok özledim...                   │    │   │
│  │  │                                                  │    │   │
│  │  │ [✅ Onayla]  [❌ Reddet]                         │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Onaylandığında
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DİĞER SUNUCULAR                            │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │   Arkadaş Grubu      │    │   Okul Sunucusu      │          │
│  │   #mesajlar          │    │   #itiraflar         │          │
│  │                      │    │                      │          │
│  │  💌 Sevgili Ahmet,   │    │  💌 Sevgili Ayşe,    │          │
│  │  Seni çok özledim... │    │  Keşke konuşsaydık..│          │
│  └──────────────────────┘    └──────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

**Özet:**
- Tüm mesajlar **senin merkez sunucuna** düşer
- **Senin ekibin** onaylar veya reddeder
- Onaylanan mesajlar **ilgili sunucunun kanalında** görünür

---

## Kurulum

### Adım 1: Python Kur

1. https://www.python.org/downloads/ → İndir ve kur
2. **"Add Python to PATH"** kutusunu işaretle!

### Adım 2: Discord Bot Oluştur

1. https://discord.com/developers/applications → "New Application"
2. Sol menü → **Bot** → "Reset Token" → Kopyala
3. Aşağı kaydır:
   - **MESSAGE CONTENT INTENT** → AÇ
   - **SERVER MEMBERS INTENT** → AÇ
4. "Save Changes"

### Adım 3: Bot'u Sunuculara Ekle

1. Sol menü → **OAuth2** → **URL Generator**
2. SCOPES: `bot`, `applications.commands`
3. BOT PERMISSIONS: `Administrator`
4. URL'yi kopyala → Tarayıcıda aç → Sunucuları seç

### Adım 4: Merkez Sunucunu Ayarla

1. **Geliştirici Modu'nu aç:** Discord Ayarları → Gelişmiş → Geliştirici Modu
2. Merkez sunucunda bir **#onay-bekleyenler** kanalı oluştur
3. Bu kanala sağ tıkla → **"Kanal Kimliğini Kopyala"**
4. Bir **ekip rolü** oluştur (veya mevcut olanı kullan)
5. Role sağ tıkla → **"Rol Kimliğini Kopyala"**

### Adım 5: Bot Dosyalarını Ayarla

1. `.env.example` dosyasını kopyala → adını `.env` yap
2. `.env` dosyasını düzenle:

```env
DISCORD_TOKEN=bot_tokenin_buraya
APPROVAL_CHANNEL_ID=onay_kanali_id_buraya
TEAM_ROLE_ID=ekip_rolu_id_buraya
```

### Adım 6: Bot'u Çalıştır

Klasörde komut satırı aç:

```cmd
pip install -r requirements.txt
python bot.py
```

---

## Kullanım

### Merkez Sunucuda (Sen)

Mesajlar `#onay-bekleyenler` kanalına düşer:
- **✅ Onayla** → Mesaj ilgili sunucuya gönderilir
- **❌ Reddet** → Mesaj silinir

### Diğer Sunucularda (Yöneticiler)

Yönetici mesaj kanalını ayarlar:
```
!kanal #mesajlar
```

### Herkes

```
/mesaj          → Anonim mesaj gönderme formu açar
/isim Ahmet     → "Ahmet"e gönderilen mesajları arar
/isimler        → Tüm isimleri listeler
/istatistik     → İstatistikleri gösterir
```

---

## Komutlar

| Komut | Kim Kullanır | Ne Yapar |
|-------|--------------|----------|
| `!kanal #kanal` | Sunucu Yöneticisi | Mesaj kanalını ayarlar |
| `!yardim` | Herkes | Yardım mesajı gösterir |
| `/mesaj` | Herkes | Anonim mesaj gönderir |
| `/isim <isim>` | Herkes | İsme göre mesaj arar |
| `/isimler` | Herkes | Tüm isimleri listeler |
| `/istatistik` | Yönetici | İstatistikleri gösterir |

---

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

---

## Sorun Giderme

**Bot çalışmıyor:**
- `.env` dosyasındaki değerleri kontrol et
- Token doğru mu?
- Kanal ve rol ID'leri doğru mu?

**Mesajlar onay kanalına düşmüyor:**
- `APPROVAL_CHANNEL_ID` doğru mu?
- Bot o kanalda mesaj gönderme yetkisine sahip mi?

**Onaylanan mesajlar görünmüyor:**
- Hedef sunucuda `!kanal #kanal` çalıştırıldı mı?
- Bot o kanalda mesaj gönderme yetkisine sahip mi?

---

## Lisans

MIT
