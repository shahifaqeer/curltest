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

def download_DEBUG(proxy=1, file_zize='10M', run_num=0, rate='', delay=''):
    outfile = "curl-proxy_"+str(proxy)+"-file_"+file_zize+"-rate_"+rate+"-delay_"+delay+"-run_"+str(run_num)+".log"
    cmd = "curl 10.0.0.1:8055/test" + file_zize + ".gz -o /dev/null"
    if proxy == 1:
        cmd += " -x http://10.0.2.1:3128"
    # BLOCKING CMD
    o = subprocess.check_output(cmd, shell=True)
    print o
    return

def set_rate_delay(Q, rate, delay):
    rate_bits = str(rate)
    delay_ms = str(delay)
    Q.remoteCommand('tc qdisc del dev br-lan root')
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

def test_all_combos(Q, M):
    for rate in [0, 5, 10, 15, 20, 25]:
        for file_size in ['500K', '2M', '10M']:
            M.remoteCommand('sudo sh clearcache.sh')
            for run_num in range(20):
                for delay in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                    set_rate_delay(Q, rate, delay)
                    time.sleep(0.1)
                    print "DONE delay "+str(delay)+ " Run number "+str(run_num)+" file_size " + file_size
                    for proxy in [0, 1]:
                        download(proxy, file_size, run_num, str(rate), str(delay))
                        if proxy == 1:
                            M.remoteCommand('sudo sh clearcache.sh')
            time.sleep(1)
    return

def clear_polipo_cache(M):
    M.remoteCommand('sudo sh clearcache.sh')
    return

def quick_test(Q, M):
    file_size = '500K'
    for run_num in range(5):
        for delay in [1, 10, 30, 100]:
            set_rate_delay(Q, 1, delay)
            time.sleep(0.1)
            print "DONE rate, delay "+str(1)+", "+str(delay)+ " Run number "+str(run_num)+" file_size " + file_size
            for proxy in [0, 1]:
                download_DEBUG(proxy, file_size, run_num, '0', str(delay))
                if proxy == 0:
                    print "clear cache"
                    M.remoteCommand('sudo kill -USR1 $(pgrep polipo)')
                    M.remoteCommand('sleep 0.1')
                    M.remoteCommand('sudo polipo -x')
                    M.remoteCommand('sudo kill -USR2 $(pgrep polipo)')
                    #clear_polipo_cache(M)
    return


if __name__=="__main__":

    #R = Router('192.168.10.1', 'root', 'passw0rd', 'R')
    Q = Router('10.0.1.1', 'root', 'passw0rd', 'Q')
    M = Router('10.0.2.1', 'sarthak', 'sarthak123', 'Q')

    #quick_test(Q)
    start_t = time.time()

    test_all_combos(Q, M)

    set_rate_delay(Q, 0, 0)
    done_t = time.time()
    print "DONE ", (done_t - start_t)
    #quick_test(Q, M)
    '''
    set_rate_delay(Q, 1, 100)

    M.remoteCommand('sudo sh clearcache.sh')
    download_DEBUG(0, '500K', 0, '1', '100')
    download_DEBUG(1, '500K', 0, '1', '100')
    M.remoteCommand('sudo sh clearcache.sh')
    download_DEBUG(0, '500K', 1, '1', '100')
    download_DEBUG(1, '500K', 1, '1', '100')
    M.remoteCommand('sudo sh clearcache.sh')
    download_DEBUG(0, '500K', 2, '1', '100')
    download_DEBUG(1, '500K', 2, '1', '100')
    M.remoteCommand('sudo sh clearcache.sh')
    '''
    Q.host.close()
    M.host.close()
