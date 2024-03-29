import os 
from glob import glob 
import webvtt
import soundfile as sf
import json 
import csv

def convert_vtt_time_to_second(time_vtt, minus_time=False):
    hour, minutes, second = time_vtt.split(":")
    minus_total_time = 0.3 if minus_time else 0
    return max(float(hour) * 3600 + float(minutes) * 60 + float(second) - minus_total_time, 0.0)

def get_video_id(path):
    return path.split('/')[-1]

def has_transcript(folder_path):
    for path in glob(f'{folder_path}/*.vtt'):
        return path 
    return None 

def get_transcript(path):
    # print(path + '/' + 'transcript.vie-VN.vtt')
    captions = webvtt.read(path + '/' + 'transcript.vie-VN.vtt')#captions[0] = 00:00:01.018 00:00:03.701 mà chúng ta sợ hãi khi mà phát biểu trước đám đông
    dicts = []
    dicts_filename_only = []
    prev_line = None
    index = 0
    # print(captions)
    for c in captions:
        # print(c.start,c.end)# lay start va end time
        if any("<c>" in l for l in c.lines):
            print("co <c> trong phan tu roi")
            continue
        # Collect lines that are not dupes
        not_dupe_lines = []
        for line in c.lines:
            # print(line)
            if not line.strip():
                continue
            if line == prev_line: #check trung lap
                break
            else:
                prev_line = line
            not_dupe_lines.append(line)
        if not_dupe_lines:
            dicts.append({"start": convert_vtt_time_to_second(c.start), "end": convert_vtt_time_to_second(c.end), 
            "duration": convert_vtt_time_to_second(c.end) - convert_vtt_time_to_second(c.start),
            "text": not_dupe_lines, "file_name" : f'{index}.wav'})
            dicts_filename_only.append({"text": not_dupe_lines, "file_name" : f'{index}.wav'})
            # print(dicts)
        index = index + 1
    with open(path + '/' + "/transcript.json", 'w', encoding='utf8') as json_file:
        json.dump(dicts, json_file, ensure_ascii=False, indent=3)
    with open(path + '/' + "/transcript_sub.json", 'w', encoding='utf8') as json_file:
        json.dump(dicts_filename_only, json_file, ensure_ascii=False, indent=3)

def merge_transcript(path):
    """Gộp transcript quá gần nhau

    Args:
        video_id(str): ID of tiktok video
    """
    transcript_path = f"{path}/transcript.json"
    if os.path.exists(transcript_path):
        f = open(f"{path}/transcript.json", encoding='utf8')
        data = json.load(f)
        print(data[0])#dict
        dicts = []
        cur_start = 0.0
        cur_end = 0.0
        cur_label = ""
        cur_file_name = None
        i = 0
        print(len(data))
        while i < len(data)-1:#merge 2 transcrip cach nhau 0.03
            # print(data[i])
            if data[i+1]['start'] - data[i]['end'] < 0.02:
                temp = None
                #Check xem co bao nhieu file lien nhau lien tiep tinh tu file i
                for j in range(i, len(data)-1):# check data[i+1] gan data[i+1] (if no break) (if yes => data[i+3] co gan data[i+2] khong,...)
                    if data[j+1]['start'] - data[j]['end'] < 0.02:
                        # print(data[j]['end'],"----------------------",data[j+1]['start'],data[j+1]['text'])
                        temp = j+1 #gop vao => i tang 1
                    else:
                        break
                # print(temp-i)
        
                cur_start = data[i]['start']
                cur_end = data[temp]['end']
                cur_file_name = data[temp]['file_name']
                cur_label = data[i]['text'][0]
                k = i+1
                
                while k < temp + 1: #merg transcript cac file gan nhau lien tiep
                    # print(cur_label)
                    # print(data[k]['text'][0])
                    cur_label = cur_label + " " + data[k]['text'][0]
                    k = k + 1
                    
                print(cur_label)
                cur_label = [cur_label]
                
                dicts.append({"start": cur_start, "end": cur_end, 
                    "duration": cur_end - cur_start,"text": cur_label, "file_name" : cur_file_name})
                i = temp+1

                cur_start = 0.0
                cur_end = 0.0
                cur_label = ""
                cur_file_name = None
            else:
                dicts.append({"start": data[i]['start'], "end": data[i]['end'], 
                    "duration": data[i]['duration'],"text": data[i]['text'], "file_name" : data[i]['file_name']})
                i = i+1

        if i == len(data) - 1:
            dicts.append({"start": data[i]['start'], "end": data[i]['end'], 
                    "duration": data[i]['duration'],"text": data[i]['text'], "file_name" : data[i]['file_name']})
            
        path_save = f"{path}/final_transcript.json"
        # print(path_save)
        with open(path_save, 'w', encoding='utf8') as json_file:
            json.dump(dicts, json_file, ensure_ascii=False, indent=3)

def cut_audio_align(filename, start, end, save_name):
    data, samplerate = sf.read(filename)
    basename = os.path.splitext(os.path.basename(filename))[0]
    start_cut = int(start * 16000)
    end_cut = int(end * 16000)
    data_cut = data[start_cut:end_cut]
    save_path = f"audio_cut/{basename}"
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)
        print(f"Create {save_path} successfully!!!!!")
    sf.write(save_path + "/"+save_name, data_cut, samplerate)

def cut_audio(path):
    '''
        This function allows you to cut a long audio file into multiple short audio files 

        Args:
        video_id: ID of video
    '''
    path = path.replace('\\', '/')
    video_id = get_video_id(path)
    print(video_id)# path tuong doi: audio_mien_trung\chu0t_ga0\7297043504126102786

    with open('final_label.csv', mode='a',newline = "",encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        all_data = []
        final_transcript_path = f"{path}/final_transcript.json"
        if os.path.exists(final_transcript_path):
            data = json.load(open(final_transcript_path,mode='r',encoding='utf-8'))
            index = 0
            for audio in data:
                list_time = []
                label = None
                duration = 0.0
                for attribute, value in audio.items():
                    if attribute == "text":
                        label = value
                    if attribute == "duration":
                        duration = value
                    if (attribute == "start" or attribute == "end"):
                        list_time.append(value)
                label = label[0].lower().strip()
                audio_path = f"{path}/{video_id}.wav"
                print(audio_path)
                audio_save_name = f'{index}.wav'
                all_data.append([os.path.join(f"audio_cut/{video_id}", audio_save_name), label, duration])
                cut_audio_align(audio_path, list_time[0], list_time[1], audio_save_name)
                index = index + 1
        csv_writer.writerows(all_data)

def run(category_path):
    for chanel_path in glob(f'{category_path}/*'):
        for video_folder in glob(f'{chanel_path}/*'):
            if has_transcript(video_folder):
                try:
                    get_transcript(video_folder)
                    merge_transcript(video_folder)
                    cut_audio(video_folder)
                except Exception as ex:
                    print(ex)
                    continue

if __name__ == '__main__':
    path='C:/Users/Superman/Desktop/Check_tool/Tiktok_STT/CrawlSTT_Transcript_Audio_tiktok/audio_mien_trung'
    run(path)