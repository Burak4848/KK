# Groq (Llama 3) Yapay Zeka bağlantısını burada yaptım.
# Yapay zeka bu kütüphane üzerinden yemeklerin kalorisini tahmin ediyor.

import json
import os
from models import Ogun, Spor

# Railwayden aldığımız şifreyi okuyoruz (Kolaylık olsun diye eski değişkenden de okuyabilir)
API_ANAHTARI = os.environ.get("GROQ_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def api_anahtari_var_mi():
    # Sistemde anahtar var mı diye bakıyoruz
    if API_ANAHTARI and len(API_ANAHTARI) > 0:
        return True
    else:
        return False

def yemek_analiz_et(yemek_adi):
    # Bu kısmı yazarken yapay zekadan yardım aldım
    # Yemeği sorup cevap alıyoruz
    if not yemek_adi or yemek_adi.strip() == "":
        return None, "Yemek adı boş olamaz."

    if not api_anahtari_var_mi():
        return None, "Yapay Zeka API anahtarı eksik."

    try:
        from groq import Groq
        
        # Groq istemcisini baslat
        client = Groq(api_key=API_ANAHTARI)

        istem = f"""Sen bir diyetisyen asistanısın. Aşağıdaki yemek/porsiyon için besin değerlerini tahmin et: "{yemek_adi}"
SADECE JSON formatında yanıt ver, başka hiçbir kelime ekleme:
{{"kalori": 100, "protein": 10, "karbonhidrat": 10, "yag": 10}}"""

        # API'ye istek gonder
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": istem}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        metin = chat_completion.choices[0].message.content.strip()
        veri = json.loads(metin)

        ogun = Ogun(
            yemek_adi=yemek_adi,
            kalori=veri.get("kalori", 0),
            protein=veri.get("protein", 0),
            karbonhidrat=veri.get("karbonhidrat", 0),
            yag=veri.get("yag", 0),
        )
        return ogun, "Yapay Zeka ile analiz edildi."

    except Exception as hata:
        return None, "Yapay Zeka API hatası: " + str(hata)

def spor_analiz_et(spor_adi):
    if not spor_adi or spor_adi.strip() == "":
        return None, "Spor adı boş olamaz."

    if not api_anahtari_var_mi():
        return None, "Yapay Zeka API anahtarı eksik."

    try:
        from groq import Groq
        
        # Groq istemcisini baslat
        client = Groq(api_key=API_ANAHTARI)

        istem = f"""Sen bir fitness uzmanısın. Aşağıdaki spor/egzersiz için ortalama bir kişinin yakacağı kaloriyi tahmin et: "{spor_adi}"
SADECE JSON formatında yanıt ver, başka hiçbir kelime ekleme:
{{"sure_dk": 30, "yakilan_kalori": 200}}"""

        # API'ye istek gonder
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": istem}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        metin = chat_completion.choices[0].message.content.strip()
        veri = json.loads(metin)

        spor = Spor(
            spor_adi=spor_adi,
            sure_dk=veri.get("sure_dk", 30),
            yakilan_kalori=veri.get("yakilan_kalori", 0),
        )
        return spor, "Yapay Zeka ile analiz edildi."

    except Exception as hata:
        return None, "Yapay Zeka API hatası: " + str(hata)
