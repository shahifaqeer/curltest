import subprocess
from classes import Router

def download(proxy=1, file_zize='10M', run_num=0):
    outfile = "curl-proxy_"+str(proxy)+"-file_"+file_zize+"-run_"+str(run_num)+".log"
    cmd = "curl 192.168.20.1:8055/test" + file_zize + ".gz -o /dev/null --stderr /home/gtnoise/test/"+outfile
    if proxy == 1:
        cmd += " -x http://192.168.1.1:3128"
    # BLOCKING CMD
    subprocess.check_output(cmd, shell=True)
    return 0

if __name__=="__main__":
    #for run_num in range(50):
    #    for file_size in ['10M', '2M', '500K']:
    #        for proxy in [0, 1]:
    #            download(proxy, file_size, run_num)
    R = Router('192.168.10.1', 'root', 'passw0rd', 'R')
    Q = Router('10.0.1.1', 'root', 'passw0rd', 'Q')
    download(1, '2M', 0)
    download(0, '2M', 0)
