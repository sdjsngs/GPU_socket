import re
import time
import subprocess
import os
import socket

def get_info():

    info = { 'gpu': []}

    msg = subprocess.Popen(['nvidia-smi'], stdout = subprocess.PIPE).stdout.read().decode(errors='ignore')
    msg = msg.strip().split('\n')

    lino = 8
    while True:
        status = re.findall('(\d+)MiB / +(\d+)MiB.* +(\d+)%.*', msg[lino])
        if status == []: break
        mem_usage, mem_total,percentage = status[0]
        gpu_name=msg[lino-1].split("|")[1]

        info['gpu'].append({
            "gpu_name": gpu_name,
            "memory_used":"{:.2f} GB".format(float(mem_usage)/1024.0),
            'total_memory': "{:.2f} GB".format(float(mem_total)/1024.0),
            "memory_usage":str(percentage)+"%",
        })
        lino += 3

    return info


def load_local_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    return local_ip


def open_address_txt(txt_file):
    if os.path.isfile(txt_file):
        with open(txt_file,"r") as f:
            lines=f.readlines()
            server_ip, port=lines[0].strip("\n").split(" ")
        return server_ip,port
    else:
        return 0,0


def html_send(server_ip,port,send_info):
    """用来完成整体的控制"""
    # 1. 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置当服务器先close 即服务器端4次挥手之后资源能够立即释放，这样就保证了，下次运行程序时 可以立即绑定7890端口
    # tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    tcp_server_socket.connect((server_ip, int(port)))

    tcp_server_socket.send(
        send_info.encode()
    )

    # 关闭监听套接字
    tcp_server_socket.close()


if __name__=="__main__":

    server_ip, port=open_address_txt("./server_address.txt")


    print("check the GOU info -> server ip:port={}:{}".format(server_ip,port))
    local_ip=load_local_ip()
    print("local_ip:",local_ip)
    # load gpu infor and send to server_ip:port
    mean_info = get_info()
    send_infos = ""
    for step in range(len(mean_info["gpu"])):
        send_info = "ip:{},id:{},GPU:{},MemoryInfo:{}/{},MemoryUsage:{}\n".format(
            local_ip, step, mean_info["gpu"][step]["gpu_name"], mean_info["gpu"][step]["memory_used"],
            mean_info["gpu"][step]["total_memory"],
            mean_info["gpu"][step]["memory_usage"],
        )

        send_infos += send_info
    print("GPU info for this PC",send_infos)


    while True:
        # load gpu infor and send to server_ip:port
        mean_info = get_info()
        send_infos=""
        for step in range(len(mean_info["gpu"])):


            send_info="ip:{},id:{},GPU:{},MemoryInfo:{}/{},MemoryUsage:{}\n".format(
                local_ip,step,mean_info["gpu"][step]["gpu_name"],mean_info["gpu"][step]["memory_used"],mean_info["gpu"][step]["total_memory"],
                mean_info["gpu"][step]["memory_usage"],
            )

            send_infos+=send_info
        html_send(
            server_ip,port,send_infos
        )

        time.sleep(120)
