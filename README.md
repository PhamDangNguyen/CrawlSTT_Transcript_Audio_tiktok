# Thu thập và xử lý dữ liệu từ TikTok 

## 1. Tổng quan 

Các bước thực hiện:
* Step 1: Download audio từ một kênh tiktok 

* Step 2: Cut các audio có transcript sau khi download 

* Step 3: Tiền xử lý dữ liệu audio sau khi cắt

### 1.1 Download audio 

* Input: chanel url và output_path (nơi lưu các audio của chanel sau khi download)
* Output: Các audio + transacript của channel 
* **Note:** Gặp vấn đề ở phần giải rotate captcha của tiktok 

### 1.2 Cut audio

* Input: Tên folder chứa các audio sau khi tải về 
* Output: Các audio nhỏ được cắt từ audio gốc và file *final_label.csv* lưu thông tin cắc subaudio sau khi cắt.
* Các bước: lấy ra các audio có transcript -> Merge các transcript gần nhau -> Cắt thành các audio nhỏ theo start và endtime 

### 1.3 Tiền xử lý dữ liệu 

![voice_preprocessing](https://github.com/BigdataCIST/Hadoop/assets/103992475/605fd6a6-d668-4f1b-be83-8a63be4a17a3)

Các bước thực hiện tiền xử lý dữ liệu:

* Step 1: Chuyển đổi audio về dạng 1 channel, 16khz và .wav
* Step 2: Chuyển đổ số thành chữ số, ví dụ "10" -> "mười"
* Step 3: Kiểm tra các từ trong transcript có nằm trong từ điển tiếng anh hoặc tiếng việt không, nếu không thì bỏ qua audio đó
* Step 4: Chạy force alignment để loại bỏ các audio bị thừa đầu hoặc đuôi
* Step 5: Lọc bỏ các audio có confidence score thấp hơn ngưỡng 0.65


## 2. Chạy chương trình:

### 2.1 Cài đặt môi trường và các tool liên quan

* Cài đặt môi trường và thư viện
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -U webdriver_manager

```

* Cài đặt [yt-dlp](https://github.com/yt-dlp/yt-dlp/) để download audio + transcript trên tiktok 

* Cài đặt [ffmpeg](https://hocdevops.com/os/cai-dat-va-su-dung-ffmpeg-tren-ubuntu-20-04/) để xử lý audio

### 2.2 Chạy chương trình


* Chạy toàn bộ pipeline 
```
python main.py
```

Hoặc: 

* Download audio từ một kênh tiktok
```
python scraper/tiktok_scraper.py
```

* Cut audio sau khi download về 
```
python process/process.py
```

* Tiền xử lý dữ liệu sau khi cut 
```
python preprocessing/utils.py
```
