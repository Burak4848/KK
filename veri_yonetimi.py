# Json dosyalarıyla veri kaydetme işlemleri. Program kapanıp açıldığında veriler gitmesin diye.

import json
import os
from datetime import date, timedelta

from models import Kullanici, GunlukKayit


# dosya yollarini tanimla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERI_KLASORU = os.path.join(BASE_DIR, "veri")
KULLANICI_DOSYASI = os.path.join(VERI_KLASORU, "kullanici.json")
KAYITLAR_DOSYASI = os.path.join(VERI_KLASORU, "kayitlar.json")


def _klasor_olustur():
    # Veri klasörü yoksa kod hata veriyordu, o yüzden böyle bir fonksiyon yazdım
    if not os.path.exists(VERI_KLASORU):
        os.makedirs(VERI_KLASORU)


# ---- KULLANICI PROFILI ----

def kullanici_kaydet(kullanici):
    # Profili JSON dosyasına kaydediyoruz
    try:
        _klasor_olustur()
        dosya = open(KULLANICI_DOSYASI, "w", encoding="utf-8")
        json.dump(kullanici.sozluge_donustur(), dosya, ensure_ascii=False, indent=2)
        dosya.close()
        return True
    except (OSError, PermissionError) as hata:
        print("[HATA] Profil kaydedilemedi:", hata)
        return False


def kullanici_yukle():
    # Uygulama açılınca dosyadan veriyi okumak için
    try:
        dosya = open(KULLANICI_DOSYASI, "r", encoding="utf-8")
        veri = json.load(dosya)
        dosya.close()
        kullanici = Kullanici.sozlukten_olustur(veri)
        return kullanici
    except FileNotFoundError:
        # dosya henuz olusturulmamis, normal durum
        return None
    except (json.JSONDecodeError, KeyError, ValueError) as hata:
        print("[HATA] Profil okunamadi:", hata)
        return None


# ---- GUNLUK KAYITLAR ----

def kayitlari_yukle():
    # Bütün günlük yenen yemekleri ve sporları yüklüyoruz
    try:
        dosya = open(KAYITLAR_DOSYASI, "r", encoding="utf-8")
        ham_veri = json.load(dosya)
        dosya.close()

        # ham veriyi GunlukKayit nesnelerine donustur
        kayitlar = {}
        for tarih, kayit_veri in ham_veri.items():
            kayitlar[tarih] = GunlukKayit.sozlukten_olustur(kayit_veri)
        return kayitlar

    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, KeyError, ValueError) as hata:
        print("[HATA] Kayitlar okunamadi:", hata)
        return {}


def kayitlari_kaydet(kayitlar):
    # Günü bitirince verileri kaydettiğimiz yer
    try:
        _klasor_olustur()

        # GunlukKayit nesnelerini sozluklere donustur
        ham_veri = {}
        for tarih, kayit in kayitlar.items():
            ham_veri[tarih] = kayit.sozluge_donustur()

        dosya = open(KAYITLAR_DOSYASI, "w", encoding="utf-8")
        json.dump(ham_veri, dosya, ensure_ascii=False, indent=2)
        dosya.close()
        return True

    except (OSError, PermissionError) as hata:
        print("[HATA] Kayitlar kaydedilemedi:", hata)
        return False


def bugunun_kaydini_al(kayitlar):
    """Bugunun GunlukKayit nesnesini doner. Yoksa yenisini olusturur."""
    bugun = date.today().isoformat()
    if bugun not in kayitlar:
        kayitlar[bugun] = GunlukKayit(tarih=bugun)
    return kayitlar[bugun]


def son_n_gun(kayitlar, n=7):
    """
    Son n gune ait ozet bilgileri liste olarak doner.
    Her eleman: {"tarih": str, "kalori": float, "gun_adi": str}
    """
    gun_adlari = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    bugun = date.today()
    sonuc = []

    for i in range(n - 1, -1, -1):
        gun = bugun - timedelta(days=i)
        tarih_str = gun.isoformat()

        # o gune ait kayit var mi kontrol et
        if tarih_str in kayitlar:
            kalori = kayitlar[tarih_str].toplam_kalori()
        else:
            kalori = 0

        # gun adini belirle
        if i == 0:
            gun_adi = "Bugün"
        else:
            gun_adi = gun_adlari[gun.weekday()]

        sonuc.append({
            "tarih": tarih_str,
            "kalori": kalori,
            "gun_adi": gun_adi,
        })

    return sonuc
