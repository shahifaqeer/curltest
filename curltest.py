import subprocess
from classes import Router
import time


def download(proxy=1, file_zize='10M', run_num=0, rate='', delay=''):
    outfile = "curl-proxy_"+str(proxy)+"-file_"+file_zize+"-rate_"+rate+"-delay_"+delay+"-run_"+str(run_num)+".log"
    cmd = "curl 10.0.0.1:8055/test" + file_zize + ".gz -o /dev/null --stderr /home/gtnoise/test/"+outfile
    if proxy == 1:
        cmd += " -x http://10.0.2.1:3128"
    # BLOCKING CMD
    subprocess.check_output(cmd, shell=True)
    return 0

def set_rate_delay(Q, rate, delay):

    rate_bits = str(rate)
    delay_ms = str(delay)

    Q.remoteCommand('tc qdisc del dev br-lan root;tc qdisc add dev br-lan root netem delay 40ms;tc qdisc show dev br-lan')

    if rate != 0:
        Q.remoteCommand('sh ratelimit4.sh eth0 '+rate_bits+' '+delay_ms)
        Q.remoteCommand('sh ratelimit4.sh eth1 '+rate_bits+' '+delay_ms)
    else:
        Q.remoteCommand('tc qdisc del dev eth0 root')
        Q.remoteCommand('tc qdisc del dev eth1 root')
        if delay > 0:
            Q.remoteCommand('tc qdisc add dev br-lan root netem delay' +delay_ms+ 'ms')
        else:
            Q.remoteCommand('tc qdisc del dev br-lan root')
    return 0

def test_all_combos(Q):
    for file_size in ['10M', '2M', '500K']:
        for run_num in range(50):
            for delay in [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                set_rate_delay(Q, 0, delay)
                time.sleep(0.1)
                print "DONE delay "+str(delay)+ " Run number "+str(run_num)+" file_size " + file_size
                for proxy in [0, 1]:
                    download(proxy, file_size, run_num, '0', str(delay))
        time.sleep(1)
    return


def quick_test(Q):
    file_size = '10M'
    for run_num in range(5):
        for delay in [1, 10, 30, 100]:
            set_rate_delay(Q, 0, delay)
            time.sleep(0.3)
            print "DONE rate, delay "+str(0)+", "+str(delay)+ " Run number "+str(run_num)+" file_size " + file_size
            for proxy in [0, 1]:
                download(proxy, file_size, run_num, '0', str(delay))
    return


if __name__=="__main__":

    #R = Router('192.168.10.1', 'root', 'passw0rd', 'R')
    Q = Router('10.0.1.1', 'root', 'passw0rd', 'Q')

    #quick_test(Q)
    test_all_combos(Q)
    #download(1, '2M', 0)
    #download(0, '2M', 0)
    Q.host.close()
