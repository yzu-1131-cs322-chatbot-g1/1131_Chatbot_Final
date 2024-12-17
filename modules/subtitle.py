import auto_subtitle 

# 假設 generate_subtitle 函數接受一個影片檔案路徑並返回字幕
video_path = "uploads\video.mp4"
subtitle = auto_subtitle.generate_subtitle(video_path)

# 將生成的字幕輸出到檔案
with open("output.srt", "w") as subtitle_file:
    subtitle_file.write(subtitle)