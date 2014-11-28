import subprocess
from random import shuffle
from classes import Router
import time


def download(proxy=1, file_zize='10M', run_num=0, rate='', delay=''):
    outfile = "curl-proxy_"+str(proxy)+"-file_"+file_zize+"-rate_"+rate+"-delay_"+delay+"-run_"+str(run_num)+".log"
    cmd = "curl 10.0.0.1:8055/test" + file_zize + ".gz -o /dev/null --stderr /home/gtnoise/test/"+outfile
    if proxy == 1:
        cmd += " -x http://10.0.2.1:3128"
    if proxy == 2:
        cmd += " -x http://10.0.0.1:3128"
    # BLOCKING CMD
    o = subprocess.check_output(cmd, shell=True)
    return 0

def download_DEBUG(proxy=1, file_zize='10M', run_num=0, rate='', delay=''):
    outfile = "curl-proxy_"+str(proxy)+"-file_"+file_zize+"-rate_"+rate+"-delay_"+delay+"-run_"+str(run_num)+".log"
    cmd = "curl 10.0.0.1:8055/test" + file_zize + ".gz -o /dev/null"
    if proxy == 1:
        cmd += " -x http://10.0.2.1:3128"
    if proxy == 2:
        cmd += " -x http://10.0.0.1:3128"
    # BLOCKING CMD
    print cmd
    print "DELAY ", delay, " Run Number ", str(run_num), " PROXY ", str(proxy)
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

def test_all_combos(Q, M, S, file_size='500K'):
    proxies = range(3)
    for delay in [0, 5, 10, 15, 20, 25, 30, 35, 40, 60, 80, 100]:
        for rate in [0, 5, 10, 15, 20, 25, 30, 35, 40, 60, 80, 100]:
            M.remoteCommand('sudo sh clearcache.sh')
            S.remoteCommand('sudo sh clearcache.sh')
            set_rate_delay(Q, rate, delay)
            time.sleep(1)
            for run_num in range(50):
                time.sleep(0.1)
                shuffle(proxies)
                for proxy in proxies:
                    download(proxy, file_size, run_num, str(rate), str(delay))
                    clear_polipo_cache(M, S)
            print time.time(), ": DONE rate "+str(rate)+" delay "+str(delay)+ " file_size " + file_size
    return

def clear_polipo_cache(M, S):
    M.remoteCommand('sudo sh clearcache.sh')
    S.remoteCommand('sudo sh clearcache.sh')
    return

def quick_test(Q, M, S):
    file_size = '500K'
    rate = 5
    proxies = range(3)
    for delay in [1, 10, 20, 30, 100]:
        for run_num in range(5):
            clear_polipo_cache(M, S)
            set_rate_delay(Q, rate, delay)
            time.sleep(0.1)
            shuffle(proxies)
            for proxy in proxies:
                download_DEBUG(proxy, file_size, run_num, str(rate), str(delay))
                clear_polipo_cache(M, S)
    return


if __name__=="__main__":

    #R = Router('192.168.10.1', 'root', 'passw0rd', 'R')
    Q = Router('10.0.1.1', 'root', 'passw0rd', 'Q')
    M = Router('10.0.2.1', 'sarthak', 'sarthak123', 'M')
    S = Router('10.0.0.1', 'gtnoise', 'gtnoise', 'S')

    start_t = time.time()
    print "START ", start_t

    #quick_test(Q, M, S)
    test_all_combos(Q, M, S, '2M')

    set_rate_delay(Q, 0, 0)
    done_t = time.time()
    print "DONE ", (done_t - start_t)

    start_t = time.time()
    print "START ", start_t
    test_all_combos(Q, M, S, '10M')
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
    S.host.close()
