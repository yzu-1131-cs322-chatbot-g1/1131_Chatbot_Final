from modules.config import config
import google.generativeai as genai


# Gemini API Settings
genai.configure(api_key=config["Gemini"]["API_KEY"])


llm_role_description = """
妳是一位幼稚園老師，妳會用生活化的例子來回答問題。
妳的口頭禪是「好棒棒」，妳會用這個口頭禪來鼓勵學生。
使用繁體中文來回答問題。
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
    except Exception as e:
        print(e)
        return "皆麽奈夫人故障中。"


