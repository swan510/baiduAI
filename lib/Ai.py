import json,gc,binascii
import urequests
from machine import unique_id
from machine import I2S,Pin
import time


class BaiduVoice():
    def __init__(self,apiKey,sercretKey,dev_pid,dev_cuid,audiorate):
        self.apiKey = apiKey
        self.sercretKey = sercretKey
        self.dev_pid = dev_pid
        self.dev_cuid = dev_cuid
        self.audiorate = audiorate
# token获取
    def fetchToken(self):
        url=f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.apiKey}&client_secret={self.sercretKey}'
        payload = json.dumps("")
        headers = {
            'Content-Type':'application/json',
            'Accept': 'application/json'
        }
        response = urequests.request("POST",url,headers=headers,data=payload)
        return str(response.json().get("access_token"))
# 百度语音识别
    def speechRecongize(self,audiofile):
        _token = self.fetchToken()
        with open(audiofile,'rb') as f:
            speech_data = f.read()
        url = f'http://vop.baidu.com/pro_api?dev_pid={self.dev_pid}&cuid={self.dev_cuid}&token={_token}'
        headers = {
            'Content-Type': f'audio/pcm; rate={self.audiorate}'     
        }
        response = urequests.request("POST",url,data=speech_data,headers=headers)
        results = json.loads(response.text)
        if results["err_no"] != 0:
            raise ValueError(results["err_msg"],results["err_no"])
        elif results["err_msg"] == "success.":
            gc.collect()
            return results["result"][0]
# 百度语音合成 需要将文本进行url转码，text_urlencode储存转码后的文本
    def speechTTS(self,text):
        _token = self.fetchToken()
        text = binascii.hexlify(text).decode("utf-8") # 对文字进行转码
        text_urlencode = ''
        for i in range(0,len(text)):
            if i%2 == 0:
                text_urlencode += '%'
            text_urlencode += text[i]
        # tts_url 中的ctp,lan,spd,vol,per,aue参数数值可以根据API自己设置，aue最好是设置6 生成wav音频 
        tts_url = f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={_token}&cuid={self.dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111&aue=6'
        # max98357A io口设置
        i2s = I2S(1,sck=Pin(5),ws=Pin(6),sd=Pin(4),mode=I2S.TX,bits=16,format=I2S.MONO,rate=16000,ibuf=20000)
        response = urequests.get(tts_url,stream=True)
        response.raw.read(44)
        while True:
            try:
                content_byte = response.raw.read(1024)
                if len(content_byte) == 0:
                    time.sleep_ms(100)
                    break
                i2s.write(content_byte)
            except Exception as ret:
                print("产生的异常为",ret)
                i2s.deinit()
                break
        time.sleep_ms(100)
        i2s.deinit()              
# 文心一言使用
class BaiduAI():
    def __init__(self,apiKey,sercretKey):
        self.apiKey = apiKey
        self.sercretKey = sercretKey
    def aiTalk(self,text,_token):
        url = f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token={_token}'
        payload = json.dumps({
            "messages":[
                {
                    "role":"user",
                    "content":text
                }
            ]
        })
        headers = {
            'Content-Type':'application/json'
            }
        response = urequests.request("POST",url,headers=headers,data=payload.encode("utf-8"))
        results = json.loads(response.text)
        return results["result"]        
# deeoseek 使用,免费api获取申请地址:https://cloud.siliconflow.cn/models
class DeepseekAI():
    # 网址:https://siliconflow.cn/zh-cn/models
    def __init__(self,apiKey):
        self.apiKey = apiKey
    def deepseekTalk(self,text):
        url = "https://api.siliconflow.cn/v1/chat/completions"
        # deepseek-ai/DeepSeek-R1-Distill-Qwen-14B,deepseek-ai/DeepSeek-R1-Distill-Llama-8B
        payload = json.dumps({
            "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            "stream": False,
            "max_tokens": 512,
            "stop": ["null"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"},
    
        })
        headers = {
            "Authorization": f"Bearer {self.apiKey}",
            "Content-Type": "application/json"
        }
        response = urequests.request("POST",url,headers=headers,data=payload.encode("utf-8"))
        results = json.loads(response.text)
        print(results["choices"][0]["message"]["content"])
        return results["choices"][0]["message"]["content"]
    