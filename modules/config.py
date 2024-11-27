import configparser

# 全域唯一字典
config = {}

def load_config(file_path="config.ini"):
    """
    讀取 config.ini 並將資料存入全域字典 config
    """
    print(f'Loading config from {file_path}')

    global config
    parser = configparser.ConfigParser()
    parser.read(file_path, encoding="utf-8")

    for section in parser.sections():
        config[section] = {key: parser[section][key] for key in parser[section]}

# 初始化配置
load_config()
