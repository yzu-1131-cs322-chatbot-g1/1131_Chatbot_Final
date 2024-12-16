import requests
import configparser
import os
from datetime import datetime
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

class MovieSearch:
    def __init__(self, config_path=None):
        """
        初始化 MovieSearch 類別
       
        :param config_path: config.ini 檔案路徑
        """
        # 如果沒有指定路徑，使用預設路徑
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
       
        # 使用 UTF-8 編碼讀取配置文件
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
       
        # 確保成功讀取 API key
        try:
            self.tmdb_api_key = config['TMDB']['API_KEY']
            self.azure_key = config['AzureTranslator']['Key']
            self.azure_region = config['AzureTranslator']['Region']
            self.azure_endpoint = config['AzureTranslator']['Endpoint']
        except KeyError as e:
            raise ValueError(f"未在 config.ini 中找到 {str(e)} 配置")
       
        self.base_url = "https://api.themoviedb.org/3/movie/popular?language=zh-TW'"
        
        # 初始化 Azure 翻譯客戶端
        try:
            # 使用新的初始化方式
            self.translator = TextTranslationClient(
                credential = AzureKeyCredential(self.azure_key),
                endpoint = self.azure_endpoint,
                region = self.azure_region
            )
        except Exception as e:
            print(f"Azure 翻譯客戶端初始化錯誤: {e}")
            self.translator = None

    def _translate_text(self, text, target_language='zh-Hant'):
        """
        使用 Azure 翻譯文本
        :param text: 要翻譯的文本
        :param target_language: 目標語言代碼
        :return: 翻譯後的文本
        """ 
        if not self.translator:
            print("Azure 翻譯器未初始化")
            return text

        try:
            # 翻譯
            response = self.translator.translate(
                body = [text], 
                to_language = [target_language]
            )
            print(response)
            # 返回第一個翻譯結果
            if response and response[0].translations:
                return response[0].translations[0].text
            else:
                print("未找到翻譯結果")
                return text
        except Exception as e:
            print(f"翻譯失敗: {e}")
            return text

    def _convert_date(self, date_str):
        """將日期轉換為更友好的中文格式"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return f"{date_obj.year}年"
        except:
            return date_str

    def search_movie(self, movie_name):
        """
        搜尋電影並獲取詳細資訊
        :param movie_name: 電影名稱
        :return: 電影詳細資訊字典
        """
        try:
            # 第一步：搜尋電影
            search_url = f"{self.base_url}/search/movie?api_key={self.tmdb_api_key}&query={movie_name}"
            search_response = requests.get(search_url)
            if search_response.status_code != 200:
                return f"搜尋電影時發生錯誤：{search_response.status_code}"
            search_data = search_response.json()
           
            # 如果沒有找到電影
            if not search_data['results']:
                return "找不到相關電影"
            
            # 取第一個搜尋結果的電影 ID
            movie_id = search_data['results'][0]['id']
            
            # 第二步：獲取電影詳細資訊
            details_url = f"{self.base_url}/movie/{movie_id}?api_key={self.tmdb_api_key}&append_to_response=credits,release_dates"
            details_response = requests.get(details_url)
            if details_response.status_code != 200:
                return f"獲取電影詳細資訊時發生錯誤：{details_response.status_code}"
            movie_details = details_response.json()
            
            # 翻譯電影名稱
            translated_title = self._translate_text(movie_details['title'])
            
            # 翻譯劇情簡介
            translated_overview = self._translate_text(movie_details['overview'])
            
            # 提取導演
            directors = [crew['name'] for crew in movie_details.get('credits', {}).get('crew', [])
                         if crew['job'] == 'Director']
            director = self._translate_text(directors[0]) if directors else "無資訊"
            
            # 提取主演並翻譯
            actors = [actor['name'] for actor in movie_details.get('credits', {}).get('cast', [])[:3]]
            translated_actors = [self._translate_text(actor) for actor in actors]
            main_actors = "、".join(translated_actors) if translated_actors else "無資訊"
            
            # 取得上映年份的中文格式
            release_date = datetime.strptime(movie_details['release_date'], "%Y-%m-%d")
            formatted_release_date = release_date.strftime("%Y年%m月%d日")
            
            # 格式化回覆訊息
            message = f"""🎬 電影名稱: {translated_title}
⭐ 電影評分: {movie_details['vote_average']}/10
📅 上映年份: {formatted_release_date}
👥 導演: {director}
🌟 主演: {main_actors}

📝 劇情簡介: 
{translated_overview}

📊 電影評價:
總投票數: {movie_details['vote_count']} 票
"""
            return message
       
        except Exception as e:
            return f"搜尋電影時發生未預期的錯誤：{str(e)}"

def search_movie_command(movie_name):
    '''
    用於 Line Bot 的電影搜尋命令處理函數
   
    :param movie_name: 電影名稱
    :return: 電影資訊訊息
    '''
    movie_searcher = MovieSearch()
    return movie_searcher.search_movie(movie_name)