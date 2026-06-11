import sys
print("Python dipakai:", sys.executable)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

# ==============================
# 1. SETUP DRIVER
# ==============================
options = webdriver.ChromeOptions()
options.add_argument("--lang=id-ID")
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 40)

# ==============================
# 2. BUKA GOOGLE MAPS UNMUL
# ==============================
driver.get(
    #Kampus gunung kelua
    #"https://www.google.com/maps/place/Universitas+Mulawarman/@-0.4725676,117.1574767,14z/data=!4m6!3m5!1s0x2df67f4bb8b9dcd1:0x6fd5d38233261f93!8m2!3d-0.4684587!4d117.1539974!16s%2Fm%2F0fqmxkv?entry=ttu&g_ep=EgoyMDI2MDEyNS4wIKXMDSoASAFQAw%3D%3D"
    #Kampus Banggeris
    #"https://www.google.com/maps/place/Universitas+Mulawarman,+Kampus+Jalan+Banggeris/@-0.4885258,117.0753889,13z/data=!4m10!1m2!2m1!1sUniversitas+Mulawarman!3m6!1s0x2df67ee347b7c2d1:0xcb73347201ce74c!8m2!3d-0.492518!4d117.122551!15sChZVbml2ZXJzaXRhcyBNdWxhd2FybWFuIgOIAQGSAQp1bml2ZXJzaXR54AEA!16s%2Fg%2F11bc73s5c0?entry=ttu&g_ep=EgoyMDI2MDIwMS4wIKXMDSoASAFQAw%3D%3D"
    #Kampus II
    "https://www.google.com/maps/place/Universitas+Mulawarman,+Kampus+II/@-0.4885258,117.0753889,13z/data=!4m12!1m2!2m1!1sUniversitas+Mulawarman!3m8!1s0x2df67f148917abc3:0x230787853e0773af!8m2!3d-0.4885258!4d117.1474867!9m1!1b1!15sChZVbml2ZXJzaXRhcyBNdWxhd2FybWFuIgOIAQGSARFwdWJsaWNfdW5pdmVyc2l0eeABAA!16s%2Fg%2F11bwfltgnd?entry=ttu&g_ep=EgoyMDI2MDIwMS4wIKXMDSoASAFQAw%3D%3D"
)
time.sleep(10)

# ==============================
# 3. KLIK TAB ULASAN
# ==============================
review_btn = wait.until(EC.element_to_be_clickable((
    By.XPATH, '//button[contains(@aria-label,"Ulasan")]'
)))
review_btn.click()
time.sleep(8)

# ==============================
# 4. AMBIL DIV SCROLL ASLI (INI KUNCI)
# ==============================
scrollable_div = wait.until(EC.presence_of_element_located((
    By.XPATH,
    '//div[contains(@class,"m6QErb") and contains(@class,"DxyBCb")]'
)))

# ==============================
# 5. SCROLL VIA JAVASCRIPT
# ==============================
last_height = driver.execute_script(
    "return arguments[0].scrollHeight", scrollable_div
)

for i in range(200):  # cukup untuk >1200 review
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollHeight",
        scrollable_div
    )
    time.sleep(2)

    new_height = driver.execute_script(
        "return arguments[0].scrollHeight", scrollable_div
    )

    if new_height == last_height:
        break
    last_height = new_height

# ==============================
# 6. KLIK SEMUA 'LAINNYA'
# ==============================
buttons = driver.find_elements(By.XPATH, '//button[contains(text(),"Lainnya")]')
for b in buttons:
    try:
        driver.execute_script("arguments[0].click();", b)
        time.sleep(0.2)
    except:
        pass

# ==============================
# 7. AMBIL DATA REVIEW
# ==============================
reviews = driver.find_elements(By.XPATH, '//div[@data-review-id]')
print("Total review ditemukan:", len(reviews))

data = []

for r in reviews:
    try:
        text = r.find_element(By.XPATH, './/span[contains(@class,"wiI7pd")]').text
    except:
        text = ""

    try:
        rating = r.find_element(By.XPATH, './/span[@role="img"]').get_attribute("aria-label")
    except:
        rating = ""

    if text.strip():
        data.append({
            "review": text,
            "rating": rating
        })

# ==============================
# 8. SIMPAN CSV
# ==============================
df = pd.DataFrame(data)
df.to_csv("review_unmul_google_maps.csv", index=False, encoding="utf-8-sig")

print("==============================")
print("Jumlah ulasan berhasil diambil:", len(df))
print("File disimpan: review_unmul_google_maps.csv")
print("==============================")

driver.quit()
