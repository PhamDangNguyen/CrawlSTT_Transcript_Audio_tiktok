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
    captions = webvtt.read(path + '/' + 'transcript.vie-VN.vtt')
    dicts = []
    dicts_filename_only = []
    prev_line = None
    index = 0
    print(captions)
    for c in captions:
        if any("<c>" in l for l in c.lines):
            
            continue
        # Collect lines that are not dupes
        not_dupe_lines = []
        for line in c.lines:
            if not line.strip():
                continue
            if line != prev_line:
                not_dupe_lines.append(line)
            prev_line = line
        if not_dupe_lines:
            dicts.append({"start": convert_vtt_time_to_second(c.start), "end": convert_vtt_time_to_second(c.end), 
            "duration": convert_vtt_time_to_second(c.end) - convert_vtt_time_to_second(c.start),
            "text": not_dupe_lines, "file_name" : f'{index}.wav'})
            dicts_filename_only.append({"text": not_dupe_lines, "file_name" : f'{index}.wav'})
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
        f = open(f"{path}/transcript.json")
        data = json.load(f)
        dicts = []
        cur_start = 0.0
        cur_end = 0.0
        cur_label = ""
        cur_file_name = None

        i = 0
        while i < len(data)-1:
            
            if data[i+1]['start'] - data[i]['end'] < 0.03:
                print(i)
                temp = i + 1
                for j in range(i+1, len(data)-1):
                    if data[j+1]['start'] - data[j]['end'] < 0.03:
                        print(data[j]['end'],data[j+1]['start'])
                        temp = j+1
                    else:
                        break
                
                # cur_label = [data[temp-1]['text'][0] + " " +data[temp]['text'][0]]
                cur_start = data[i]['start']
                cur_end = data[temp]['end']
                cur_file_name = data[temp]['file_name']
                k = i
                while k < temp + 1:
                    cur_label = cur_label + " " + data[k]['text'][0]
                    k = k + 1
                # for k in range(i,temp):    
                #     cur_label = cur_label + " " + data[k]['text'][0] + " " +data[k+1]['text'][0]
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

        with open(f"./{path}/final_transcript.json", 'w', encoding='utf8') as json_file:
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
    video_id = get_video_id(path)
    with open('final_label.csv', mode='a',newline = "") as f:
        csv_writer = csv.writer(f)
        all_data = []
        final_transcript_path = f"{path}/final_transcript.json"
        if os.path.exists(final_transcript_path):
            data = json.load(open(final_transcript_path))
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
    category_path = 'audio_test'
    run(category_path)