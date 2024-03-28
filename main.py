import os
# from scraper import TiktokScraper
from process import audio_cut
from preprocessing.utils import convert_16khz, convert_num_to_wordnum, run_check_vocab, run_force_aligment,filter_by_confidence

# Step 1: Download audio from tiktok channel
output_path='audio_mien_trung'
# tiktok_scraper = TiktokScraper(headless=False)
# tiktok_scraper.download_audio_from_channel(channel_url="https://www.tiktok.com/@goctamsu20_", output_path=output_path)
# tiktok_scraper.driver.quit()

# Step 2: Cut audio
audio_cut.run(output_path)

# # Step 3: Preprocessing 
# if not os.path.exists('logs'):
#     os.makedirs('logs')
# ## 3.1. Chuyển đổi về 1 channel + 16khz
# convert_16khz()
# os.rename("final_label.csv", "logs/final_label.csv")
# ## 3.2. Chuyển số thành chữ số
# convert_num_to_wordnum()
# os.rename("final_label_1ch.csv", "logs/final_label_1ch.csv")
# ## 3.3. Kiểm tra trong câu có chứa từ không phải là tiếng anh hoặc tiếng việt không
# run_check_vocab()
# os.rename("final_label_1ch_wordnum.csv", "logs/final_label_1ch_wordnum.csv")
# ## 3.4. Force aligment để loại bỏ những audio bị thừa đầu, thừa đuôi
# run_force_aligment()
# os.rename("final_label_1ch_wordnum_vocab.csv", "logs/final_label_1ch_wordnum_vocab.csv")
# ## 3.5. Lọc những audio có confidence score thấp 
# filter_by_confidence()
# os.rename("final_label_1ch_wordnum_vocab_force_alignment.csv", "logs/final_label_1ch_wordnum_vocab_force_alignment.csv")