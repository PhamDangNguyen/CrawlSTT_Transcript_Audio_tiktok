import re
import requests
def get_vtt_text(url, folder_save):
    file_path = folder_save + '/' + 'transcript.vie-VN.vtt'
    headers = {
        'authority': 'v16-webapp.tiktok.com',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'origin': 'https://www.tiktok.com',
        'referer': 'https://www.tiktok.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers={
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    })
    match = re.search(r'\"Url\":(.*?),\"Format\":', response.text)
    if match:
        dataList_string = match.group(1)
        vtt_link = bytes(dataList_string, 'utf-8').decode('unicode_escape').replace('"', '')

        vtt_res = requests.request("GET", vtt_link, headers=headers)
        # print(f"ngon - {vtt_link.re}")
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(vtt_res.text)
       
        return True
    
    print("Loi roi")
    return False


if __name__ == '__main__':
    url = "https://www.tiktok.com/@chu0t_ga0/video/7297043504126102786"
    file_path = "C:/Users/Superman/Desktop/Check_tool/Tiktok_STT/CrawlSTT_Transcript_Audio_tiktok/scraper/extra_functionN"
    # text = get_vtt_text(url, file_path)