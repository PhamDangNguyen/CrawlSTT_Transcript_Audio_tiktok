from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.parse
import requests


def get_VTT(url,folder_save):

    name_save = folder_save +'/' + 'transcript.vie-VN.vtt'

    url = urllib.parse.quote(url)#ma hoa url theo Chorm
    print(url)
    driver = webdriver.Chrome()
    #get link VTT from web 'https://getsubs.cc/?'
    driver.get(f"https://getsubs.cc/?u={url}")
    time.sleep(2)
    transcript_element = driver.find_element(By.XPATH, "//a[@title='Download as VTT File']")
    print(transcript_element)
    link_vtt = transcript_element.get_attribute('href')
    print(link_vtt)
    #get .VTT file from web 'https://getsubs.cc/?'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Referer': 'https://getsubs.cc/?'
    }
    response = requests.get(link_vtt, headers=headers)
    print(response.text)

    with open(name_save, "w", encoding="utf-8",newline='') as f:
        f.write(response.text)
        

if __name__ == "__main__":
    # # get link dowload VTT
    url = 'https://www.tiktok.com/@goctamsu20_/video/7230289891525954821'
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    #     'Referer': 'https://getsubs.cc/?'
    # }
    # link_vtt = "https://getsubs.cc/get_t.php?u=95db6ae82d8aa5234a6c3047fbe3f4b5&format=vtt&hl=vie&a=&removeTags=1"
    # response = requests.get(link_vtt, headers=headers)
    # print(response.status_code)
    # print(response.text)

    # get_VTT(url=url,folder_save="C:/Users/Superman/Desktop/Check_tool/Tiktok_STT/CrawlSTT_Transcript_Audio_tiktok/scraper/extra_functionN")