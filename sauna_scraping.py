from urllib import request
import requests
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

##################################################################
#URLs
df = pd.read_csv("/Users/birsenbayat/Desktop/Detailpages_URLs.csv")
urls = df["Kundenseiten URLs"]

#Scraping
def write_to_csv(data, filename='sauna_sample1.csv'):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)


# Başlıkları CSV dosyasına yazmak için header
header = ['url', 'title', 'subtitle', 'text_1_after_sub', 'image1_url', 'image2_url']
write_to_csv(header)

for url in urls:
    try:
        # HTTP isteği gönder
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP hatalarını kontrol et

        # HTML'yi parse et
        soup = BeautifulSoup(response.text, "html.parser")

        # Başlık (title) bulma
        table_section = soup.find('table', border='0')  # İlk table_section'ı arıyoruz
        if table_section:
            title_tag = table_section.find('h5', align='center')
            title = title_tag.get_text(strip=True) if title_tag else "Başlık bulunamadı"
        else:
            # Eğer ilk table_section bulunmazsa, alternatif table'ı arıyoruz
            table_section = soup.find('table', style="border:0; width:100%")
            title_tag = table_section.find('h1', align='center') if table_section else None
            title = title_tag.get_text(strip=True) if title_tag else "Başlık bulunamadı"

        # Alt başlık (subtitle) bulma - Table altındaki <p> veya <div> etiketindeki <em> etiketini alıyoruz
        if table_section:
            p_tag = table_section.find('p', style='text-align:center')
            if p_tag:
                subtitle = p_tag.find('em').get_text(strip=True) if p_tag.find('em') else "Alt başlık bulunamadı"
            else:
                # Eğer <p> etiketi bulunmazsa, <div style="text-align:center"> altında <em> etiketini arıyoruz
                div_tag = table_section.find('div', style='text-align:center')
                if div_tag:
                    subtitle = div_tag.find('em').get_text(strip=True) if div_tag.find('em') else "Alt başlık bulunamadı"
                else:
                    # <p> ve <div> etiketi bulunmazsa <h2> etiketine bakıyoruz
                    h2_tag = table_section.find('h2', style='text-align:center')
                    if h2_tag:
                        subtitle = h2_tag.get_text(strip=True)
                    else:
                        subtitle = "Alt başlık h2 etiketi bulunamadı"
        else:
            # Eğer ilk table_section ve alternatif table_section bulunmazsa
            subtitle = "Table bulunamadı"

        # "text_1_after_sub" metnini bulma - <font color="#0000FF"> etiketi içindeki metni alıyoruz
        text_1_after_sub = ""

        # table_section'ın None olup olmadığını kontrol ediyoruz
        if table_section:
            p_tags = table_section.find_all('p', style='text-align:center')  # Tüm <p> etiketlerini bul
            if len(p_tags) > 1:  # Eğer birden fazla <p> etiketi varsa
                font_tag = p_tags[1].find('font', color="#0000FF")  # İkinci <p> etiketini seçiyoruz
                if font_tag:
                    text_1_after_sub = font_tag.get_text(strip=True)

                if font_tag:
                    text_1_after_sub = font_tag.get_text(strip=True)
                else:
                    # Eğer <font> etiketi bulamazsak, h2'yi kontrol et
                    h2_tag = table_section.find('h2', style='text-align:center')
                    if h2_tag:
                        font_tag = h2_tag.find('font', color="#0000FF")
                        if font_tag:
                            text_1_after_sub = font_tag.get_text(strip=True)
                        else:
                            text_1_after_sub = "Text 1 after sub h2 içinde bulunamadı"
                    else:
                        text_1_after_sub = "Text 1 after sub etiketi bulunamadı"
        else:
            text_1_after_sub = "Table section bulunamadı"

        # Fotoğraf linklerini saklamak için bir liste
        image_links = []
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

        # Tüm <p> etiketlerini bul
        p_tags = soup.find_all('p')
        start_collecting = False

        # Her bir <p> etiketini kontrol et
        for idx, p_tag in enumerate(p_tags):
            if not start_collecting and "skizze" in p_tag.get_text(strip=True).lower():
                start_collecting = True  # Başlama noktasını işaretle

            if start_collecting:
                img_tag = p_tag.find('img')  # <p> içindeki <img> etiketi
                if img_tag:
                    relative_img_url = img_tag.get('src')  # <img> etiketindeki src değerini al
                    if relative_img_url.lower().endswith(valid_extensions):  # Uzantıyı kontrol et
                        full_img_url = urljoin(url, relative_img_url)  # Tam URL oluştur
                        image_links.append(full_img_url)  # URL'yi sakla

        # Image URLs ekleme
        image1_url = image_links[0] if len(image_links) > 0 else "Resim 1 bulunamadı"
        image2_url = image_links[1] if len(image_links) > 1 else "Resim 2 bulunamadı"

        # CSV'ye yazma
        write_to_csv([url, title, subtitle, text_1_after_sub, image1_url, image2_url])

    except requests.exceptions.RequestException as e:
        # Hata durumunda, örneğin URL'ye ulaşılamazsa
        write_to_csv([url, "Hata", "Hata", str(e), "Hata", "Hata"])
