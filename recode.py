from machine import I2S,SPI
from machine import Pin
import os
import uos
import time
class Soundrecode():
    def __init__(self,sampleRate,bitsPerSample,num_channels,datasize):
        self.sampleRate = sampleRate
        self.bitsPerSample = bitsPerSample
        self.num_channels = num_channels
        self.datasize = datasize
        self.sck_pin_inmp441 = Pin(17)
        self.ws_pin_inmp441 = Pin(15)
        self.sd_pin_inmp441 = Pin(16)
    def createWavHeader(self):    
        o = bytes("RIFF",'ascii')                                                                  # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(4,'little')                                                  # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE",'ascii')                                                                 # (4byte) File type
        o += bytes("fmt ",'ascii')                                                                 # (4byte) Format Chunk Marker
        o += (16).to_bytes(4,'little')                                                             # (4byte) Length of above format data
        o += (1).to_bytes(2,'little')                                                              # (2byte) Format type (1 - PCM)
        o += (self.num_channels).to_bytes(2,'little')                                              # (2byte)
        o += (self.sampleRate).to_bytes(4,'little')                                                # (4byte)
        o += (self.sampleRate * self.num_channels * self.bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
        o += (self.num_channels * self.bitsPerSample // 8).to_bytes(2,'little')                    # (2byte)
        o += (self.bitsPerSample).to_bytes(2,'little')                                             # (2byte)
        o += bytes("data",'ascii')                                                                 # (4byte) Data Chunk Marker
        o += (self.datasize).to_bytes(4,'little')                                                  # (4byte) Data size in bytes
        return o
    def beginRecode(self,sfile,bufSize,recodeTime):
        # bufSize = 32768
        aduioInI2S = I2S(0,sck = self.sck_pin_inmp441,ws = self.ws_pin_inmp441,sd = self.sd_pin_inmp441,
                         mode = I2S.RX,
                         bits = self.bitsPerSample,
                         format = I2S.STEREO,
                         rate = self.sampleRate,
                         ibuf = bufSize)
        # 音频数据读取缓存
        readBuf = bytearray(bufSize)
        print("read recode")
        time.sleep(1)
        if sfile in uos.listdir():
            print("del",sfile)
            uos.remove(sfile)
            time.sleep_ms(200)
        fin = open(sfile,'wb')
        startTime = time.time()
        head = self.createWavHeader()
        fin.write(head)
        print("start recode")
        while f:
            currByteCount = audioInI2S.readinto(readBuf)
            print('in ', len(readBuf))
            audio_data = bytearray()
            audio_data.extend(readBuf)
            fin.write(audio_data)
            # 检查是否到达文件时长
            if time.time() - start_time >= recodeTime:
                f = False   
        fin.close()
        print("recode end")
class  Soundplay():
    def __init__(self,sflie,sampleyRate,bitPerSample):
        self.audio_out = I2S(1,sck = Pin(5),ws = Pin(6),sd = Pin(4),
                             mode = I2S.TX,bits = bitPerSample,format = I2S.STEREO,
                             rate = sampleRate, ibuf = 2000)
        self.sfile = sfile
    def beginPlay(self):
        f = open(self.sfile,'rb')
        pos = f.seek(44) 
        wav_samples = bytearray(1024)
        wav_samples_mv = memoryview(wav_samples)
        print("start play")
        while True:
            try:
                num_read = f.readinto(wav_samples_mv)
                # WAV文件结束
                if num_read == 0: 
                    break
                # 直到所有样本都写入I2S外围设备
                num_written = 0
                while num_written < num_read:
                    num_written += audio_out.write(wav_samples_mv[num_written:num_read])    
            except Exception as ret:
                print("产生异常...", ret)
                break
        print("play end")

