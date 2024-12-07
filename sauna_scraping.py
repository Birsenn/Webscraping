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


header = ['url', 'title', 'subtitle', 'text_1_after_sub', 'image1_url', 'image2_url']
write_to_csv(header)

for url in urls:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        table_section = soup.find('table', border='0')
        if table_section:
            title_tag = table_section.find('h5', align='center')
            title = title_tag.get_text(strip=True) if title_tag else "Başlık bulunamadı"
        else:
            table_section = soup.find('table', style="border:0; width:100%")
            title_tag = table_section.find('h1', align='center') if table_section else None
            title = title_tag.get_text(strip=True) if title_tag else "Başlık bulunamadı"

        if table_section:
            p_tag = table_section.find('p', style='text-align:center')
            if p_tag:
                subtitle = p_tag.find('em').get_text(strip=True) if p_tag.find('em') else "Alt başlık bulunamadı"
            else:
                div_tag = table_section.find('div', style='text-align:center')
                if div_tag:
                    subtitle = div_tag.find('em').get_text(strip=True) if div_tag.find('em') else "Alt başlık bulunamadı"
                else:
                    h2_tag = table_section.find('h2', style='text-align:center')
                    if h2_tag:
                        subtitle = h2_tag.get_text(strip=True)
                    else:
                        subtitle = "Alt başlık h2 etiketi bulunamadı"
        else:
            subtitle = "Table bulunamadı"
            
        text_1_after_sub = ""

        if table_section:
            p_tags = table_section.find_all('p', style='text-align:center')
            if len(p_tags) > 1:
                font_tag = p_tags[1].find('font', color="#0000FF")
                if font_tag:
                    text_1_after_sub = font_tag.get_text(strip=True)

                if font_tag:
                    text_1_after_sub = font_tag.get_text(strip=True)
                else:
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

        image_links = []
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

        p_tags = soup.find_all('p')
        start_collecting = False

        for idx, p_tag in enumerate(p_tags):
            if not start_collecting and "skizze" in p_tag.get_text(strip=True).lower():
                start_collecting = True 

            if start_collecting:
                img_tag = p_tag.find('img')
                if img_tag:
                    relative_img_url = img_tag.get('src')
                    if relative_img_url.lower().endswith(valid_extensions):
                        full_img_url = urljoin(url, relative_img_url)
                        image_links.append(full_img_url)

        image1_url = image_links[0] if len(image_links) > 0 else "Resim 1 bulunamadı"
        image2_url = image_links[1] if len(image_links) > 1 else "Resim 2 bulunamadı"

        write_to_csv([url, title, subtitle, text_1_after_sub, image1_url, image2_url])

    except requests.exceptions.RequestException as e:
        write_to_csv([url, "Hata", "Hata", str(e), "Hata", "Hata"])
