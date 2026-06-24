# app.py - Kaç Kalori Projesi Ana Dosyası
# Bu dosyayı yapay zekadan yardım alarak yazdım.
# Web sitemiz buradan çalışıyor. Bütün sayfaları burada bağladım.

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from models import Kullanici, Ogun, Spor
import veri_yonetimi as vy
import gemini_servis as gemini

# Flask uygulamasini olustur
app = Flask(__name__)
app.secret_key = "kac-kalori-final-projesi-2025"  # flash mesajlari icin gerekli


@app.route("/")
def anasayfa():
    """Tanitim sayfasi. Uygulamanin ne yaptigini anlatan landing page."""
    return render_template("index.html")


@app.route("/app")
def uygulama():
    """Uygulama sayfasi. Profil yoksa kurulum ekrani, varsa dashboard gosterir."""
    kullanici = vy.kullanici_yukle()

    # kullanici profili yoksa kurulum ekranini goster
    if kullanici is None:
        return render_template("yansayfa.html", kullanici=None)

    # bugunun kayitlarini yukle
    kayitlar = vy.kayitlari_yukle()
    bugun = vy.bugunun_kaydini_al(kayitlar)

    # yuzde hesapla (hedefe ne kadar ulasti)
    yuzde = 0
    if kullanici.hedef_kalori > 0:
        yuzde = round((bugun.toplam_kalori() / kullanici.hedef_kalori) * 100)

    # haftalik veriyi hesapla
    haftalik = vy.son_n_gun(kayitlar, 7)

    # haftalik grafigin maksimum degerini bul
    en_yuksek = kullanici.hedef_kalori
    for gun in haftalik:
        if gun["kalori"] > en_yuksek:
            en_yuksek = gun["kalori"]
    if en_yuksek == 0:
        en_yuksek = 1  # sifira bolme hatasini onle
    haftalik_max = en_yuksek

    return render_template(
        "yansayfa.html",
        kullanici=kullanici,
        bugun=bugun,
        yuzde=yuzde,
        haftalik=haftalik,
        haftalik_max=haftalik_max,
        gemini_aktif=gemini.api_anahtari_var_mi(),
    )


@app.route("/profil-kaydet", methods=["POST"])
def profil_kaydet():
    """Formdan gelen bilgilerle kullanici profili olusturur veya gunceller."""
    try:
        # form verilerini al
        ad = request.form.get("ad", "").strip()
        if ad == "":
            ad = "Kullanıcı"

        yas = int(request.form.get("yas", 25))
        kilo = float(request.form.get("kilo", 70))
        boy = float(request.form.get("boy", 170))
        cinsiyet = request.form.get("cinsiyet", "erkek")
        aktivite_seviyesi = request.form.get("aktivite_seviyesi", "orta")

        # negatif veya sifir deger kontrolu
        if yas <= 0 or kilo <= 0 or boy <= 0:
            flash("Yaş, kilo ve boy pozitif olmalıdır.", "hata")
            return redirect(url_for("uygulama"))

        # kullanici nesnesi olustur ve kaydet
        kullanici = Kullanici(ad, yas, kilo, boy, cinsiyet, aktivite_seviyesi)
        kaydedildi = vy.kullanici_kaydet(kullanici)
        if kaydedildi:
            flash("Hoş geldin, " + ad + "! Günlük hedefin " + str(kullanici.hedef_kalori) + " kcal.", "basarili")
        else:
            flash("Profil kaydedilemedi. Lütfen tekrar deneyin.", "hata")

    except ValueError:
        flash("Yaş, kilo ve boy için geçerli sayılar girin.", "hata")

    return redirect(url_for("uygulama"))


@app.route("/ogun-ekle-ai", methods=["POST"])
def ogun_ekle_ai():
    """Gemini AI ile yemek adından ogun ekler."""
    yemek_adi = request.form.get("yemek_adi", "").strip()

    if yemek_adi == "":
        flash("Yemek adı boş olamaz.", "hata")
        return redirect(url_for("uygulama"))

    # Gemini'ye sor
    ogun, mesaj = gemini.yemek_analiz_et(yemek_adi)

    if ogun is None:
        return jsonify({"basarili": False, "hata": "AI analizi başarısız: " + mesaj})

    # Frontend'e onay penceresi icin geri dondur
    return jsonify({
        "basarili": True,
        "yemek_adi": ogun.yemek_adi,
        "kalori": round(ogun.kalori, 1),
        "protein": round(ogun.protein, 1),
        "karbonhidrat": round(ogun.karbonhidrat, 1),
        "yag": round(ogun.yag, 1),
        "mesaj": mesaj
    })


@app.route("/ogun-ekle-manuel", methods=["POST"])
def ogun_ekle_manuel():
    """Kullanicinin elle girdigi degerlerle ogun ekler."""
    try:
        # form verilerini al
        yemek_adi = request.form.get("yemek_adi", "").strip()
        if yemek_adi == "":
            yemek_adi = "Öğün"

        kalori = float(request.form.get("kalori", 0))
        protein = float(request.form.get("protein", 0) or 0)
        karbonhidrat = float(request.form.get("karbonhidrat", 0) or 0)
        yag = float(request.form.get("yag", 0) or 0)

        # negatif deger kontrolu
        if kalori < 0 or protein < 0 or karbonhidrat < 0 or yag < 0:
            flash("Değerler negatif olamaz.", "hata")
            return redirect(url_for("uygulama"))

        # ogun nesnesi olustur
        ogun = Ogun(yemek_adi, kalori, protein, karbonhidrat, yag)

        # kaydet
        kayitlar = vy.kayitlari_yukle()
        bugun = vy.bugunun_kaydini_al(kayitlar)
        bugun.ogun_ekle(ogun)
        vy.kayitlari_kaydet(kayitlar)

        flash(yemek_adi + " eklendi — " + str(round(ogun.kalori)) + " kcal", "basarili")

    except ValueError:
        flash("Kalori ve makrolar için geçerli sayılar girin.", "hata")

    return redirect(url_for("uygulama"))


@app.route("/ogun-sil/<int:index>")
def ogun_sil(index):
    """Bugunun ogun listesinden belirtilen indeksteki ogunu siler."""
    kayitlar = vy.kayitlari_yukle()
    bugun = vy.bugunun_kaydini_al(kayitlar)

    silindi_mi = bugun.ogun_sil(index)
    if silindi_mi:
        vy.kayitlari_kaydet(kayitlar)
        flash("Öğün silindi.", "basarili")
    else:
        flash("Öğün bulunamadı.", "hata")

    return redirect(url_for("uygulama"))


@app.route("/spor-ekle-ai", methods=["POST"])
def spor_ekle_ai():
    """Gemini AI ile spor adından spor ekler."""
    spor_adi = request.form.get("spor_adi", "").strip()

    if spor_adi == "":
        flash("Spor adı boş olamaz.", "hata")
        return redirect(url_for("uygulama"))

    # Gemini'ye sor
    spor, mesaj = gemini.spor_analiz_et(spor_adi)

    if spor is None:
        return jsonify({"basarili": False, "hata": "AI analizi başarısız: " + mesaj})

    # Frontend'e onay penceresi icin geri dondur
    return jsonify({
        "basarili": True,
        "spor_adi": spor.spor_adi,
        "sure_dk": spor.sure_dk,
        "yakilan_kalori": round(spor.yakilan_kalori, 1),
        "mesaj": mesaj
    })


@app.route("/spor-ekle-manuel", methods=["POST"])
def spor_ekle_manuel():
    """Kullanicinin elle girdigi degerlerle spor ekler."""
    try:
        # form verilerini al
        spor_adi = request.form.get("spor_adi", "").strip()
        if spor_adi == "":
            spor_adi = "Egzersiz"

        sure_dk = float(request.form.get("sure_dk", 0))
        yakilan_kalori = float(request.form.get("yakilan_kalori", 0))

        # negatif deger kontrolu
        if sure_dk < 0 or yakilan_kalori < 0:
            flash("Değerler negatif olamaz.", "hata")
            return redirect(url_for("uygulama"))

        # spor nesnesi olustur
        spor = Spor(spor_adi, sure_dk, yakilan_kalori)

        # kaydet
        kayitlar = vy.kayitlari_yukle()
        bugun = vy.bugunun_kaydini_al(kayitlar)
        bugun.spor_ekle(spor)
        vy.kayitlari_kaydet(kayitlar)

        flash("🏃 " + spor_adi + " eklendi — " + str(round(spor.yakilan_kalori)) + " kcal yakıldı", "basarili")

    except ValueError:
        flash("Süre ve kalori için geçerli sayılar girin.", "hata")

    return redirect(url_for("uygulama"))


@app.route("/spor-sil/<int:index>")
def spor_sil(index):
    """Bugunun spor listesinden belirtilen indeksteki sporu siler."""
    kayitlar = vy.kayitlari_yukle()
    bugun = vy.bugunun_kaydini_al(kayitlar)

    silindi_mi = bugun.spor_sil(index)
    if silindi_mi:
        vy.kayitlari_kaydet(kayitlar)
        flash("Spor silindi.", "basarili")
    else:
        flash("Spor bulunamadı.", "hata")

    return redirect(url_for("uygulama"))


# programi calistir
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
