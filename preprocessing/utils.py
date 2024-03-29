import tqdm
import os
import re
import requests
import json
from typing import List, Dict, Tuple, Union
from unidecode import unidecode
from time import time
from scipy.io import wavfile
from pymongo import MongoClient 
import time
import subprocess

cli = MongoClient(host='103.252.1.144', port=27017, username='admin', password='CIST2o20')
col = cli.voice.error

def ffmpeg_convert(input_audio_path,output_audio_path):
    # Execute ffmpeg command to resample and convert to mono
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_audio_path,
        '-ac', '1',
        '-ar', '16000',
        '-c:a', 'pcm_s16le',
        '-y',  # Overwrite output file if it already exists
        output_audio_path
    ]

    # Execute ffmpeg command
    subprocess.run(ffmpeg_command)


EN_VOCAB = set(open("preprocessing/data/en_words.txt", "r").read().splitlines())
VI_VOCAB = set(open("preprocessing/data/vi_words.txt", "r", encoding="utf-8").read().splitlines())

def _normalize_text(text):
    """ Chuẩn hóa từ bằng cách chuyển về viết thường và xóa bỏ dấu cách (space) dư thừa

    Args:
        text(str): Câu đầu vào
    Returns:
        (str): Câu sau khi được chuẩn hóa
    """
    text = text.lower()
    text = ' '.join(text.split())
    return text 

def _contains_digit(text):
    """Kiểm tra từ có chứa chữ số không

    Args:
        text(str): Từ đầu vào
    Returns:
        (bool): True nếu chứa chữ số còn lại là False
    """
    pattern = r'\d'
    return bool(re.search(pattern, text))

def convert_16khz(csv_name='final_label.csv', new_path='audio_processed/', old_path='audio_cut/'):
    """Chuyển đổi audio về dạng 1 channel + 16khz

    Args:
        csv_name(str): Đường dẫn file csv chứa thông tin địa chỉ audio và transcript của nó
        new_path(str): Vị trí mới để lưu audio sau khi đã xử lý
        old_path(str): Vị trí audio cần được xử lý
    Returns:
        (): File csv mới chứa thông tin sau khi đã được xử lý
    """
    print('[INFO] Converting:', csv_name)
    with open(f'{csv_name[:-4]}_1ch.csv', 'w', encoding='utf8') as fp:
        print(f'file,text,duration', file=fp)
        pbar = tqdm.tqdm(open(csv_name,encoding='utf8').read().strip().split('\n'))
        for line in pbar:
            try:
                path, text, _ = line.split(',')
                path = path.replace('\\', '/')
                # print(path,"----",text)
            except Exception as ex:
                print(ex)
                continue
            if len(text) < 5:
                continue
            _new_path = path.replace(old_path, new_path)
            assert os.path.exists(path)
            # _new_path.replace('\\', '/')
            new_dir_path = '/'.join(_new_path.split('/')[:-1])
            if not os.path.exists(new_dir_path):
                os.makedirs(new_dir_path)

            _new_path = _new_path[:-4] + '_1ch.wav'
            if not os.path.exists(_new_path):
                print(path)
                print(_new_path)
                ffmpeg_convert(path,_new_path)
            
            assert os.path.exists(_new_path)      
            fs, speech = wavfile.read(_new_path)

            duration = len(speech) / fs

            if duration > 20 or duration < 1:
                continue
            print(f'{_new_path},{text},{duration}', file=fp)

def compare(raw_text, norm_words, index):
    """So sánh transcript của audio với transcript sau khi infer qua model để chuyển đổi token dạng số thành chữ số 

    Args:
        raw_text(str): transcript của audio sau khi crawl
        norm_words(list): list các token sau khi qua infer 
        index(int): vị trí của token trong raw_text cần so sánh 
    Returns:
        (str|None): chữ số tương ứng với số trong raw_text nếu tìm được, không trả về None
    """
    for i in range(index -2, index + 3):
        try:
            if raw_text[index] == norm_words[i]["content"].lower():
                return ' '.join([item["content"] for item in norm_words[i]["raw_words"]])
        except:
            continue
    return None

def speech_2_text_upload_file(audio_path):
    url = "https://voicestreaming.cmccist.ai/speech_to_text_upload_file"
    payload={'is_normalize': '1'}
    files=[
        ('content',('2_1ch.wav',open(audio_path,'rb'),'audio/wav'))
    ]
    headers = {
        'api_key': 'mtqijSUcj3hC96vWB6bsmqkgTud7y1tYQ4Tawa0R2V8OwShEAp8E3GEuCZ4F8Uo5'
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        response = response.json()
        return response.get("task_id")
    return None 

def speech_to_text(audio_path):
    task_id = speech_2_text_upload_file(audio_path)
    if not task_id:
        return None
    url = "https://voicestreaming.cmccist.ai/get_result_speech_to_text_large_file"
    payload = {
        'task_id': task_id,
        'detail_word': '1'
        }
    headers = {
        'api_key': 'mtqijSUcj3hC96vWB6bsmqkgTud7y1tYQ4Tawa0R2V8OwShEAp8E3GEuCZ4F8Uo5'
        }
    retry = 0
    while retry < 10: 
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200 and response.json().get("metadata"):
            return response.json()
        time.sleep(2)
        retry = retry + 1
    return None 

def solve(audio_path, raw_text):
    is_solved = True
    raw_text = raw_text.split()
    response = speech_to_text(audio_path)
    norm_words = []
    for segment in response["metadata"]["segments"]:
        norm_words += segment["norm_words"]
    for i in range(len(raw_text)):
        if _contains_digit(raw_text[i]):
            word_num = compare(raw_text, norm_words, i)
            if word_num:
                raw_text[i] = word_num
            else:
                is_solved = False 
                break
    if is_solved:
        return ' '.join(raw_text)
    return None 

def convert_num_to_wordnum(csv_name='final_label_1ch.csv'):
    """
    How to work:
    - Step 1: Call API to force alignment
    - Step 2: Compare number in Tiktok label and CMC model in the same location
    - Step 3: If same (or nearly) location, replace norm number of CMC to list of raw words
    """
    with open(f'{csv_name[:-4]}_wordnum.csv', 'w', encoding='utf8') as fp:
        print(f'file,text,duration', file=fp)
        pbar = tqdm.tqdm(open(csv_name,encoding='utf8').read().strip().split('\n')[1:])
        for line in pbar:
            path, text, duration = line.split(',')
            # Chuẩn hóa dữ liệu
            text = _normalize_text(text)
            # Kiểm tra có số trong text không, nếu có thì xử lý
            if _contains_digit(text):
                norm_text = solve(path, text)
                if not norm_text:
                    try:
                        col.insert_one({'path': path, 'text': text, 'duration': duration, 'error': 'convert_num_to_wordnum'})
                    except:
                        pass 
                    continue
                text = norm_text
            print(f'{path},{text},{duration}', file=fp)

def check_vi(word: str, max_distance: int = 0):
    """Kiểm tra một từ có phải tiếng Việt hay không
    - Nếu từ đó có trong vocab tiếng Việt -> True
    - Nếu từ đó có chứa dấu thanh -> True
    """
    return word.lower() in VI_VOCAB or unidecode(word) != word

def check_num(word:str):
    """
    Kiểm tra xem có phải số không
    """
    return bool(re.search(r'\w*\d\w*', word))

def check_en(
    word: str,
) -> Tuple:
    """Kiểm tra một từ có phải là từ tiếng Anh hay không
    - Nếu từ đó có nhỏ hơn hoặc bằng 3 chữ cái -> False
    - Nếu từ đó có trong vocab tiếng Anh -> True
    """
    return len(word) > 3 and word.lower() in EN_VOCAB

def check_vocab(text):
    for word in text.split():
        if check_num(word):
            continue
        if check_vi(word) or check_en(word):
            continue
        return False 
    return True

def run_check_vocab(csv_name="final_label_1ch_wordnum.csv"):
    with open(f'{csv_name[:-4]}_vocab.csv', 'w', encoding='utf8') as fp:
        print(f'file,text,duration', file=fp)
        pbar = tqdm.tqdm(open(csv_name).read().strip().split('\n')[1:])
        for line in pbar:
            path, text, duration = line.split(',')
            if not check_vocab(text):
                try:
                    col.insert_one({'path': path, 'text': text, 'duration': duration, 'error': 'vocab'})
                except:
                    pass 
                continue
            print(f'{path},{text},{duration}', file=fp)

def force_alignment_large_file(audio_path, transcript):
    url = "https://voicestreaming.cmccist.ai/force_alignment"

    payload={
        'transcript': transcript,
        'repeat_limit': '2'
        }
    files=[
        ('content',('11_1ch.wav',open(audio_path,'rb'),'audio/wav'))]
    headers = {
        'api_key': 'mtqijSUcj3hC96vWB6bsmqkgTud7y1tYQ4Tawa0R2V8OwShEAp8E3GEuCZ4F8Uo5'
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        response = response.json()
        return response.get("task_id")
    return None 

def force_alignment(audio_path, transcript):
    task_id = force_alignment_large_file(audio_path, transcript)
    if not task_id:
        return None
    url = "https://voicestreaming.cmccist.ai/get_result_force_alignment"

    payload={'task_id': task_id}
    headers = {}
    retry = 0
    while retry < 10: 
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200 and response.json().get("force_align_result"):
            return response.json()
        time.sleep(2)
        retry = retry + 1 
    return None 
    
def check_force_alignment(path, text, duration):
    """
    How it works:
    - Call API Force alignment

    """
    try:
        align_result = force_alignment(path, text)["force_align_result"]["list_align"]
        if align_result[0]["start"] >= 0.5 or (duration - align_result[-1]["end"] >= 0.5):
            return False
        return True
    except Exception as ex:
        print(ex)
    return False 

def run_force_aligment(csv_name="final_label_1ch_wordnum_vocab.csv"):
    with open(f'{csv_name[:-4]}_force_alignment.csv', 'w', encoding='utf8') as fp:
        print(f'file,text,duration', file=fp)
        pbar = tqdm.tqdm(open(csv_name).read().strip().split('\n')[1:])
        for line in pbar:
            path, text, duration = line.split(',')
            if not check_force_alignment(path, text, float(duration)):
                try:
                    col.insert_one({'path': path, 'text': text, 'duration': duration, 'error': 'force_alignment'})
                except:
                    pass 
                continue
            print(f'{path},{text},{duration}', file=fp)

def check_confidence(audio_path, threshold):
    response = speech_to_text(audio_path)
    confidence_scores = []
    for segment in response["metadata"]["segments"]:
        confidence_scores += [norm_word["confident_score"] for norm_word in segment["norm_words"]]
    confidence_score = sum(confidence_scores)/len(confidence_scores)
    if confidence_score > threshold:
        return True 
    return False

def filter_by_confidence(csv_name="final_label_1ch_wordnum_vocab_force_alignment.csv", threshold=0.65):
    with open(f'{csv_name[:-4]}_final.csv', 'w', encoding='utf8') as fp:
        print(f'file,text,duration', file=fp)
        pbar = tqdm.tqdm(open(csv_name).read().strip().split('\n')[1:])
        for line in pbar:
            path, text, duration = line.split(',')
            if not check_confidence(path, threshold):
                try:
                    col.insert_one({'path': path, 'text': text, 'duration': duration, 'error': 'confidence'})
                except:
                    pass 
                continue
            print(f'{path},{text},{duration}', file=fp)

if __name__ == '__main__':
    # 1. Chuyển đổi về 1 channel + 16khz
    convert_16khz()
    # 2. Chuyển số thành chữ số
    convert_num_to_wordnum()
    # 3. Kiểm tra trong câu có chứa từ không phải là tiếng anh hoặc tiếng việt không
    run_check_vocab()
    # 4. Force aligment để loại bỏ những audio bị thừa đầu, thừa đuôi
    run_force_aligment()
    # 5. Lọc những audio có confidence score thấp 
    filter_by_confidence()