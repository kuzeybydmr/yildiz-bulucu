# Gerekli modülleri içe aktarma
import os
from datetime import datetime, timezone
import time
import math
import json
try:
    import serial.tools.list_ports as listele
    import serial
except ModuleNotFoundError:
    os.system("pip install serial")

def yildiz_konum(ya, da, en, boy, utc_zaman=None):
    # Fonksiyonda verilmediyse UTC zamanı ayarlama
    if utc_zaman is None:
        utc_zaman = datetime.now(timezone.utc)

    # Jülyen tarihi hesabı
    d = (utc_zaman - datetime(2000, 1, 1, 12, tzinfo=timezone.utc)).total_seconds() / 86400.0

    gmst = ((18.697374558 + 24.06570982441908 * d) % 24) * 15

    dec_rad = math.radians(da)
    lat_rad = math.radians(en)

    # Radyan olarak saat yönü
    ha_rad = math.radians((gmst + boy) % 360) - math.radians(ya)

    # Dik açıklık hesabı
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    alt_rad = math.asin(sin_alt)

    # Yatay açıklık hesabı
    cos_az = (math.sin(dec_rad) - math.sin(alt_rad) * math.sin(lat_rad)) / (math.cos(alt_rad) * math.cos(lat_rad))
    az_rad = math.acos(cos_az)

    # Saat açısına göre yönü ayarlama
    if math.sin(ha_rad) > 0:
        az_rad = 2 * math.pi - az_rad

    return math.degrees(az_rad), math.degrees(alt_rad)

os.system("color")

print("\033[94mYıldız Bulucu\033[0m")

portlar = listele.comports()
if len(portlar) != 0:
    for port in portlar:
        print(f"\033[92mBağlanıldı: {port.description}\033[0m")
        if "USB-SERIAL" in port.description:
            arduino = serial.Serial(port.device)
            arduino.baudrate = 9600
            break
else:
    print("\033[91mLütfen cihazın kablosunu bilgisayarın USB girişine bağlayın.\033[0m\nBağladıktan sonra programı tekrar çalıştırabilirsiniz.")
    os.system("pause")
    quit()

yildiz_konumlari = {
    "andromeda": (10.684, 41.269),
    "sirius": (101.287, -16.716),
    "betelgeuse": (88.793, 7.407),
    "polaris": (37.954, 89.264),
    "vega": (279.234, 38.783),
    "arcturus": (213.915, 19.182),
    "antares": (247.351, -26.432),
    "rigel": (78.634, -8.202),
    "aldebaran": (68.98, 16.509),
    "canopus": (95.987, -52.695),
    "capella": (79.172, 45.998),
    "altair": (297.696, 8.868),
    "spica": (201.298, -11.161),
    "procyon": (114.825, 5.225),
    "deneb": (310.358, 45.281),
    "fomalhaut": (344.412, -29.622),
    "barnard": (119.4520769583333, 4.6933649722222)
}

print("Çıkış yapmak için \033[1;4mCtrl + C\033[0m")

ayar_klasoru = os.path.join(os.getcwd(), "Yıldız Bulucu")
ayar_dosyasi = os.path.join(ayar_klasoru, "ayar.json")

if os.path.exists(ayar_dosyasi):
    ayar = json.loads(open(ayar_dosyasi, 'r').read())
    enlem, boylam = ayar["enlem"], ayar["boylam"]
else:
    enlem, boylam = input("Gözlemci enlemini girin (°): "), input("Gözlemci boylamını girin (°): ")
    if not os.path.exists(ayar_klasoru):
        os.mkdir(ayar_klasoru)
    open(ayar_dosyasi, 'w').write("{" + f'\n\t"enlem": {enlem},\n\t"boylam": {boylam}\n' + "}")

yildiz = input("Yıldız adını girin: ")

yatay_aciklik, dik_aciklik = yildiz_konumlari[yildiz.lower()][0], yildiz_konumlari[yildiz.lower()][1]

while True:
    az, alt = yildiz_konum(yatay_aciklik, dik_aciklik, float(enlem), float(boylam))
    
    if alt >= 0:
        arduino.write(f"{az},{alt}\n".encode('utf-8'))
        print(f"\033[92m Azimut: {az:4f} İrtifa: {alt:4f} \033[0m\r", end="")
    else:
        print("\033[91mYıldız ufkun altında.\033[0m\r", end="")

    time.sleep(1)