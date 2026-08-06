import os
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from fronend.models import (
    Mahsulot,
    Category,
    Banner,
    PageBanner,
    AdminAloqa,
    SellerProfile,
    AdminPremiumSettings,
)

# =====================================================================
# DEMO USERS
# =====================================================================
SUPERUSER_USERNAME = "admin"
SUPERUSER_PASSWORD = "admin12345"

SELLERS = [
    {"username": "sotuvchi1", "password": "sotuvchi12345", "name": "Aziz Karimov", "phone": "+998901234501", "location": "Toshkent, Chilonzor", "telegram": "aziz_karimov"},
    {"username": "sotuvchi2", "password": "sotuvchi12345", "name": "Dilnoza Rahimova", "phone": "+998901234502", "location": "Toshkent, Yunusobod", "telegram": "dilnoza_r"},
    {"username": "sotuvchi3", "password": "sotuvchi12345", "name": "Jasur Toshmatov", "phone": "+998901234503", "location": "Samarqand", "telegram": "jasur_t"},
    {"username": "sotuvchi4", "password": "sotuvchi12345", "name": "Malika Yusupova", "phone": "+998901234504", "location": "Farg'ona, Qo'qon", "telegram": "malika_y"},
    {"username": "sotuvchi5", "password": "sotuvchi12345", "name": "Shahzod Ergashev", "phone": "+998901234505", "location": "Buxoro", "telegram": "shahzod_e"},
]

VILOYAT_TUMAN = [
    ("toshkent", "Chilonzor"),
    ("toshkent", "Yunusobod"),
    ("toshkent", "Mirzo Ulug'bek"),
    ("samarqand", "Samarqand sh."),
    ("fargona", "Qo'qon"),
    ("andijon", "Andijon sh."),
    ("namangan", "Namangan sh."),
    ("buxoro", "Buxoro sh."),
    ("xorazm", "Urganch"),
    ("qashqadaryo", "Qarshi"),
    ("jizzax", "Jizzax sh."),
    ("sirdaryo", "Guliston"),
    ("toshkent", "Olmazor"),
    ("toshkent", "Shayxontohur"),
]

# =====================================================================
# PRODUCT DATA  (name, turi, narx, description)
# 20 ta elon har bir kategoriya uchun
# =====================================================================
CATEGORY_DATA = {
    "elektronika": {
        "label": "Elektronika",
        "premium": False,
        "products": [
            ("iPhone 13 128GB", "Smartfon", "7500000", "Zamonaviy smartfon, batareyasi 100%, yangi holatda."),
            ("Samsung Galaxy S23", "Smartfon", "8900000", "Yuqori sifatli kamerasi va tez protsessorli telefon."),
            ("MacBook Air M1", "Noutbuk", "9500000", "Yengil va kuchli noutbuk, batareyasi 18 soat."),
            ("HP Pavilion 15", "Noutbuk", "6200000", "O'qish va ishlash uchun ideal noutbuk."),
            ("AirPods Pro 2", "Quloqchin", "1400000", "Noisy cancelling funksiyali quloqchin."),
            ("JBL Charge 5", "Kolonka", "1100000", "Suvga chidamli, kuchli basli kolonka."),
            ("Apple Watch SE", "Smart soat", "2500000", "Fitnes va sog'liqni kuzatish uchun ajoyib soat."),
            ("PlayStation 5", "O'yin konsoli", "6500000", "Ikki qo'l boshqaruvchisi bilan."),
            ("Canon EOS 2000D", "Kamera", "4800000", "Boshlang'ich fotograf uchun DSLR kamera."),
            ("LG 43'' 4K TV", "Televizor", "3200000", "4K Ultra HD, smart funksiyali televizor."),
            ("Redmi Note 12", "Smartfon", "2300000", "Katta ekran va uzoq batareya quvvati."),
            ("Logitech MX Master 3", "Sichqoncha", "650000", "Professional ish uchun sichqoncha."),
            ("Keychron K2", "Klaviatura", "750000", "Mexanik klaviatura, Bluetooth."),
            ("Samsung 27'' Monitor", "Monitor", "2100000", "Full HD monitor, ish va o'yin uchun."),
            ("HP LaserJet Printer", "Printer", "2900000", "Lazerli printer, tez bosib chiqarish."),
            ("Anker PowerBank 20000mAh", "Power bank", "350000", "Katta quvvatli zaryadlovchi."),
            ("iPad 10.2", "Planshet", "4200000", "O'qish va ishlash uchun planshet."),
            ("DJI Mini 3", "Dron", "7800000", "Yengil va stabil dron, 4K video."),
            ("Xiaomi Robot Vacuum", "Robot changyutkich", "2400000", "Avtomatik tozalovchi robot."),
            ("Bose QC45", "Quloqchin", "2800000", "Yuqori sifatli ovoz, nois cancelling."),
        ],
    },
    "kitob": {
        "label": "Kitoblar",
        "premium": False,
        "products": [
            ("O'tkan kunlar", "Roman", "45000", "Abdulla Qodiriyning mashhur asari."),
            ("Alpomish", "Doston", "30000", "O'zbek xalq dostoni."),
            ("Shahnameh", "Epik asar", "120000", "Firdavsiyning buyuk asari."),
            ("Kichkina shahzoda", "Badiiy", "25000", "Sent-Ekzyuperi asari."),
            ("Python dasturlash", "Darslik", "180000", "Boshlang'ich dasturchilar uchun."),
            ("Ingliz tili qo'llanma", "O'quv qo'llanma", "60000", "Tez va oson ingliz tili."),
            ("Rich dad poor dad", "Moliyaviy", "75000", "Moliyaviy savodxonlik kitobi."),
            ("1984", "Distopiya", "55000", "Jorj Oruellning mashhur asari."),
            ("Bolalar ensiklopediyasi", "Ensiklopediya", "90000", "Bolalar uchun rasmli ensiklopediya."),
            ("Tibbiyot asoslari", "Tibbiyot", "140000", "Tibbiyot talabalari uchun."),
            ("Izohli lug'at", "Lug'at", "85000", "O'zbek tilining izohli lug'ati."),
            ("Harry Potter 1", "Fantastika", "70000", "J.K. Rowling asari."),
            ("She'rlar to'plami", "She'riyat", "40000", "Cho'lpon she'rlari."),
            ("Iqtisodiyot nazariyasi", "Darslik", "110000", "Oliy o'quv yurtlari uchun."),
            ("Psixologiya asoslari", "Ilmiy", "95000", "Psixologiya faniga kirish."),
            ("Organik kimyo", "Darslik", "130000", "Kimyo fakulteti talabalari uchun."),
            ("Xotira", "Ilmiy-ommabop", "80000", "Xotira qobiliyatini rivojlantirish."),
            ("Detektiv hikoyalar", "Detektiv", "50000", "Agata Kristi hikoyalari."),
            ("Komiks Marvel", "Komiks", "45000", "Marvel komikslari to'plami."),
            ("Tarix saboqlari", "Tarixiy", "65000", "Jahon tarixiga sayohat."),
        ],
    },
    "mebel": {
        "label": "Mebellar",
        "premium": False,
        "products": [
            ("Burchak divan", "Divan", "4500000", "Yangi holatda, yumshoq burchak divan."),
            ("Ikki kreslo", "Kreslo", "1800000", "Qulay va zamonaviy kreslolar."),
            ("Karavot 160x200", "Karavot", "3200000", "Matras bilan birga."),
            ("Garderob shkafi", "Shkaf", "2800000", "3 eshikli garderob shkafi."),
            ("Kompyuter stoli", "Stol", "1200000", "Ish xonasi uchun stol."),
            ("Oshxona stoli", "Stol", "950000", "6 kishilik oshxona stoli."),
            ("Kitob javoni", "Javon", "800000", "Zamonaviy kitob javoni."),
            ("Tualet stol", "Stol", "1100000", "Ko'zguli tualet stol."),
            ("Bolalar karavoti", "Karavot", "1500000", "Bolalar uchun qulay karavot."),
            ("Yumshoq puf", "Puf", "250000", "Turli rangda, yumshoq puf."),
            ("Televizor stol", "Stol", "700000", "Televizor uchun zamonaviy stol."),
            ("Ochiq divan", "Divan", "2600000", "Ikki o'rinli ochiq divan."),
            ("Yotoq to'plami", "To'plam", "5500000", "Karavot, shkaf va tualet stol."),
            ("Ofis kreslosi", "Kreslo", "900000", "Ergonomik ofis kreslosi."),
            ("Oshxona to'plami", "To'plam", "6800000", "To'liq oshxona mebellari."),
            ("Qabul stoli", "Stol", "1400000", "Ofis uchun qabul stoli."),
            ("Ilgich javon", "Javon", "400000", "Kiyim uchun ilgich javon."),
            ("Non stoli", "Stol", "550000", "Oshxona uchun qulay stol."),
            ("Shkaf 3 eshikli", "Shkaf", "2200000", "Keng va qulay shkaf."),
            ("Loft stol", "Stol", "1650000", "Loft uslubidagi stol."),
        ],
    },
    "cheteltovarlar": {
        "label": "Chet el tovarlari",
        "premium": False,
        "products": [
            ("Erkaklar teri sumkasi", "Turkiya tovarlari", "850000", "Haqiqiy teridan tayyorlangan sumka."),
            ("Ayollar parfyumi", "Parfyumeriya", "600000", "Fransiya parfyumeriyasi, 100ml."),
            ("Erkaklar qo'l soati", "Soat", "750000", "Yapon mexanizmi bilan."),
            ("Kosmetika to'plami", "Kosmetika", "450000", "Turkiyadan olib kelingan kosmetika."),
            ("Ayollar poyabzali", "Poyabzal", "550000", "Italiya uslubidagi poyabzal."),
            ("Nike krossovka", "Poyabzal", "950000", "Original Nike krossovka."),
            ("Quyosh ko'zoynagi", "Aksessuar", "300000", "UV himoyali ko'zoynak."),
            ("Ayollar sumkasi", "Sumka", "700000", "Brendli ayollar sumkasi."),
            ("Termos 1L", "Uy-ro'zg'or", "150000", "12 soat issiq ushlab turadi."),
            ("Idish-tovoq to'plami", "Oshxona", "400000", "24 donadan iborat to'plam."),
            ("O'yinchoq robot", "O'yinchoq", "250000", "Xitoydan olib kelingan robot."),
            ("Salfetka to'plami", "Uy matolari", "120000", "Yuqori sifatli salfetkalar."),
            ("Pardalar", "Uy matolari", "350000", "Oyna uchun parda to'plami."),
            ("Zargarlik buyumlari", "Zargarlik", "1200000", "Ayollar uchun zargarlik to'plami."),
            ("Fitnes bilaguzuk", "Gadjet", "350000", "Qadam va yurak urishini kuzatadi."),
            ("Erkaklar kamar", "Aksessuar", "180000", "Teri kamar."),
            ("Chanel parfyumi", "Parfyumeriya", "800000", "Chanel No.5, 50ml."),
            ("Ayollar xalati", "Kiyim", "280000", "Yengil va qulay xalat."),
            ("Telefon g'iloflari", "Aksessuar", "50000", "Barcha modellar uchun."),
            ("Qo'l soati Tomos", "Soat", "950000", "Zamonaviy dizayn."),
        ],
    },
    "uyjoyelonlari": {
        "label": "Uy joy elonlari",
        "premium": True,
        "products": [
            ("2 xonali xonadon, Chilonzor", "Ko'chmas mulk", "1200000000", "Markazga yaqin, yangi ta'mirlangan xonadon."),
            ("Yangi uy, Yangihayot", "Uy", "1500000000", "2 qavatli, hujjatlari tayyor."),
            ("3 xonali kvartira, Yunusobod", "Kvartira", "1800000000", "Yashil hudud, park yonida."),
            ("Yer maydoni 10 sotix", "Yer", "600000000", "Toshkent viloyatida."),
            ("Ofis ijaraga", "Ijara", "15000000", "Mustaqillik shoh ko'chasi."),
            ("Do'kon binosi", "Tijorat", "900000000", "Chorsu bozoriga yaqin."),
            ("Dala hovli", "Hovli", "750000000", "Qibray tumanida, bog'li hovli."),
            ("1 xonali kvartira, Sergeli", "Kvartira", "700000000", "Metroga yaqin."),
            ("Yangi qurilish 2 xonali", "Kvartira", "950000000", "2026 yil tugallanadi."),
            ("Tomosha xonadon", "Kvartira", "2300000000", "Mirzo Ulug'bek, shahar manzarasi."),
            ("Ijaraga 1 xonali", "Ijara", "2500000", "Olmazor tumanida, mebelsiz."),
            ("Xususiy uy, Zangiota", "Uy", "1100000000", "Katta hovli, bog'li."),
            ("Ofis maydoni", "Tijorat", "40000000", "Yunusobodda, 100 kv.m."),
            ("Mehmonxona binosi", "Tijorat", "3000000000", "10 xonali mehmonxona."),
            ("Yotoqxona o'rinlari", "Ijara", "5000000", "Talabalar uchun qulay."),
            ("Kottej, Chortoq", "Uy", "1400000000", "Dengiz manzarali."),
            ("Tijorat maydoni ijaraga", "Ijara", "12000000", "Savdo uchun ideal joy."),
            ("Bog' uyi", "Uy", "850000000", "Yuqori Chirchiq, daryo bo'yida."),
            ("4 xonali uy, Chirchiq", "Uy", "1300000000", "Katta hovli bilan."),
            ("Garaj", "Ko'chmas mulk", "120000000", "Avtoulov uchun qulay garaj."),
        ],
    },
    "onavabollar": {
        "label": "Onalar va bolalar",
        "premium": False,
        "products": [
            ("Bolalar aravachasi", "Aravacha", "1200000", "Yengil va ixcham aravacha."),
            ("Chaqaloq beshigi", "Beshik", "900000", "Tabiiy yog'ochdan."),
            ("Oziqlantiruvchi stul", "Stul", "600000", "Sozlanadigan balandlik."),
            ("Bolalar kiyimlari to'plami", "Kiyim", "250000", "0-2 yosh uchun."),
            ("Yurish o'yinchoq", "O'yinchoq", "180000", "Musiqali yurish o'yinchoq."),
            ("Pampers katta to'plam", "Gigiyena", "300000", "5 o'lcham, 100 dona."),
            ("Bolalar sumkasi", "Sumka", "120000", "Maktab uchun qulay."),
            ("Chaqaloq walker", "Aksessuar", "350000", "Yurishni o'rganish uchun."),
            ("Bolalar velosipedi", "Velosiped", "700000", "12 dyuym, yordamchi g'ildirak."),
            ("O'quv stoli", "Stol", "450000", "Chizish va o'qish uchun."),
            ("Bolalar ko'rpasi", "Matras", "200000", "Yumshoq va iliq ko'rpa."),
            ("Tungi lampa", "Yoritish", "90000", "Yulduzli osmon proyektori."),
            ("Bolalar uyi o'yinchoq", "O'yinchoq", "400000", "Chodir uyi, tez yig'iladi."),
            ("Chaqaloq kiyimi", "Kiyim", "150000", "0-3 oy, paxta matosidan."),
            ("Oziq blenderi", "Oshxona", "550000", "Sabzavot pyuresi uchun."),
            ("Chizish to'plami", "O'yinchoq", "80000", "Bo'yoq va qalamlar."),
            ("Sling", "Aksessuar", "250000", "Chaqaloq ko'tarish uchun."),
            ("Bolalar poyabzali", "Poyabzal", "110000", "Ortopedik tagcharm."),
            ("Yumshoq o'yinchoq", "O'yinchoq", "130000", "Musiqali ayiqcha."),
            ("Baby monitor", "Elektronika", "450000", "Chaqaloqni kuzatish uchun."),
        ],
    },
    "avto_elonlari": {
        "label": "Auto elonlar",
        "premium": True,
        "products": [
            ("Chevrolet Cobalt", "Yengil avtomobil", "155000000", "2019 yil, avtomat, 1.5."),
            ("Chevrolet Nexia 3", "Yengil avtomobil", "125000000", "2020 yil, mexanik, kam yurgan."),
            ("Damas", "Yengil avtomobil", "88000000", "2021 yil, yaxshi holatda."),
            ("Matiz", "Yengil avtomobil", "60000000", "Iqtisodiy va ixcham."),
            ("Spark", "Yengil avtomobil", "95000000", "2022 yil, avtomat."),
            ("Gentra", "Yengil avtomobil", "135000000", "2018 yil, salon toza."),
            ("Malibu 2", "Yengil avtomobil", "280000000", "2021 yil, to'liq jihozli."),
            ("Onix", "Yengil avtomobil", "175000000", "2022 yil, kam yurgan."),
            ("Tracker", "Yengil avtomobil", "220000000", "Crossover, 2021 yil."),
            ("Kia K5", "Yengil avtomobil", "400000000", "2022 yil, premium sinf."),
            ("Toyota Camry", "Yengil avtomobil", "350000000", "2020 yil, to'liq optsiya."),
            ("Hyundai Accent", "Yengil avtomobil", "165000000", "2021 yil, avtomat."),
            ("Lada Vesta", "Yengil avtomobil", "130000000", "2019 yil, qulay sedan."),
            ("BYD Chazor", "Yengil avtomobil", "250000000", "Gibrid, iqtisodiy."),
            ("Chery Tiggo 7", "Crossover", "280000000", "2022 yil, yangi holatda."),
            ("Ravon R2", "Yengil avtomobil", "105000000", "2018 yil, avtomat."),
            ("Damas Labo", "Yengil avtomobil", "75000000", "Yuk uchun qulay."),
            ("Lacetti", "Yengil avtomobil", "110000000", "2016 yil, xizmat ko'rsatilgan."),
            ("Captiva", "Crossover", "200000000", "2017 yil, 7 o'rinli."),
            ("Monza", "Yengil avtomobil", "145000000", "2022 yil, kafolat bilan."),
        ],
    },
    "uy_jihozlari": {
        "label": "Uy jihozlari",
        "premium": False,
        "products": [
            ("Kir yuvish mashinasi Samsung", "Texnika", "3500000", "7 kg, yangi holatda."),
            ("Muzlatkich Ariston", "Texnika", "4200000", "Ikkita kamerali muzlatkich."),
            ("Gaz plitasi 4 otliq", "Oshxona", "1500000", "Gaz bilan ishlaydi."),
            ("Changyutkich Dyson", "Texnika", "5500000", "Simsiz, kuchli changyutkich."),
            ("Idish yuvish mashinasi", "Texnika", "4000000", "O'rnatilgan, 12 komplekt."),
            ("Mikroto'lqinli pech", "Oshxona", "1300000", "Grill funksiyali."),
            ("Qahva qaynatgich", "Oshxona", "1000000", "Espresso tayyorlaydi."),
            ("Blender", "Oshxona", "500000", "2 stakanli, kuchli."),
            ("Elektr choynak", "Oshxona", "250000", "1.7L, tez qaynaydi."),
            ("Televizor Samsung 55''", "Texnika", "5000000", "4K, smart TV."),
            ("Konditsioner", "Texnika", "4500000", "9 BTU, sovuq/issiq."),
            ("Ventilyator", "Texnika", "350000", "Oyoqli, uch tezlik."),
            ("Dazmol", "Texnika", "300000", "Bug'li dazmol."),
            ("Soch quritgich", "Texnika", "200000", "3 rejimli fena."),
            ("Elektr gril", "Oshxona", "700000", "Barbekyu uchun."),
            ("Toster", "Oshxona", "180000", "2 tirozli toster."),
            ("Elektr samovar", "Oshxona", "450000", "3L hajmli."),
            ("Multi-cooker", "Oshxona", "900000", "10 rejimli pishirgich."),
            ("Elektr qozon", "Oshxona", "400000", "5L, plov uchun."),
            ("Yumshoq isitgich", "Texnika", "280000", "Konvektor isitgich."),
        ],
    },
    "kiyim": {
        "label": "Kiyim-kechak",
        "premium": False,
        "products": [
            ("Erkaklar kurtka", "Kurtka", "700000", "Qishki, suv o'tkazmaydi."),
            ("Ayollar palto", "Palto", "900000", "Issiq, klassik uslub."),
            ("Futbolka (x3)", "Futbolka", "150000", "Turli rangda."),
            ("Jinsi shim Levi's", "Shim", "450000", "Original Levi's."),
            ("Erkaklar ko'ylagi", "Ko'ylak", "300000", "Oq, L o'lcham."),
            ("Ayollar ko'ylagi", "Ko'ylak", "350000", "Yozgi, yengil."),
            ("Krossovka", "Poyabzal", "500000", "Sport uchun qulay."),
            ("Erkaklar poyabzal", "Poyabzal", "600000", "Klassik tufli."),
            ("Sport kostyum", "Kostyum", "650000", "Komfortli, trikotaj."),
            ("To'y libosi", "Libos", "1500000", "Ayollar uchun elegante libos."),
            ("Ish kostyumi", "Kostyum", "1200000", "Erkaklar uchun klassik."),
            ("Sviter", "Sviter", "250000", "Issiq, jun matosidan."),
            ("Yomg'ir kurtkasi", "Kurtka", "380000", "Yengil va suv o'tkazmas."),
            ("Pijama", "Pijama", "180000", "Ikkita to'plam."),
            ("Xalat", "Xalat", "220000", "Uy uchun qulay."),
            ("Sharf to'plami", "Aksessuar", "90000", "3 dona, issiq."),
            ("Qalpoq", "Aksessuar", "80000", "Qishki, trikotaj."),
            ("Ayollar sumkasi", "Sumka", "550000", "Ko'p joyli sumka."),
            ("Belbog'", "Aksessuar", "120000", "Teri belbog'."),
            ("Galstuk", "Aksessuar", "100000", "Ish uchun galstuk."),
        ],
    },
    "avto": {
        "label": "Avto ehtiyot qismlar",
        "premium": False,
        "products": [
            ("Qishki shina 205/55 R16", "Shina", "1100000", "Yangi, 4 dona."),
            ("Akkumulyator 60Ah", "Akkumulyator", "900000", "12V, kafolatli."),
            ("Motor moyi 5W-30", "Moy", "450000", "4L, sintetik."),
            ("Havo filtri", "Filtr", "60000", "Universal o'lcham."),
            ("Fara birligi", "Fara", "350000", "Cobalt uchun."),
            ("Tormoz kolodkalari", "Tormoz", "250000", "Old va orqa."),
            ("G'ildirak diski", "Disk", "400000", "R15, original."),
            ("Videoregistrator", "Elektronika", "600000", "Full HD, tungi ko'rish."),
            ("Yon ko'zgu", "Ko'zgu", "280000", "Elektr boshqaruvli."),
            ("Kapot", "Kuzov", "500000", "Rangli, kafolatli."),
            ("Bamper", "Kuzov", "700000", "Old bamper, original."),
            ("Kompressor", "Asbob", "350000", "Shinalarni shamollatish."),
            ("Domkrat", "Asbob", "200000", "3 tonna yuk ko'taradi."),
            ("Starter", "Elektr qism", "450000", "Nexia uchun."),
            ("Generator", "Elektr qism", "500000", "90A, yangi."),
            ("Rul qoplamasi", "Aksessuar", "150000", "Teri, tikilgan."),
            ("O'rindiq qoplamalari", "Aksessuar", "320000", "To'liq to'plam."),
            ("Antenna", "Aksessuar", "60000", "Uzun antena."),
            ("Kabellar to'plami", "Elektr qism", "120000", "Massa kabellari."),
            ("Batareya zaryadkasi", "Asbob", "400000", "Intellektual zaryadka."),
        ],
    },
    "boshqa": {
        "label": "Boshqa",
        "premium": False,
        "products": [
            ("Futbol to'pi", "Sport", "250000", "Yangi, 5-o'lcham."),
            ("Gantel to'plami", "Sport", "800000", "10 va 20 kg."),
            ("Gitara", "Musiqa", "900000", "Akustik gitara."),
            ("Skripka", "Musiqa", "1500000", "Boshlang'ich daraja."),
            ("Rower mashinasi", "Sport", "2500000", "Uy uchun trenajyor."),
            ("Velosiped", "Sport", "1800000", "21 tezlikli."),
            ("Qurilish materiallari", "Qurilish", "2000000", "G'isht, sement va boshqalar."),
            ("Asal (3L)", "Oziq-ovqat", "250000", "Tabiiy, xonagi."),
            ("Qo'y go'shti", "Oziq-ovqat", "900000", "Tirik vazn bo'yicha."),
            ("Olma 20kg", "Meva", "100000", "Samarqand olmasi."),
            ("Bog' asboblari to'plami", "Bog'dorchilik", "500000", "Belkurak, ketmon va boshqa."),
            ("Projektor chiroq", "Qurilish", "300000", "LED, tashqi o'rnatish."),
            ("Beton aralashtirgich", "Qurilish", "4500000", "160L hajmli."),
            ("Kartoshka (tovar)", "Oziq-ovqat", "1000000", "Ulurji narx."),
            ("Qoramol", "Chorvachilik", "8000000", "2 yoshli g'unajin."),
            ("Parranda tovuq", "Chorvachilik", "50000", "Yosh tovuqlar."),
            ("Asalari oilasi", "Asalarichilik", "700000", "Gulcham bilan."),
            ("Qishloq xo'jalik texnikasi", "Qishloq xo'jaligi", "15000000", "Traktor, ishchi holatda."),
            ("Baliq to'plami", "Chorvachilik", "300000", "Hovuz uchun."),
            ("Yugurish yo'lakchasi", "Sport", "3000000", "Elektr, uy uchun."),
        ],
    },
}

# =====================================================================
# RASMLAR (images.unsplash.com - haqiqiy mahsulot rasmlari)
# Har bir kategoriyada 20 ta rasm URL. Agar URL ishlamasa, tizim
# avtomatik ravishda picsum.photos dan zaxira rasm oladi.
# =====================================================================
U = "https://images.unsplash.com/photo-{id}?w=800&q=70"
CATEGORY_IMAGES = {
    "elektronika": [
        "1518770660439-4636190af475",
        "1526738549149-8e07eca6c147",
        "1505740420928-5e560c06d30e",
        "1511707171634-5f897ff02aa9",
        "1496181133206-80ce9b88a853",
        "1519085360753-af0119f7cbe7",
        "1525547719571-a2d4ac8945e2",
        "1546868871-7041f2a55e12",
        "1550745165-9bc0b252726f",
        "1550009158-9ebf69173e03",
        "1588508065123-287b28e013da",
        "1555786766-2f18e0e7ee14",
        "1509062522246-3755977927d7",
        "1531297484001-80022131f5a1",
        "1544256718-3bcf237f3974",
        "1593640408182-31c70c8268f5",
        "1542393545-10f5cde2c810",
        "1585298723682-7115561c51b7",
        "1602088113235-229c19758e9b",
        "1512426995798-8f5c78c986d9",
    ],
    "kitob": [
        "1544716278-ca5e3f4abd8c",
        "1524578271613-d550eacf6090",
        "1512820790803-83ca734da794",
        "1526243741027-444d633d7365",
        "1532012197267-da84d127e765",
        "1495446815901-a7297e633e8d",
        "1481627834876-b7833e8f5570",
        "1507842217343-583bb7270b66",
        "1519682337058-a94d03133720",
        "1544947950-fa07a98d237f",
        "1589998059171-988d887df646",
        "1535398089889-dd0df5963144",
        "1513475382585-d06e58bcb0e0",
        "1505751172876-fa1923c5c528",
        "1598619439334-c6f1d12e5d9f",
        "1551268301-787975f1b94e",
        "1603162617224-bc0aefb6e2c4",
        "1610116306796-6fea9f4fae38",
        "1613323072-2f6f1c1f5a0f",
        "1548142813-c0483508a9cd",
    ],
    "mebel": [
        "1555041469-a586c61ea9bc",
        "1538688525198-9b88f6f53126",
        "1592078615290-033ee584e267",
        "1550226891-ef816aed4a98",
        "1505693416388-ac5ce068fe85",
        "1533090161767-e6ffed986c88",
        "1493663284031-b7e3aefcae8e",
        "1524758631624-e2822e304c36",
        "1550254478-ead40cc54513",
        "1567016432779-094069958ea5",
        "1573607212330-ffb9d5ad8e0a",
        "1586023492125-27b2c045efd7",
        "1595526114035-0d45ed16cfbf",
        "1554568218-0f1715e72254",
        "1584100936595-c0654b55a2e2",
        "1595428774223-ef52624120d2",
        "1519710164239-da123dc03ef4",
        "1522708323590-d24dbb6b0267",
        "1583847268964-b28dc8f51f92",
        "1594620302200-9a762244a156",
    ],
    "cheteltovarlar": [
        "1548036328-c9fa89d128fa",
        "1523275335684-37898b6baf30",
        "1585386959984-a4155224a1ad",
        "1523170335258-f5ed11844a49",
        "1596462502278-27bfdc403348",
        "1571781926291-c477ebfd024b",
        "1556228578-8c89e6adf883",
        "1526170375885-4d8ecf77b99f",
        "1575909812264-6902b55846ae",
        "1590874103328-eac38a683ce7",
        "1584917865442-de89df76afd3",
        "1542293786-8b7f2fc436a3",
        "1595950653106-6c9ebd614d3a",
        "1549298916-b41d501d3772",
        "1560343090-f0409e92791a",
        "1572635196237-14b3f281503f",
        "1577803645773-f96470509666",
        "1511499767150-a48a237f0083",
        "1560343090-f0409e92791a",
        "1525904094978-34d5a50d507e",
    ],
    "uyjoyelonlari": [
        "1568605114967-8130f3a36994",
        "1570129477492-45c003edd2be",
        "1600596542815-ffad4c1539a9",
        "1600585154340-be6161a56a0c",
        "1600607687939-ce8a6c25118c",
        "1512917774080-9991f1c4c750",
        "1560448204-e02f11c3d0e2",
        "1523217582562-09d0def993a6",
        "1580587771525-78b9dba3b914",
        "1571003123894-1f0594d2b5d9",
        "1613490493576-7fde63acd811",
        "1600047509807-ba8f99d2cdde",
        "1600585154526-990dced4db0d",
        "1600210492486-724fe5c67fb0",
        "1600566753190-17f0baa2a6c3",
        "1600607687644-c7171b42498f",
        "1560448075-bb985bda2eab",
        "1522708323590-d24dbb6b0267",
        "1502005229762-cf1b2da7c5d6",
        "1494526585095-c41746248156",
    ],
    "onavabollar": [
        "1519238263530-99bdd11df2ea",
        "1522771930-78848d9293e8",
        "1555252333-9f8e92e65df9",
        "1519689680058-324335c77eba",
        "1583484963886-c0d60b3204a3",
        "1503917988258-f87a78e3c995",
        "1503454537195-1dcabb73ffb9",
        "1595435934249-5df7ed86e1c0",
        "1567892118905-4d4e91f0c8e7",
        "1520869562399-e77f4eefa4b8",
        "1516627145497-ae6968895b74",
        "1484820540004-14229fe36ca4",
        "1502374454532-255ab9180d8b",
        "1584320528174-a4edf3cde6a0",
        "1584824489209-2e414c65b4f2",
        "1498233138222-77d3116264e8",
        "1476703993599-0035a21b17a9",
        "1519681393784-d120267933ba",
        "1519682337058-a94d03133720",
        "1503917988258-f87a78e3c995",
    ],
    "avto_elonlari": [
        "1503376780353-7e6692767b70",
        "1542362567-b07e54358753",
        "1533473359331-0135ef1b58bf",
        "1494976388531-d1058494cdd8",
        "1553440569-bcc63803a83d",
        "1583121274602-3e2820c69888",
        "1605559424843-9e4c228bf1c2",
        "1511919884226-fd3cad34687c",
        "1538590631527-3c7f0e00a69e",
        "1552519507-da3b142c6e3d",
        "1571607388263-1044f9ea01dd",
        "1555215695-3004980ad54e",
        "1583267746897-2cf415887172",
        "1550355291-aaa55504a773",
        "1549399542-7e3f8b79c341",
        "1560958089-b8a1929cea89",
        "1571209115301-4d0bb729d762",
        "1590362891991-f776e747a588",
        "1617531653332-bd46c24f2068",
        "1571607388263-1044f9ea01dd",
    ],
    "uy_jihozlari": [
        "1556911220-bff31c812dba",
        "1544244015-0df4b3ffc6b0",
        "1584622650111-993a426fbf0a",
        "1556909114-f6e7ad7d3136",
        "1574269909862-7e1d70bb8078",
        "1585515320310-259814833e62",
        "1556905052-332f0bdf86f6",
        "1590794056226-79ef3a8147e1",
        "1600585152220-90363fe7e115",
        "1616046229478-9901c5536e45",
        "1584345604476-8ec5e12e42dd",
        "1545058455-f8b2d5c63ca2",
        "1584568694244-14fbdf83bd30",
        "1544620347-c4fd4a34d7e7",
        "1593359675129-3e8324ae7d88",
        "1550029402-226115b7c579",
        "1593784991095-a205069470b6",
        "1580894732444-8ecbe7904575",
        "1556911220-bff31c812dba",
        "1600585154340-be6161a56a0c",
    ],
    "kiyim": [
        "1521572163474-6864f9cf17ab",
        "1445205170230-053b83016050",
        "1434389677669-e08b4cac3105",
        "1523381210434-271e8be1f52b",
        "1541099649105-f69ad21f3246",
        "1489987707025-afc232f7ea0f",
        "1543087905-1ac25384d59e",
        "1525507119028-ed4c629a60a3",
        "1512436991641-6745cdb1723f",
        "1489987707025-afc232f7ea0f",
        "1487222477894-8943e31ef7b2",
        "1519238263530-99bdd11df2ea",
        "1548036328-c9fa89d128fa",
        "1560241564-1c524c0b8c9b",
        "1551163943-3f7b2d2d5b8c",
        "1591047139829-d91aecb6caea",
        "1584917865442-de89df76afd3",
        "1560769629-975ec94e6a86",
        "1571875257727-256c39da42af",
        "1539533018447-63fcce2678e3",
    ],
    "avto": [
        "1486262715619-67b85e0b08d3",
        "1530046339160-ce3e530c7d2f",
        "1605559424843-9e4c228bf1c2",
        "1487754180451-c456f719a1fc",
        "1562518093-40f3a0a7a6c0",
        "1578842177283-3bf7fb053ecf",
        "1583267528397-172fbb95dffe",
        "1492144534655-ae79c964c9d7",
        "1621939514649-280e2d25b72c",
        "1504222490345-c075b6008014",
        "1530124566582-a618bc2615dc",
        "1581092160562-40aa08e78837",
        "1581092160607-ee22621dd758",
        "1581091012184-7d837f9b7834",
        "1581092918056-0c4c3acd3789",
        "1489824904134-891ab64532f1",
        "1517420704952-d9f39e95b43e",
        "1562518093-40f3a0a7a6c0",
        "1621939514649-280e2d25b72c",
        "1486262715619-67b85e0b08d3",
    ],
    "boshqa": [
        "1517649763962-0c623066013b",
        "1511379938547-c1f69419868d",
        "1461896836934-ffe607ba8211",
        "1514525253161-7a46d19cd819",
        "1538805060514-97d9cc17730c",
        "1498050108023-c5249f4df085",
        "1503387762-592deb58ef4e",
        "1471508936332-e5fd5c87c9b6",
        "1544025162-d76694265947",
        "1552674605-db6ffd4facb5",
        "1534438327276-14e5300c3a48",
        "1504307651254-35680f356dfd",
        "1585336261022-680e295ce3fe",
        "1416879595882-3373a0480b5b",
        "1558981806-ec527fa84c39",
        "1526506118085-60ce8714f8c5",
        "1517836357463-d25dfeac3438",
        "1576678927484-cc907957088c",
        "1530549387789-4c1017266635",
        "1550345332-09e3ac987658",
    ],
}

BANNER_FILES = {
    "desktop": ["main_page_banner.webp", "main_page_banner_2.webp"],
    "mobile": ["main_page_banner_3.webp", "main_page_banner_4.webp"],
}


def download(url, filepath, timeout=30):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if len(data) < 2000:
            return False, "too small"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(data)
        return True, "downloaded"
    except Exception as e:
        return False, str(e)[:120]


def ensure_image(cat_key, index):
    """Rasmni yuklab oladi yoki mavjud bo'lsa qaytaradi. URL manzilini qaytaradi."""
    fname = "asosiyimg/seed_{}_{}.jpg".format(cat_key, index)
    filepath = os.path.join(settings.MEDIA_ROOT, fname)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
        return fname, "cache"
    ids = CATEGORY_IMAGES.get(cat_key, [])
    url = U.format(id=ids[index % len(ids)]) if ids else None
    ok, status = download(url, filepath) if url else (False, "no url")
    if not ok:
        ok, status = download(
            "https://picsum.photos/seed/{}_{}/800/600".format(cat_key, index),
            filepath,
        )
    return fname, status


class Command(BaseCommand):
    help = "Har bir kategoriyaga 20 tadan e'lon qo'shadi (rasmlar bilan) va demo ma'lumotlar yaratadi."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Mavjud bo'lsa ham qayta ishga tushirish.")
        parser.add_argument("--no-images", action="store_true", help="Rasm yuklab olmaslik (faqat bazaga yozish).")

    def handle(self, *args, **options):
        force = options["force"]
        no_images = options["no_images"]
        now = timezone.now()

        existing = Mahsulot.objects.count()
        if existing >= sum(len(c["products"]) for c in CATEGORY_DATA.values()) and not force:
            self.stdout.write("E'lonlar allaqachon mavjud ({} ta). --force bilan qayta ishga tushiring.".format(existing))
            return

        # ---------------- USERS ----------------
        admin, created_admin = User.objects.get_or_create(
            username=SUPERUSER_USERNAME,
            defaults={"email": "admin@tezsot.uz", "is_staff": True, "is_superuser": True},
        )
        if created_admin:
            admin.set_password(SUPERUSER_PASSWORD)
            admin.save()
            self.stdout.write("Superuser '{}' yaratildi.".format(SUPERUSER_USERNAME))

        seller_users = []
        for s in SELLERS:
            user, created = User.objects.get_or_create(
                username=s["username"],
                defaults={"email": "{}@example.uz".format(s["username"]), "first_name": s["name"].split()[0], "last_name": s["name"].split()[-1]},
            )
            if created:
                user.set_password(s["password"])
                user.save()
            SellerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "phone": s["phone"],
                    "location": s["location"],
                    "telegram": s["telegram"],
                    "bio": "{} - Tez Sot Market sotuvchisi".format(s["name"]),
                },
            )
            seller_users.append(user)
        self.stdout.write("Sotuvchilar: {}".format(", ".join(u.username for u in seller_users)))

        # ---------------- CATEGORIES ----------------
        for key, data in CATEGORY_DATA.items():
            Category.objects.get_or_create(
                name=data["label"],
                defaults={"description": "{} bo'limi".format(data["label"]), "has_premium": data.get("premium", False), "premium_fee": 50000 if data.get("premium") else 0},
            )
        self.stdout.write("{} ta kategoriya yaratildi.".format(Category.objects.count()))

        # ---------------- ADMIN ALOQA ----------------
        if not AdminAloqa.objects.exists():
            AdminAloqa.objects.create(
                manzil="Toshkent shahri, Chilonzor tumani, Bunyodkor ko'chasi 1",
                telefon="+998901234567",
                email="info@tezsot.uz",
                telegram="https://t.me/tezsotmarket",
                instagram="https://instagram.com/tezsotmarket",
                facebook="https://facebook.com/tezsotmarket",
            )

        # ---------------- BANNERS ----------------
        banner_count = Banner.objects.count()
        if banner_count == 0:
            for dev, files in BANNER_FILES.items():
                for i, fname in enumerate(files):
                    rel = "banners/{}".format(fname)
                    if os.path.exists(os.path.join(settings.MEDIA_ROOT, rel)):
                        b = Banner(
                            title="Promo banner {}".format(i + 1),
                            device_type=dev,
                            is_active=True,
                        )
                        b.image.name = rel
                        b.save()
            self.stdout.write("Bannerlar yaratildi.")

        if not PageBanner.objects.exists():
            for page, title, subtitle in [
                ("home", "Tez Sot Market", "O'zbekistondagi eng tez savdo platformasi"),
                ("profile", "Shaxsiy kabinet", "E'lonlaringizni boshqaring"),
            ]:
                PageBanner.objects.create(page=page, title=title, subtitle=subtitle, is_active=True)

        AdminPremiumSettings.get_settings()

        # ---------------- PRODUCTS ----------------
        total = 0
        downloads = {"downloaded": 0, "cache": 0, "picsum": 0}
        for cat_key, data in CATEGORY_DATA.items():
            products = data["products"]
            self.stdout.write("[{}] {} ta e'lon qo'shilmoqda...".format(data["label"], len(products)))
            for i, (name, turi, narx, desc) in enumerate(products):
                seller = seller_users[i % len(seller_users)]
                viloyat, tuman = VILOYAT_TUMAN[i % len(VILOYAT_TUMAN)]

                fname = "asosiyimg/seed_{}_{}.jpg".format(cat_key, i)
                if no_images:
                    status = "skipped"
                else:
                    fname, status = ensure_image(cat_key, i)
                    if status == "picsum":
                        downloads["picsum"] += 1
                    else:
                        downloads[status] += 1

                p = Mahsulot(
                    user=seller,
                    category=cat_key,
                    mahsulotturi=turi,
                    name=name,
                    viloyat=viloyat,
                    tuman=tuman,
                    manzil="{} tumani".format(tuman),
                    telefon=seller.seller_profile.phone,
                    telegram_username=seller.seller_profile.telegram,
                    email=seller.email,
                    tavsif="{}.\n\n{}. Holati: yangi. Narx kelishilgan. Batafsil ma'lumot uchun telefon qiling.".format(desc, turi),
                    sana=(now - timedelta(days=i)).date(),
                    narx=narx,
                    miqdor=(i % 3) + 1,
                    search_keywords="{} {} {} {}".format(name, turi, data["label"], desc),
                )
                if not no_images:
                    pool = CATEGORY_IMAGES.get(cat_key, [])
                    p.asosiyimg.name = fname
                    if pool:
                        p.birimg.name = "asosiyimg/seed_{}_{}.jpg".format(cat_key, (i + 1) % len(products))
                        p.ikkiimg.name = "asosiyimg/seed_{}_{}.jpg".format(cat_key, (i + 2) % len(products))
                        p.uchuimg.name = "asosiyimg/seed_{}_{}.jpg".format(cat_key, (i + 3) % len(products))
                p.save()

                # Har bir kategoriyadan 2 tasini premium qilish (home sahifasi uchun)
                if i < 2 and data.get("premium", False):
                    p.is_premium = True
                    p.premium_since = now
                    p.premium_expiry = now + timedelta(days=30)
                    p.premium_priority = 7
                    p.is_featured = True
                    p.featured_until = now + timedelta(days=30)
                    p.save()

                total += 1

            self.stdout.write("  [OK] {} - {} ta e'lon".format(data["label"], len(products)))
        self.stdout.write(
            self.style.SUCCESS(
                "\nTayyor! Jami {} ta e'lon qo'shildi (rasmlar: {} yangi, {} keshlangan, {} picsum).".format(
                    total, downloads["downloaded"], downloads["cache"], downloads["picsum"]
                )
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Admin: login -> {}, parol -> {}".format(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
            )
        )
