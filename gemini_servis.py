# Google Gemini Yapay Zeka bağlantısını burada yaptım.
# Yapay zeka bu kütüphane üzerinden yemeklerin kalorisini tahmin ediyor.

import json
import os

from models import Ogun, Spor

# Railwayden aldığımız şifreyi okuyoruz
API_ANAHTARI = os.environ.get("GEMINI_API_KEY", "")


def api_anahtari_var_mi():
    # Sistemde anahtar var mı diye bakıyoruz
    if API_ANAHTARI and len(API_ANAHTARI) > 0:
        return True
    else:
        return False


def yemek_analiz_et(yemek_adi):
    # Bu kısmı yazarken yapay zekadan yardım aldım
    # Yemeği sorup cevap alıyoruz
    # bos girdi kontrolu
    if not yemek_adi or yemek_adi.strip() == "":
        return None, "Yemek adı boş olamaz."

    # API anahtari kontrolu
    if not api_anahtari_var_mi():
        return None, "GEMINI_API_KEY tanımlı değil. Ortam değişkenini ayarlayın."

    try:
        # kutuphaneyi import et
        import google.generativeai as genai

        # API'yi yapilandir
        genai.configure(api_key=API_ANAHTARI)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Gemini'ye gonderilecek prompt
        istem = """Sen bir diyetisyen asistanısın. Aşağıdaki yemek/porsiyon için
besin değerlerini tahmin et: "{}"

SADECE şu JSON formatında yanıt ver, başka hiçbir açıklama ekleme:
{{"kalori": <sayı>, "protein": <gram>, "karbonhidrat": <gram>, "yag": <gram>}}""".format(yemek_adi)

        # API'ye istek gonder
        yanit = model.generate_content(istem)
        metin = yanit.text.strip()

        # ```json ... ``` kod blogunu temizle
        if metin.startswith("```"):
            metin = metin.strip("`")
            if metin.lower().startswith("json"):
                metin = metin[4:]
        metin = metin.strip()

        # JSON'u parse et
        veri = json.loads(metin)

        # Ogun nesnesi olustur
        ogun = Ogun(
            yemek_adi=yemek_adi,
            kalori=veri.get("kalori", 0),
            protein=veri.get("protein", 0),
            karbonhidrat=veri.get("karbonhidrat", 0),
            yag=veri.get("yag", 0),
        )
        return ogun, "Gemini AI ile analiz edildi."

    except ImportError:
        return None, "google-generativeai kütüphanesi kurulu değil. 'pip install google-generativeai' çalıştırın."
    except json.JSONDecodeError:
        return None, "Gemini yanıtı işlenemedi (geçersiz format)."
    except Exception as hata:
        return None, "Gemini API hatası: " + str(hata)


def spor_analiz_et(spor_adi):
    """
    Gemini API'ye spor/egzersiz bilgisini gonderir, yakilan kalori tahmini alir.
    Geriye (Spor nesnesi, mesaj) veya (None, hata mesaji) doner.
    """
    # bos girdi kontrolu
    if not spor_adi or spor_adi.strip() == "":
        return None, "Spor adı boş olamaz."

    # API anahtari kontrolu
    if not api_anahtari_var_mi():
        return None, "GEMINI_API_KEY tanımlı değil. Ortam değişkenini ayarlayın."

    try:
        # kutuphaneyi import et
        import google.generativeai as genai

        # API'yi yapilandir
        genai.configure(api_key=API_ANAHTARI)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Gemini'ye gonderilecek prompt
        istem = """Sen bir fitness uzmanı asistanısın. Aşağıdaki spor/egzersiz aktivitesi için
ortalama bir kişinin yakacağı kaloriyi tahmin et: "{}"

SADECE şu JSON formatında yanıt ver, başka hiçbir açıklama ekleme:
{{"sure_dk": <dakika>, "yakilan_kalori": <sayı>}}""".format(spor_adi)

        # API'ye istek gonder
        yanit = model.generate_content(istem)
        metin = yanit.text.strip()

        # ```json ... ``` kod blogunu temizle
        if metin.startswith("```"):
            metin = metin.strip("`")
            if metin.lower().startswith("json"):
                metin = metin[4:]
        metin = metin.strip()

        # JSON'u parse et
        veri = json.loads(metin)

        # Spor nesnesi olustur
        spor = Spor(
            spor_adi=spor_adi,
            sure_dk=veri.get("sure_dk", 30),
            yakilan_kalori=veri.get("yakilan_kalori", 0),
        )
        return spor, "Gemini AI ile analiz edildi."

    except ImportError:
        return None, "google-generativeai kütüphanesi kurulu değil. 'pip install google-generativeai' çalıştırın."
    except json.JSONDecodeError:
        return None, "Gemini yanıtı işlenemedi (geçersiz format)."
    except Exception as hata:
        return None, "Gemini API hatası: " + str(hata)

