# 1131_Chatbot_Final

## 待辦清單

https://github.com/orgs/yzu-1131-cs322-chatbot-g1/projects/7

上面有需要做的事情，可以去認領，也可以看已經做好的東西。

記得先設定 Assignee 再設定認領狀態。

## 準備工作

### requirements.txt

```cmd
pip install -r requirements.txt
```

### config.ini

由於 config.ini 裡面會放如 `API_KEY` 等不建議公開到網路上的資訊，所以 config.ini 被加入到 .gitignore 中，不會被 git 版本控制。
但也因為這樣，儲存庫上不會有 config.ini，執行前需手動新增 config.ini 在與 app.py 同一層的位置，並填入以下內容：

```ini
# (若有修改麻煩更新此處)
[test]
message = Test World :wink:

[Line]
CHANNEL_ACCESS_TOKEN=替換成你的
CHANNEL_SECRET=替換成你的

[Gemini]
API_KEY=替換成你的

[AzureTranslator]
Key=替換成你的
Region=替換成你的
EndPoint=https://api.cognitive.microsofttranslator.com/
```

## 開發

### modules
可以把獨立的功能寫成模組，放在 modules 資料夾中，降低 app.py 的複雜度。

用法：
```python
from modules import ModuleName
```
```python
from modules.ModuleName import ClassName, VariableName, FunctionName
```
例如：
```python
from modules.config import config
```

### commit
- commit 的頻率會影響協作效率，太頻繁會讓歷史紀錄變得雜亂、間隔太長會讓版本回溯變得困難。

- 基本原則是每個 commit 都是一個獨立的功能，可以單獨運作，不會影響其他功能。

- push 前可以先 pull，確保沒有 conflict 或解決後再 push。
