import socket
import os




def html_sever(server_ip,port):
    """用来完成整体的控制"""
    # 1. 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置当服务器先close 即服务器端4次挥手之后资源能够立即释放，这样就保证了，下次运行程序时 可以立即绑定7890端口
    # tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 2. 绑定
    try:
        tcp_server_socket.bind((server_ip, int(port))) #
    except OSError:
        tcp_server_socket.bind(("localhost", int(port)))  #

    # 3. 变为监听套接字
    tcp_server_socket.listen(128)

    # service_client(new_socket, send_info)
    ip_dict={}

    while True:
        # 4. 等待新客户端的链接

        new_socket, client_addr = tcp_server_socket.accept()
        # print("get new client")
        message = str(new_socket.recv(4096), 'utf-8')
        if message[0:2]=="ip":
            """
            ip:192.168.255.6, id:0, GPU:   0  GeForce RTX 207... WDDM  , MemoryInfo:2.85 GB/8.00 GB, MemoryUsage:30%
            """
            ip_key=message.split(",")[0].split(":")[-1]
            ip_dict[ip_key]=message

        method = message.split(' ')[0]
        if method =="GET":
            #send the str to
            strs=""
            for key_ in ip_dict.keys():
                strs+=ip_dict[key_]+"\n"

            # print("strs:",strs)

            response = "HTTP/1.1 200 OK\r\n"
            response += "\r\n"
            new_socket.send((response+strs).encode("utf-8"))


        new_socket.close()

    # 关闭监听套接字
    tcp_server_socket.close()


def open_address_txt(txt_file):
    if os.path.isfile(txt_file):
        with open(txt_file,"r") as f:
            lines=f.readlines()
            server_ip, port=lines[0].strip("\n").split(" ")
        return server_ip,port
    else:
        return 0,0


if __name__=="__main__":
    server_ip, port=open_address_txt("./server_address.txt")

    print(
        "check the GPU info -> server ip:port={}:{}".format(server_ip,port)
    )

    html_sever(server_ip, port)
