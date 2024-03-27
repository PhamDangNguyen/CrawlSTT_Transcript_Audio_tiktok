from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import cv2 as cv
import numpy as np
import os
from collections import Counter
import time
import random
import requests

def __solve_captcha(driver):
    print('wait img loader...')
    while True:
        try:
            img = driver.find_element(By.ID, "captcha-verify-image")
            if img.get_attribute('src'):
                time.sleep(1)
                img.screenshot('foo.png')
                break
        except Exception as e:
            print('Failed to read image from captcha')
    img = cv.imread('foo.png')
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    corners = cv.goodFeaturesToTrack(gray, 15, 0.05, 1)
    corners = np.int0(corners)

    x_Array = []
    for i in corners:
        x, y = i.ravel()
        cv.circle(img, (x, y), 3, 255, -1)
        if x > 70:
            x_Array.append(x)

    x_Array.sort()
    print(x_Array)

    slider = driver.find_element(
        By.CLASS_NAME, "captcha_verify_slide--slidebar")
    source = driver.find_element(
        By.CLASS_NAME, "secsdk-captcha-drag-icon")
    source_location = source.location
    source_size = source.size

    array = [170, 345, 400, 400, 345]
    # проверка числа на уникальность, для устранения "гуляюших координат"
    unic = Counter(x_Array)
    for x in x_Array:
        if unic[x] > 1:
            x_offset = x-8
            break

    y_offset = 0
    action = ActionChains(driver)
    try:
        steps_count = 5
        step = (x_offset)/steps_count
        act_1 = action.click_and_hold(source)
        for x in range(0, steps_count):
            act_1.move_by_offset(step, y_offset)
        act_1.release().perform()

        msg = driver.find_element(
            By.CLASS_NAME, 'msg').find_element(By.TAG_NAME, 'div').text
        while msg == '':
            msg = driver.find_element(
                By.CLASS_NAME, 'msg').find_element(By.TAG_NAME, 'div').text
        print(msg)

        if 'Верификация пройдена' in msg or 'complete' in msg:
            return {'success': 1}
        else:
            return {'success': 0}

    except Exception as e:
        print(e)

def solve_captcha(driver):
    print('Checking captcha')
    if driver.find_elements(By.ID, "captcha-verify-image"):
        cnt = 0
        while 1:
            print('Captcha solving . . . . . . . . . . . . . . . . . . . . .')
            ans = __solve_captcha(driver)
            if ans['success']:
                break
            time.sleep(random.randint(3, 5))
            cnt += 1
            if cnt > 5:
                raise Exception('Failed to solve captcha')
    else:
        print("Don't exist captcha")

def scroll_down(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Calculate new scroll height and compare with last scroll height
    time.sleep(random.randint(2,3))
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        return False
    return True

def download_audio(args):
    video_url, output_path = args
    """Tải audio có transcript

    Args:
        video_url(str): tiktok video url
    """
    # Create output path
    if output_path and not os.path.exists(output_path):
        os.makedirs(output_path)
    # Get video information
    video_id = video_url.split('/video/')[-1]
    channel = video_url.split('@')[-1].split('/video')[0]
    if not output_path:
        folder_path = os.path.join('audio', channel, video_id)
    else:
        folder_path = os.path.join(output_path, channel, video_id)
    # Download transcript
    dl_transcript_cmd = f'yt-dlp --write-subs --output "transcript" --paths "{folder_path}" --skip-download "{video_url}"'
    os.system(dl_transcript_cmd)
    # Download audio
    dl_audio_cmd = f'yt-dlp --extract-audio --audio-format wav --postprocessor-args "-ar 16000" --output "{video_id}.wav" --paths "{folder_path}" "{video_url}"'
    os.system(dl_audio_cmd)