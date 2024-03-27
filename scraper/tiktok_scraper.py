from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import random
from concurrent.futures import ThreadPoolExecutor
try:
    from utils import solve_captcha, scroll_down, download_audio
except:
    from scraper.utils import solve_captcha, scroll_down, download_audio

class TiktokScraper:
    def __init__(self, headless=True) -> None:
        options = Options()
        options.add_argument("start-maximized")
        if (headless):
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
    
    def solve_captcha(self, wait_time=10):
        """Giải captcha tiktok
        """
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.ID, "captcha-verify-image")))
            try:
                solve_captcha(self.driver)
                return True
            except Exception as ex:
                print('[ERROR] Solve captcha failed')
                return False 
        except Exception as ex:
            print('[INFO] The captcha does not exist')
            return True 

    def get_channel_name(self, channel_url):
        channel = channel_url.split('@')[-1]
        channel = channel.split('/')[0]
        return channel
    
    def get_video_urls(self, channel_url):
        """
        Crawl the URLs of channels through the channel URL

        Args:
            channel_url(str): channel url
        """
        self.driver.get(channel_url)
        time.sleep(random.randint(3,5))
        # Solve captcha if exists
        if not self.solve_captcha(wait_time=10):
            return []
        time.sleep(random.randint(2,3))
        # Get name of channel
        channel_name = self.get_channel_name(channel_url)
        # Close login window
        if self.driver.find_elements("xpath",'//div[@id="login-modal"]'):
            self.driver.find_element("xpath",'//div[@id="login-modal"]').send_keys(Keys.ESCAPE)
        time.sleep(random.randint(2,3))
        # Scroll down
        wait_time = 1
        while scroll_down(self.driver):
            time.sleep(wait_time)
            wait_time += random.choice([0.1, 0.2, 0.2, 0.2])
            print(f'[INFO] Sleep {wait_time} after scrolling down')
        # Get urls
        video_urls = []
        sign = f"{channel_name}/video"
        for element in self.driver.find_elements("xpath",f'//a[contains(@href, "{sign}")]'):
            url = element.get_attribute('href')
            print(f'[INFO] {url}')
            video_urls.append(url)
        return list(set(video_urls))

    def download_audio_from_channel(self, channel_url, output_path=None, num_thread=20):
        """Download audio from tiktok channel

        Args:
            channel_url(str): channel url
            ouput_path(str): path that save audio
            num_thread: number of thread that using for downloading
        
        Returns:
            (bool): True if download successfully else failed
        """
        video_urls = self.get_video_urls(channel_url)
        if not video_urls:
            return False 
        print('[INFO] Starting download audio . . . . . . . . .')
        with ThreadPoolExecutor(max_workers=num_thread) as executor:
            executor.map(download_audio, [(url, output_path) for url in video_urls])
        return True

if __name__ == '__main__':
    tiktok_scraper = TiktokScraper(headless=False)
    tiktok_scraper.download_audio_from_channel(channel_url="https://www.tiktok.com/@duyluandethuong", output_path='audio_test')