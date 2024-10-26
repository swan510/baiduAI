from machine import I2S,SPI,Pin
from machine import UART
import gc
import os
import uos
import time
import random
from baiduAI import *
from wifi_connect import do_connect


button = Pin(0)
uart0 = UART(1,baudrate=9600,tx=12,rx=13)
sampleRate = 8000
bitsPerSample = 16
bufSize = 32768
num_channels = 2
# 连接端口:3.3V SD->17  WS->16 SCK->15  L/R-> GND
#I2S所需管脚，按自己需要的接入即可
sck_pin = Pin(15) #数据时钟(INMP441模块SCK)
ws_pin = Pin(16)  #帧时钟(INMP441模块模块WS)
sd_pin = Pin(17)  #数据(INMP441模块模块SD)
file_duration = 5 # 文件时长（秒)

def createWavHeader(sampleRate, bitsPerSample, num_channels, datasize):    
    o = bytes("RIFF",'ascii')                                                   # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                                   # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                                  # (4byte) File type
    o += bytes("fmt ",'ascii')                                                  # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                              # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                               # (2byte) Format type (1 - PCM)
    o += (num_channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                      # (4byte)
    o += (sampleRate * num_channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (num_channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                                   # (2byte)
    o += bytes("data",'ascii')                                                  # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                        # (4byte) Data size in bytes
    return o


do_connect()
answertext = ['宝贝儿，我在呢','帅哥，干啥','有啥想问的','宝贝儿，想好了再问']

while True:
    uartread = uart0.read()
    time.sleep_ms(100)
    if uartread:
        print(uartread)
        if uartread == b'HELLO\r\n':
            print('我在呢')
            speech_tts(apikey,sercretkey,answertext[random.randint(0,3)])
            #创建音频对象，开始录音
            audioInI2S = I2S(0,
                 sck=sck_pin, ws=ws_pin, sd=sd_pin,
                 mode=I2S.RX,
                 bits=bitsPerSample,
                 format=I2S.STEREO,
                 rate=sampleRate,
                 ibuf=bufSize)
            readBuf = bytearray(bufSize) #音频数据读取缓冲
            recoder = True
            start_time = time.time()
            sfile = 's.pcm'        
            # 检查文件是否存在
            if sfile in uos.listdir():
                # 删除文件
                print('del', sfile)
                uos.remove(sfile)
                time.sleep(0.5)
            fin = open(sfile, 'wb')
            head = createWavHeader(sampleRate, bitsPerSample, num_channels, bufSize*file_duration)
            fin.write(head)
            print('in start')
            while recoder:
                # 读取音频数据
                currByteCount = audioInI2S.readinto(readBuf)
                print('in ', len(readBuf))        
                audio_data = bytearray()
                audio_data.extend(readBuf)
                fin.write(audio_data)
                # 检查是否到达文件时长
                if time.time() - start_time >= file_duration:
                    recoder = False
            fin.close()
            print('in end')
            print('ready recongize')
            text = recongize(sfile,dev_pid=80001) #百度语音识别
            print(text)
            ai_text = ai_recongize(Aiapikey,Aisercretkey,text) #文心一言对话
            print(ai_text)
            speech_tts(apikey,sercretkey,ai_text) #百度语音合成
