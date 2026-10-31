import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sayfa Yapılandırması
st.set_page_config(page_title="Castrol Form Stok & CRM Paneli", layout="wide")

st.title("🚛 Castrol Form Filtre - Görsel, Stok ve Araç Bilgili B2B Paneli")
st.markdown("Stoku biten ürünler listeden otomatik kaldırılır, araç ve cross referans bilgileri anında görüntülenir.")

# Dosya Yolları
URUN_DOSYASI = "urunler_stok.csv"
CRM_DOSYASI = "musteri_teklifleri.csv"

# 1. Ürün Veritabanı (Senin gönderdiğin güncel tablo yapısı ve resim sütunu ile)
if not os.path.exists(URUN_DOSYASI):
    df_ilk_urunler = pd.DataFrame([
        {
            "Kod": "31-356", 
            "Parça Adı": "Yağ Filtresi", 
            "Marka / Model": "Heavy Duty / Universal", 
            "Cross 1": "Mann W950/26", 
            "Cross 2": "Fleetguard LF16015", 
            "Liste Fiyatı": 1200.0, 
            "Stok": 50,
            "Resim": "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=300&q=80" # Örnek / Yüklenen ürün görseli temeli
        },
        {
            "Kod": "32-393", 
            "Parça Adı": "Hava Filtresi (Dış)", 
            "Marka / Model": "Volvo / Renault Kamyon", 
            "Cross 1": "Mann C30850", 
            "Cross 2": "Donaldson P777638", 
            "Liste Fiyatı": 2500.0, 
            "Stok": 30,
            "Resim": ""
        },
        {
            "Kod": "50-501", 
            "Parça Adı": "Hava Filtresi (İç)", 
            "Marka / Model": "Volvo / Renault Kamyon", 
            "Cross 1": "Mann CF1630", 
            "Cross 2": "Donaldson P777639", 
            "Liste Fiyatı": 1800.0, 
            "Stok": 40,
            "Resim": ""
        },
        {
            "Kod": "4092-945", 
            "Parça Adı": "Yakıt / Su Ayırıcı", 
            "Marka / Model": "Mercedes Axor / Actros", 
            "Cross 1": "Parker R120P", 
            "Cross 2": "Baldwin BF7633", 
            "Liste Fiyatı": 1500.0, 
            "Stok": 25,
            "Resim": ""
        },
        {
            "Kod": "70-716", 
            "Parça Adı": "Şanzıman Filtresi", 
            "Marka / Model": "ZF Şanzıman Serisi", 
            "Cross 1": "Mann H601", 
            "Cross 2": "Mahle HX12", 
            "Liste Fiyatı": 2200.0, 
            "Stok": 15,
            "Resim": ""
        }
    ])
    df_ilk_urunler.to_csv(URUN_DOSYASI, index=False)

# 2. CRM Teklif ve Sipariş Dosyası
if not os.path.exists(CRM_DOSYASI):
    df_empty_crm = pd.DataFrame(columns=[
        "Tarih", "Firma Adı", "Yetkili", "Telefon", "İl", "İlçe", "Açık Adres",
        "Toplam Liste", "Toptancı Maliyeti", "Komisyon", "Satın Alınan Ürünler", "Notlar"
    ])
    df_empty_crm.to_csv(CRM_DOSYASI, index=False)

# Güncel ürünleri yükle
df_urunler = pd.read_csv(URUN_DOSYASI)

# E-posta Gönderme Fonksiyonu (evrimileri0@gmail.com adresine sabitlendi)
def siparis_maili_gonder(MailIcerigi):
    gonderen_email = "evrimileri0@gmail.com"
    gonderen_sifre = "BURAYA_GMAIL_UYGULAMA_SIFRENIZI_YAZIN"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = gonderen_email
        msg['To'] = "evrimileri0@gmail.com"
        msg['Subject'] = "🚛 Yeni Castrol Form Siparişi / Rezervasyonu!"
        
        msg.attach(MIMEText(MailIcerigi, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gonderen_email, gonderen_sifre)
        server.sendmail(gonderen_email, "evrimileri0@gmail.com", msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# Yan Menü: Müşteri ve Adres Bilgileri
st.sidebar.header("👤 Müşteri & Lokasyon Bilgileri")
firma_adi = st.sidebar.text_input("Şirket / Firma Adı", placeholder="Örn: Özkanlar Ağır Vasıta Ltd.")
yetkili_adi = st.sidebar.text_input("Yetkili Adı Soyadı", placeholder="Örn: Ahmet Bey")
telefon = st.sidebar.text_input("Telefon Numarası", placeholder="0532...")

il = st.sidebar.selectbox("İl", ["İstanbul", "Ankara", "İzmir", "Bursa", "Konya", "Kocaeli", "Adana", "Diğer"])
ilce = st.sidebar.text_input("İlçe", placeholder="Örn: İkitelli / Başakşehir")
acik_adres = st.sidebar.text_area("Detaylı Açık Adres", placeholder="Sanayi Sitesi, Blok No, Dükkan No...")

musteri_notu = st.sidebar.text_area("Sipariş / Sevkiyat Notu", placeholder="Acil sevkiyat olacak.")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Ticari Parametreler")
toptanci_iskonto_orani = st.sidebar.slider("Toptancı İskontosu (%)", min_value=10, max_value=50, value=30, step=5)
benim_komisyon_orani = st.sidebar.slider("Komisyon Oranım (%)", min_value=1, max_value=15, value=5, step=1)

# Ana Ekran: Ürün Kataloğu (Stoku Bitenler Listeden Kaldırılır)
st.subheader("📦 Ürün Kataloğu ve Stok Seçimi")

sepet_verileri = []
guncellenmis_urunler = df_urunler.copy()

# Stok > 0 olan ürünleri filtrele (Stoku bitenler otomatik listeden kalkar)
aktif_urunler = guncellenmis_urunler[guncellenmis_urunler['Stok'] > 0]

if aktif_urunler.empty:
    st.warning("⚠️ Şu anda stokta aktif ürün bulunmamaktadır.")
else:
    for index, row in aktif_urunler.iterrows():
        # Kolonlar halinde görsel ve detayları gösterelim
        col_img, col_detay = st.columns([1, 4])
        
        with col_img:
            # Eğer ürünün görsel linki varsa göster, yoksa varsayılan ikon/yazı göster
            if pd.notna(row['Resim']) and str(row['Resim']).startswith("http"):
                st.image(row['Resim'], width=100)
            else:
                st.info("📦 Görsel Yok")
                
        with col_detay:
            st.markdown(f"### Kod: `{row['Kod']}` - {row['Parça Adı']}")
            st.markdown(f"🚗 **Araç Bilgisi (Marka / Model):** *{row['Marka / Model']}*")
            st.caption(f"🔄 **Cross 1:** {row['Cross 1']} | **Cross 2:** {row['Cross 2']} | 💰 **Liste Fiyatı:** {row['Liste Fiyatı']:,.2f} TL | 📦 **Kalan Stok:** {row['Stok']} adet")
            
            secilen_adet = st.number_input(f"Adet Al ({row['Kod']})", min_value=0, max_value=int(row['Stok']), value=0, step=1, key=str(row['Kod']))
            
            if secilen_adet > 0:
                toplam_tutar = secilen_adet * row['Liste Fiyatı']
                sepet_verileri.append({
                    "Kod": row['Kod'],
                    "Parça Adı": row['Parça Adı'],
                    "Birim Fiyat": row['Liste Fiyatı'],
                    "Adet": secilen_adet,
                    "Toplam Liste": toplam_tutar
                })
                # Orijinal dataframe üzerindeki stoku düş
                orijinal_index = guncellenmis_urunler[guncellenmis_urunler['Kod'] == row['Kod']].index[0]
                guncellenmis_urunler.loc[orijinal_index, 'Stok'] = row['Stok'] - secilen_adet

        st.markdown("---")

# Hesaplama ve Sipariş Tamamlama Alanı
if len(sepet_verileri) > 0:
    df_sepet = pd.DataFrame(sepet_verileri)
    
    toplam_liste_tutar = df_sepet["Toplam Liste"].sum()
    toptanci_maliyeti = toplam_liste_tutar * (1 - toptanci_iskonto_orani / 100)
    komisyonum = toptanci_maliyeti * (benim_komisyon_orani / 100)
    
    st.subheader("📊 Teklif Özeti ve Kazanç Tablosu")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Toplam Liste", f"{toplam_liste_tutar:,.2f} TL")
    col_b.metric(f"Toptancı Ödeyeceği (%{toptanci_iskonto_orani})", f"{toptanci_maliyeti:,.2f} TL")
    col_c.metric(f"Komisyonun (%{benim_komisyon_orani})", f"{komisyonum:,.2f} TL", delta="Net Kazanç")
    col_d.metric("Toptancı Kârı", f"{(toplam_liste_tutar - toptanci_maliyeti):,.2f} TL")
    
    with st.expander("Seçilen Ürünlerin Listesi"):
        st.dataframe(df_sepet)
    
    st.markdown("### 💾 Siparişi Onayla, Stoğu Düş ve Mail Gönder")
    st.info("💡 Sipariş onaylandığında detaylar otomatik olarak **evrimileri0@gmail.com** adresine gönderilecektir.")
    
    if st.button("Siparişi Tamamla ve Kaydet"):
        if not firma_adi:
            st.error("Lütfen sol menüden Firma / Şirket Adı giriniz!")
        else:
            # 1. Stokları güncelle (Stoku bitenler otomatik gizlenecek)
            guncellenmis_urunler.to_csv(URUN_DOSYASI, index=False)
            
            # 2. Ürün özet metni
            urun_ozeti = ", ".join([f"{row['Adet']}x {row['Parça Adı']} ({row['Kod']})" for index, row in df_sepet.iterrows()])
            
            yeni_kayit = {
                "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Firma Adı": firma_adi,
                "Yetkili": yetkili_adi,
                "Telefon": telefon,
                "İl": il,
                "İlçe": ilce,
                "Açık Adres": acik_adres,
                "Toplam Liste": toplam_liste_tutar,
                "Toptancı Maliyeti": toptanci_maliyeti,
                "Komisyon": komisyonum,
                "Satın Alınan Ürünler": urun_ozeti,
                "Notlar": musteri_notu
            }
            
            # 3. CRM Kayıtlarına ekle
            df_crm = pd.read_csv(CRM_DOSYASI)
            df_crm_yeni = pd.concat([df_crm, pd.DataFrame([yeni_kayit])], ignore_index=False)
            df_crm_yeni.to_csv(CRM_DOSYASI, index=False)
            
            # 4. E-posta Gönderme İşlemi
            mail_metni = f"""Yeni Bir Castrol Form Siparişi / Rezervasyonu Alındı!

Firma Adı: {firma_adi}
Yetkili: {yetkili_adi}
Telefon: {telefon}
Adres: {il} / {ilce} - {acik_adres}

--- SİPARİŞ DETAYLARI ---
{urun_ozeti}

Toplam Liste Tutarı: {toplam_liste_tutar:,.2f} TL
Toptancı Maliyeti: {toptanci_maliyeti:,.2f} TL
Tahmini Komisyonunuz: {komisyonum:,.2f} TL

Müşteri Notu: {musteri_notu}
Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
            mail_sonuc = siparis_maili_gonder(mail_metni)
            if mail_sonuc:
                st.success("✅ Sipariş başarıyla kaydedildi, stoktan düşüldü ve **evrimileri0@gmail.com** adresine mail gönderildi!")
            else:
                st.warning("⚠️ Sipariş ve stok kaydedildi fakat mail gönderilemedi. (Gmail uygulama şifrenizi kontrol edin).")
else:
    st.info("💡 Sipariş oluşturmak için yukarıdaki ürünlerden adet seçin.")

st.markdown("---")

# Geçmiş Müşteri Siparişleri Tablosu
st.subheader("📋 Geçmiş Müşteri Siparişleri ve Adres Arşivi")
if os.path.exists(CRM_DOSYASI):
    df_kayitlar = pd.read_csv(CRM_DOSYASI)
    if not df_kayitlar.empty:
        st.dataframe(df_kayitlar, use_container_width=True)
    else:
        st.write("Henüz kaydedilmiş sipariş bulunmuyor.")
