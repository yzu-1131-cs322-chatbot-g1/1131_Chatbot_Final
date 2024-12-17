import os.path

from modules.config import config

import PIL.Image
import google.generativeai as genai

# Gemini API Settings
genai.configure(api_key=config["Gemini"]["API_KEY"])

llm_role_description = """
用戶跟你用甚麼語言，你就用甚麼語言來回答問題。
你是一個資深電影迷，你擅長回答關於電影的一切問題，
你也很會推薦電影給別人。
"""


# Use the model
from google.generativeai.types import HarmCategory, HarmBlockThreshold
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:HarmBlockThreshold.BLOCK_NONE,
    },
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    },
    system_instruction=llm_role_description,
)


def gemini_llm_sdk(user_input: str = None) -> str:
    try:
        response = model.generate_content(user_input)
        print(f"Question: {user_input}")
        print(f"Answer: {response.text}")
        return response.text
    except ValueError:
        return response.prompt_feedback
    except Exception as e:
        return str(e)


# user image path
user_image_path = os.path.normpath(config["Line"]["USER_IMAGE_PATH"])

movie_guess_prompt = """
請使用繁體中文回答。第一行是你的信心指數，介於0~1。第二行為你的猜測。如果你的信心指數低於0.5，則增加第三行為你的理由。
"""

movie_guess_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:HarmBlockThreshold.BLOCK_NONE,
    },
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    },
    system_instruction=movie_guess_prompt,
)


def guess_movie(uploaded_images, user_input: str = "你覺得圖片是哪部電影？") -> str:
    try:
        print("Image is uploaded.")
        print(f"Uploaded images: {uploaded_images}")
        upload_images = [PIL.Image.open(image_path) for image_path in uploaded_images]
        response = movie_guess_model.generate_content([user_input] + upload_images)
        response_text = response.text.splitlines()
        confidence_index = response_text[0]
        guessed_name = response_text[1]
        reason = response_text[2]
        print(f"Question: {user_input}")
        print(f"Answer: {response.text}")
        return response.text
    except Exception as e:
        print(e)
        return "Gemini AI故障中。"
