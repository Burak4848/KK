# Bu dosyada uygulamadaki ana nesneleri yani sınıfları tanımladım.
# Kullanıcı bilgileri, yenilen öğünler ve yapılan sporlar burada tutuluyor.

from datetime import date, datetime


class Ogun:
    # Öğünlerin bilgisini tuttuğumuz sınıf

    def __init__(self, yemek_adi, kalori, protein=0, karbonhidrat=0, yag=0):
        # yemek bilgilerini kaydet
        self.yemek_adi = yemek_adi
        self.kalori = round(float(kalori), 1)
        self.protein = round(float(protein), 1)
        self.karbonhidrat = round(float(karbonhidrat), 1)
        self.yag = round(float(yag), 1)
        # ogunun eklenme saatini kaydet
        self.saat = datetime.now().strftime("%H:%M")

    def sozluge_donustur(self):
        # Json dosyasına kaydedebilmek için sözlüğe çevirmemiz gerekiyor

        sozluk = {
            "yemek_adi": self.yemek_adi,
            "kalori": self.kalori,
            "protein": self.protein,
            "karbonhidrat": self.karbonhidrat,
            "yag": self.yag,
            "saat": self.saat,
        }
        return sozluk

    @classmethod
    def sozlukten_olustur(cls, veri):
        # Json dosyasından okuduğumuz veriyi tekrar nesneye çeviriyoruz

        yemek_adi = veri.get("yemek_adi", "Bilinmeyen")
        kalori = veri.get("kalori", 0)
        protein = veri.get("protein", 0)
        karbonhidrat = veri.get("karbonhidrat", 0)
        yag = veri.get("yag", 0)

        ogun = cls(yemek_adi, kalori, protein, karbonhidrat, yag)
        # saati dosyadan oku, yoksa 00:00 yap
        ogun.saat = veri.get("saat", "00:00")
        return ogun


class Spor:
    # Yapılan egzersizleri tuttuğumuz sınıf


    def __init__(self, spor_adi, sure_dk, yakilan_kalori):
        # spor bilgilerini kaydet
        self.spor_adi = spor_adi
        self.sure_dk = round(float(sure_dk), 1)
        self.yakilan_kalori = round(float(yakilan_kalori), 1)
        # sporun eklenme saatini kaydet
        self.saat = datetime.now().strftime("%H:%M")

    def sozluge_donustur(self):
        # Spor nesnesini kaydetmek için sözlüğe çeviriyoruz

        sozluk = {
            "spor_adi": self.spor_adi,
            "sure_dk": self.sure_dk,
            "yakilan_kalori": self.yakilan_kalori,
            "saat": self.saat,
        }
        return sozluk

    @classmethod
    def sozlukten_olustur(cls, veri):
        # Dosyadan okunan veriyi nesneye çeviren fonksiyon

        spor_adi = veri.get("spor_adi", "Bilinmeyen")
        sure_dk = veri.get("sure_dk", 0)
        yakilan_kalori = veri.get("yakilan_kalori", 0)

        spor = cls(spor_adi, sure_dk, yakilan_kalori)
        # saati dosyadan oku, yoksa 00:00 yap
        spor.saat = veri.get("saat", "00:00")
        return spor


class GunlukKayit:
    # Bir gün içindeki tüm öğünleri ve sporları bu sınıfta topladım


    def __init__(self, tarih=None):
        # tarih verilmemisse bugunun tarihini al
        if tarih is not None:
            self.tarih = tarih
        else:
            self.tarih = date.today().isoformat()

        # ogunler listesini baslat
        self.ogunler = []

        # sporlar listesini baslat
        self.sporlar = []

    def ogun_ekle(self, ogun):
        # Yeni yenen yemeği listeye atıyor

        self.ogunler.append(ogun)

    def ogun_sil(self, index):
        # İstenmeyen yemeği siliyor

        try:
            self.ogunler.pop(index)
            return True
        except IndexError:
            return False

    def toplam_kalori(self):
        # O gün alınan toplam kaloriyi topluyor

        toplam = 0
        for ogun in self.ogunler:
            toplam = toplam + ogun.kalori
        return round(toplam, 1)

    def toplam_protein(self):
        """Gundeki tum ogunlerin toplam proteinini hesaplar."""
        toplam = 0
        for ogun in self.ogunler:
            toplam = toplam + ogun.protein
        return round(toplam, 1)

    def toplam_karbonhidrat(self):
        """Gundeki tum ogunlerin toplam karbonhidratini hesaplar."""
        toplam = 0
        for ogun in self.ogunler:
            toplam = toplam + ogun.karbonhidrat
        return round(toplam, 1)

    def toplam_yag(self):
        """Gundeki tum ogunlerin toplam yagini hesaplar."""
        toplam = 0
        for ogun in self.ogunler:
            toplam = toplam + ogun.yag
        return round(toplam, 1)

    def spor_ekle(self, spor):
        """Listeye yeni bir spor ekler."""
        self.sporlar.append(spor)

    def spor_sil(self, index):
        """Verilen indeksteki sporu siler. Basariliysa True doner."""
        try:
            self.sporlar.pop(index)
            return True
        except IndexError:
            return False

    def toplam_yakilan_kalori(self):
        """Gundeki tum sporlarin toplam yakilan kalorisini hesaplar."""
        toplam = 0
        for spor in self.sporlar:
            toplam = toplam + spor.yakilan_kalori
        return round(toplam, 1)

    def net_kalori(self):
        """Alinan kalori - yakilan kalori = net kalori."""
        return round(self.toplam_kalori() - self.toplam_yakilan_kalori(), 1)

    def sozluge_donustur(self):
        # Tüm günün kaydını kaydetmek için sözlüğe çevirir

        ogun_listesi = []
        for ogun in self.ogunler:
            ogun_listesi.append(ogun.sozluge_donustur())

        spor_listesi = []
        for spor in self.sporlar:
            spor_listesi.append(spor.sozluge_donustur())

        return {
            "tarih": self.tarih,
            "ogunler": ogun_listesi,
            "sporlar": spor_listesi,
        }

    @classmethod
    def sozlukten_olustur(cls, veri):
        # Dosyadan verileri okuyup günün kaydını oluşturur

        kayit = cls(tarih=veri.get("tarih"))
        ogunler_listesi = veri.get("ogunler", [])
        for ogun_verisi in ogunler_listesi:
            yeni_ogun = Ogun.sozlukten_olustur(ogun_verisi)
            kayit.ogun_ekle(yeni_ogun)
        sporlar_listesi = veri.get("sporlar", [])
        for spor_verisi in sporlar_listesi:
            yeni_spor = Spor.sozlukten_olustur(spor_verisi)
            kayit.spor_ekle(yeni_spor)
        return kayit


class Kullanici:
    # Kullanıcı bilgileri sınıfı


    def __init__(self, ad, yas, kilo, boy, cinsiyet="erkek", aktivite_seviyesi="orta"):
        self.ad = ad
        self.yas = int(yas)
        self.kilo = float(kilo)
        self.boy = float(boy)
        self.cinsiyet = cinsiyet.lower()
        self.aktivite_seviyesi = aktivite_seviyesi.lower()
        # profil olusturulunca hedef kaloriyi hesapla
        self.hedef_kalori = self._hedef_kalori_hesapla()

    def _hedef_kalori_hesapla(self):
        # İnternetten bulduğum Mifflin-St Jeor formülü ile kaloriyi hesapladım

        if self.cinsiyet == "erkek":
            bmh = 10 * self.kilo + 6.25 * self.boy - 5 * self.yas + 5
        else:
            bmh = 10 * self.kilo + 6.25 * self.boy - 5 * self.yas - 161

        # Aktivite carpanlari
        carpanlar = {
            "hareketsiz": 1.2,
            "az": 1.375,
            "orta": 1.55,
            "cok": 1.725,
            "asiri": 1.9
        }
        carpan = carpanlar.get(self.aktivite_seviyesi, 1.55)

        gunluk_kalori = bmh * carpan
        return round(gunluk_kalori)

    def sozluge_donustur(self):
        """Kullanici bilgilerini sozluge donusturur."""
        bilgiler = {
            "ad": self.ad,
            "yas": self.yas,
            "kilo": self.kilo,
            "boy": self.boy,
            "cinsiyet": self.cinsiyet,
            "aktivite_seviyesi": self.aktivite_seviyesi,
            "hedef_kalori": self.hedef_kalori,
        }
        return bilgiler

    @classmethod
    def sozlukten_olustur(cls, veri):
        """Sozlukten Kullanici nesnesi olusturur."""
        kullanici = cls(
            ad=veri.get("ad", "Kullanıcı"),
            yas=veri.get("yas", 25),
            kilo=veri.get("kilo", 70),
            boy=veri.get("boy", 170),
            cinsiyet=veri.get("cinsiyet", "erkek"),
            aktivite_seviyesi=veri.get("aktivite_seviyesi", "orta"),
        )
        # dosyada kayitli hedef varsa onu kullan
        kullanici.hedef_kalori = veri.get("hedef_kalori", kullanici.hedef_kalori)
        return kullanici
