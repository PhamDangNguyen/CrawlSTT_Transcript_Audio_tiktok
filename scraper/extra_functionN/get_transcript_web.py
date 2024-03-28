from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.parse
import requests


def get_VTT(url,folder_save,index):

    name_save = folder_save +'/' + f'{index}.vtt'

    url = urllib.parse.quote(url)#ma hoa url theo Chorm
    driver = webdriver.Chrome()
    #get link VTT from web 'https://getsubs.cc/?'
    driver.get(f"https://getsubs.cc/?u={url}")
    time.sleep(1)
    transcript_element = driver.find_element(By.XPATH, "//a[@title='Download as VTT File']")
    print(transcript_element)
    link_vtt = transcript_element.get_attribute('href')
    #get .VTT file from web 'https://getsubs.cc/?'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Referer': 'https://getsubs.cc/?'
    }
    response = requests.get(link_vtt, headers=headers)

    with open(name_save, "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    # # get link dowload VTT
    url = 'https://www.tiktok.com/@chu0t_ga0/video/7297043504126102786'
    # url = urllib.parse.quote(url)
    # driver = webdriver.Chrome()
    # driver.get(f"https://getsubs.cc/?u={url}")
    # time.sleep(1)

    # transcript_element = driver.find_element(By.XPATH, "//a[@title='Download as VTT File']")
    # print(transcript_element)

    # link_vtt = transcript_element.get_attribute('href')
    # # print(link_vtt)

    # #get VTT file
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    #     'Referer': 'https://getsubs.cc/?'
    # }
    # response = requests.get(link_vtt, headers=headers)

    # with open("test.VTT", "w", encoding="utf-8") as f:
    #     f.write(response.text)
    # get_VTT(url=url,folder_save="C:/Users/Superman/Desktop/Check_tool/Tiktok_STT/voice-tiktok",index=1)