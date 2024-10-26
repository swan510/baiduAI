import json,gc,binascii
import urequests
from machine import unique_id
from machine import I2S,Pin
import time
audiorate = 16000
dev_cuid = binascii.hexlify(unique_id()).decode("utg-8")
print(dev_cuid)

#语音识别与语音合成apikey和sercretkey，填入你自己的
apikey = ''
sercretkey = ''
#百度人工智能apikey和sercretkey，填入你自己的
Aiapikey = ''
Aisercretkey = ''

#获取token
def fetch_token(API_Key,Secret_Key):
    url=f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}'
    payload = json.dumps("")
    headers = {
        'Content-Type':'application/json',
        'Accept': 'application/json'
    }
    response = urequests.request("POST",url,headers=headers,data=payload)
    return str(response.json().get("access_token"))
#语音识别，极速段语音识别 dev_pid必须是80001
def recongize(audiofile,dev_pid=80001):
    with open(audiofile,'rb') as f:
        speech_data = f.read()
    _token = fetch_token(apikey,sercretkey)
    url = f'http://vop.baidu.com/pro_api?dev_pid={dev_pid}&cuid={dev_cuid}&token={_token}'  
    headers = {
        'Content-Type': f'audio/pcm; rate={audiorate}'     
        }
    response = urequests.request("POST",url,data=speech_data,headers=headers)
    results = json.loads(response.text)
    if results["err_no"] != 0:
        raise ValueError(results["err_msg"],results["err_no"])
    elif results["err_msg"] == "success.":
        gc.collect()
        return results["result"][0]
#百度文心一言识别对话
def ai_recongize(apikey,sercretkey,text):
    ai_token = fetch_token(apikey,sercretkey)
    url = f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token={ai_token}'
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
#百度语音合成播报
def speech_tts(API_Key,Secret_Key,text_tts):
    _token = fetch_token(apikey,sercretkey)
    text = binascii.hexlify(text_tts).decode("utf-8") # 对文字进行转码
    text_urlencode = ''
    for i in range(0,len(text)):
        if i%2 == 0:
            text_urlencode += '%'
        text_urlencode += text[i]
    tts_url = f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={_token}&cuid={dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111&aue=6'
    #创建音频对象，max85357A
    i2s = I2S(1,sck=Pin(5),ws=Pin(14),sd=Pin(11),mode=I2S.TX,bits=16,format=I2S.MONO,rate=16000,ibuf=20000)
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


