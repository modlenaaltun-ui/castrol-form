import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Castrol Form Stok & CRM Paneli", layout="wide")

st.title("🚛 Castrol Form Filtre - Stok, Cross Referans & B2B CRM Paneli")
st.markdown("Ürünlerin marka/model eşleşmelerini, cross kodlarını takip edebilir; teklif oluşturulduğunda stoktan otomatik düşebilirsiniz.")

# Dosya Yolları
URUN_DOSYASI = "urunler_stok.csv"
CRM_DOSYASI = "musteri_teklifleri.csv"

# 1. Ürün Veritabanı Yoksa İlk Halleriyle Oluştur (Marka/Model, Cross 1, Cross 2, Fiyat, Stok)
if not os.path.exists(URUN_DOSYASI):
    df_ilk_urunler = pd.DataFrame([
        {"Kod": "CF-1001", "Parça Adı": "Yağ Filtresi", "Marka / Model": "Heavy Duty / Universal", "Cross 1": "Mann W950/26", "Cross 2": "Fleetguard LF16015", "Liste Fiyatı": 1200.0, "Stok": 50},
        {"Kod": "CF-2005", "Parça Adı": "Hava Filtresi (Dış)", "Marka / Model": "Volvo / Renault Kamyon", "Cross 1": "Mann C30850", "Cross 2": "Donaldson P777638", "Liste Fiyatı": 2500.0, "Stok": 30},
        {"Kod": "CF-2006", "Parça Adı": "Hava Filtresi (İç)", "Marka / Model": "Volvo / Renault Kamyon", "Cross 1": "Mann CF1630", "Cross 2": "Donaldson P777639", "Liste Fiyatı": 1800.0, "Stok": 40},
        {"Kod": "CF-3010", "Parça Adı": "Yakıt / Su Ayırıcı", "Marka / Model": "Mercedes Axor / Actros", "Cross 1": "Parker R120P", "Cross 2": "Baldwin BF7633", "Liste Fiyatı": 1500.0, "Stok": 25},
        {"Kod": "CF-4020", "Parça Adı": "Şanzıman Filtresi", "Marka / Model": "ZF Şanzıman Serisi", "Cross 1": "Mann H601", "Cross 2": "Mahle HX12", "Liste Fiyatı": 2200.0, "Stok": 15}
    ])
    df_ilk_urunler.to_csv(URUN_DOSYASI, index=False)

# 2. CRM Teklif Dosyası Yoksa Oluştur
if not os.path.exists(CRM_DOSYASI):
    df_empty_crm = pd.DataFrame(columns=[
        "Tarih", "Firma Adı", "Yetkili", "Telefon", "Şehir", 
        "Toplam Liste", "Toptancı Maliyeti", "Komisyon", "Satın Alınan Ürünler ve Adetler", "Notlar"
    ])
    df_empty_crm.to_csv(CRM_DOSYASI, index=False)

# Güncel ürünleri yükle
df_urunler = pd.read_csv(URUN_DOSYASI)

# Yan Menü: Müşteri ve Ticari Parametreler
st.sidebar.header("👤 Müşteri & İletişim Bilgileri")
firma_adi = st.sidebar.text_input("Firma Adı", placeholder="Örn: Özkanlar Ağır Vasıta")
yetkili_adi = st.sidebar.text_input("Yetkili Adı Soyadı", placeholder="Örn: Ahmet Bey")
telefon = st.sidebar.text_input("Telefon", placeholder="0532...")
sehir = st.sidebar.selectbox("Bölge / Şehir", ["İstanbul (İkitelli/İSTOÇ)", "Ankara (Ostim)", "İzmir (3. Sanayi)", "Bursa", "Konya", "Diğer"])
musteri_notu = st.sidebar.text_area("Müşteri Notu", placeholder="Rezerve edildi, sevkiyat bekleniyor.")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Ticari Parametreler")
toptanci_iskonto_orani = st.sidebar.slider("Toptancı İskontosu (%)", min_value=10, max_value=50, value=30, step=5)
benim_komisyon_orani = st.sidebar.slider("Komisyon Oranım (%)", min_value=1, max_value=15, value=5, step=1)

# Ana Ekran: Ürün Kataloğu ve Stok Durumu
st.subheader("📦 Ürün Kataloğu, Cross Kodları ve Rezerve / Stok Seçimi")
st.markdown("Tablodan ürünlerin eşdeğer (cross) kodlarını görebilir, ihtiyacınız kadar adet seçerek müşteriye rezerve edebilirsiniz.")

# Mevcut ürünleri ekranda göstermek ve adet almak için form yapısı
sepet_verileri = []
guncellenmis_urunler = df_urunler.copy()

for index, row in guncellenmis_urunler.iterrows():
    st.markdown(f"**Kod:** `{row['Kod']}` | **Ürün:** {row['Parça Adı']} | **Uyumlu Araç/Model:** *{row['Marka / Model']}*")
    st.caption(f"🔄 **Cross 1:** {row['Cross 1']} | **Cross 2:** {row['Cross 2']} | 💰 **Liste Fiyatı:** {row['Liste Fiyatı']:,.2f} TL | 📦 **Mevcut Stok:** {row['Stok']} adet")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        # Maksimum seçilebilecek adet stok miktarı kadar olmalı
        secilen_adet = st.number_input(f"Adet Al ({row['Kod']})", min_value=0, max_value=int(row['Stok']), value=0, step=1, key=row['Kod'])
    
    if secilen_adet > 0:
        toplam_tutar = secilen_adet * row['Liste Fiyatı']
        sepet_verileri.append({
            "Kod": row['Kod'],
            "Parça Adı": row['Parça Adı'],
            "Birim Fiyat": row['Liste Fiyatı'],
            "Adet": secilen_adet,
            "Toplam Liste": toplam_tutar
        })
        # Stoktan düşülecek miktarı geçici olarak hesapla
        guncellenmis_urunler.loc[index, 'Stok'] = row['Stok'] - secilen_adet

    st.markdown("---")

# Hesaplama, Stok Düşme ve Kayıt Alanı
if len(sepet_verileri) > 0:
    df_sepet = pd.DataFrame(sepet_verileri)
    
    toplam_liste_tutar = df_sepet["Toplam Liste"].sum()
    toptanci_maliyeti = toplam_liste_tutar * (1 - toptanci_iskonto_orani / 100)
    komisyonum = toptanci_maliyeti * (benim_komisyon_orani / 100)
    
    st.subheader("📊 Teklif Özeti ve Kazanç Tablosu")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Toplam Liste Tutarı", f"{toplam_liste_tutar:,.2f} TL")
    col_b.metric(f"Toptancı Ödeyeceği (%{toptanci_iskonto_orani})", f"{toptanci_maliyeti:,.2f} TL")
    col_c.metric(f"Tahmini Komisyonun (%{benim_komisyon_orani})", f"{komisyonum:,.2f} TL", delta="Net Kazanç")
    col_d.metric("Toptancının Kârı", f"{(toplam_liste_tutar - toptanci_maliyeti):,.2f} TL")
    
    with st.expander("Seçilen Ürünlerin Detaylı Listesi"):
        st.dataframe(df_sepet)
    
    # Kaydet ve Stoğu Güncelle Butonu
    st.markdown("### 💾 Rezervasyonu Tamamla ve Stoğu Düş")
    if st.button("Teklifi Onayla, Stoğu Güncelle ve Müşteriyi Kaydet"):
        if not firma_adi:
            st.error("Lütfen sol menüden Firma Adı giriniz!")
        else:
            # 1. Ürün stoklarını kalıcı olarak güncelle ve CSV'ye yaz
            guncellenmis_urunler.to_csv(URUN_DOSYASI, index=False)
            
            # 2. Satın alınan ürünleri metin olarak özetle
            urun_ozeti = ", ".join([f"{row['Adet']}x {row['Parça Adı']} ({row['Kod']})" for index, row in df_sepet.iterrows()])
            
            yeni_kayit = {
                "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Firma Adı": firma_adi,
                "Yetkili": yetkili_adi,
                "Telefon": telefon,
                "Şehir": sehir,
                "Toplam Liste": toplam_liste_tutar,
                "Toptancı Maliyeti": toptanci_maliyeti,
                "Komisyon": komisyonum,
                "Satın Alınan Ürünler ve Adetler": urun_ozeti,
                "Notlar": musteri_notu
            }
            
            # 3. CRM Kayıtlarına ekle
            df_crm = pd.read_csv(CRM_DOSYASI)
            df_crm_yeni = pd.concat([df_crm, pd.DataFrame([yeni_kayit])], ignore_index=False)
            df_crm_yeni.to_csv(CRM_DOSYASI, index=False)
            
            st.success(f"✅ Başarılı! {firma_adi} için rezerve edilen ürünler stoktan düşüldü ve CRM'e kaydedildi. Sayfayı yenileyebilirsiniz.")
else:
    st.info("💡 Stok rezerve etmek ve teklif çıkarmak için yukarıdaki ürünlerden miktar seçin.")

st.markdown("---")

# Geçmiş Müşteri Teklifleri
st.subheader("📋 Geçmiş Müşteri Rezervasyon ve Teklif Kayıtları")
if os.path.exists(CRM_DOSYASI):
    df_kayitlar = pd.read_csv(CRM_DOSYASI)
    if not df_kayitlar.empty:
        st.dataframe(df_kayitlar, use_container_width=True)
    else:
        st.write("Henüz kaydedilmiş rezervasyon bulunmuyor.")