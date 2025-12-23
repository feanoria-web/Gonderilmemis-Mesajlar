import json
import random
from datetime import datetime, timedelta

# Türk isimleri
TURKISH_NAMES = [
    "Ahmet", "Mehmet", "Mustafa", "Ali", "Hüseyin", "Hasan", "İbrahim", "Osman", "Yusuf", "Murat",
    "Emre", "Burak", "Cem", "Deniz", "Efe", "Kaan", "Berk", "Arda", "Yiğit", "Kerem",
    "Oğuz", "Serkan", "Tolga", "Volkan", "Onur", "Uğur", "Barış", "Caner", "Erdem", "Furkan",
    "Gökhan", "Halil", "İlker", "Kadir", "Levent", "Mert", "Necati", "Orhan", "Polat", "Recep",
    "Selim", "Taner", "Umut", "Vedat", "Yavuz", "Zafer", "Alp", "Batuhan", "Çağrı", "Doruk",
    "Ayşe", "Fatma", "Zeynep", "Elif", "Merve", "Büşra", "Esra", "Selin", "Derya", "Gamze",
    "Hande", "İrem", "Cansu", "Burcu", "Pınar", "Gizem", "Tuğba", "Özge", "Seda", "Yasemin",
    "Aslı", "Başak", "Ceren", "Damla", "Ece", "Fulya", "Gül", "Hilal", "Işıl", "Jale",
    "Kardelen", "Lale", "Mine", "Naz", "Özlem", "Pembe", "Rana", "Sibel", "Tuba", "Ümit",
    "Vildan", "Yeliz", "Zehra", "Aylin", "Banu", "Defne", "Ebru", "Funda", "Gökçe", "Hayal"
]

# Mesaj şablonları
MESSAGE_TEMPLATES = [
    "Seni çok özledim...",
    "Keşke o gün farklı davransaydım.",
    "Hala aklımdasın, bunu bilmeni istedim.",
    "Seninle geçirdiğim zamanlar çok güzeldi.",
    "Sana söyleyemediklerim var, hala içimde.",
    "O gülüşünü asla unutamıyorum.",
    "Keşke bir şans daha olsaydı.",
    "Seni görmek için bahaneler arıyordum.",
    "Her şarkıda seni hatırlıyorum.",
    "Seninle tanışmak hayatımın en güzel anıydı.",
    "Keşke cesaretim olsaydı sana söylemeye.",
    "Seni kaybetmek en büyük hatalarımdan biriydi.",
    "Hala o mesajları okuyorum bazen.",
    "Seninle kahve içmek isterdim bir kez daha.",
    "O bakışlarını unutamıyorum.",
    "Keşke zamanı geri alabilseydim.",
    "Sana kırgınım ama hala seviyorum.",
    "Her yerde seni arıyorum.",
    "Seninle olan anılarımız çok kıymetli.",
    "Keşke daha çok vakit geçirseydik.",
    "Seni düşünmeden bir gün geçmiyor.",
    "O gece söylediklerin hala aklımda.",
    "Seninle dans etmek isterdim.",
    "Keşke mesajlarıma cevap verseydin.",
    "Seni beklemekten yoruldum ama hala bekliyorum.",
    "Her şey için teşekkürler.",
    "Seni affettim, bunu bilmeni istedim.",
    "Keşke yanımda olsaydın şu an.",
    "Seninle yürüdüğümüz sokakları özledim.",
    "İyi ki tanımışım seni.",
    "Sana sarılmak isterdim bir kez daha.",
    "Keşke her şey farklı olsaydı.",
    "Seni görünce kalbim hala hızlanıyor.",
    "Aklımdan çıkmıyorsun...",
    "Seninle güldüğümüz anları özledim.",
    "Keşke konuşabilseydik yüz yüze.",
    "Sana yazdığım mektupları hiç gönderemedim.",
    "Her yağmurda seni düşünüyorum.",
    "Seninle geçen yaz çok güzeldi.",
    "Keşke bir daha görüşebilsek.",
]

def generate_test_data():
    """Generate random test messages."""
    messages = {
        "pending": [],
        "approved": [],
        "rejected": []
    }

    # Her isim için 0-20 arası random mesaj
    for name in TURKISH_NAMES:
        num_messages = random.randint(0, 20)

        for _ in range(num_messages):
            # Random tarih (son 30 gün içinde)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

            message_entry = {
                "id": f"test_{timestamp.strftime('%Y%m%d%H%M%S%f')}_{random.randint(1000, 9999)}",
                "recipient": name,
                "content": random.choice(MESSAGE_TEMPLATES),
                "submitted_at": timestamp.isoformat(),
                "submitted_by": random.randint(100000000000000000, 999999999999999999),
                "approved_at": timestamp.isoformat(),
                "approved_by": random.randint(100000000000000000, 999999999999999999),
                "guild_id": random.randint(100000000000000000, 999999999999999999),
                "guild_name": "Test Sunucusu"
            }

            messages["approved"].append(message_entry)

    return messages

if __name__ == "__main__":
    data = generate_test_data()

    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_messages = len(data["approved"])
    unique_names = len(set(msg["recipient"] for msg in data["approved"]))

    print(f"✅ Test verisi oluşturuldu!")
    print(f"📊 Toplam mesaj: {total_messages}")
    print(f"👤 İsim sayısı: {unique_names}")
    print(f"📁 Dosya: messages.json")
