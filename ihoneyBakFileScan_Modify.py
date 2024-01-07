# -*- coding: UTF-8 -*-

import requests
import logging
from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime
from hurry.filesize import size
from fake_headers import Headers
from concurrent.futures import ThreadPoolExecutor

requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.WARNING, format="%(message)s")


# 假设以下变量已在函数外部正确定义并初始化
# header, proxies, timeout, outputfile

def vlun(urltarget):
    try:
        # 预先配置好请求参数
        params = {
            'url': urltarget, # 目标url
            'headers': header.generate(), # 伪造请求头
            'timeout': timeout, # 超时时间
            'allow_redirects': False,
            'stream': True,
            'verify': False,
        }

        if proxies:
            params['proxies'] = proxies

        # 发送请求
        r = requests.get(**params)

        # 使用集合来优化多次 in 检查
        content_types_to_check = {'html', 'image', 'xml', 'text', 'json', 'javascript'}
        if r.status_code == 200 and r.headers.get('Content-Type') not in content_types_to_check:
            tmp_rarsize = int(r.headers.get('Content-Length')) # 获取文件大小
            rarsize = str(size(tmp_rarsize)) # 转换为可读格式
            if int(rarsize[:-1]) > 0:
                # 带颜色输出
                logging.warning(f'\033[32m[ success ] {urltarget}  size:{rarsize}\033[0m')
                with open(outputfile, 'a') as f:
                    f.write(f"{urltarget}\n")
                    # f.write(f"{urltarget}  size:{rarsize}\n")
            else:
                # 带颜色输出
                logging.warning(f'\033[31m[ 失败 ] {urltarget}\033[0m')
        else:
            logging.warning(f'\033[31m[ 失败 ] {urltarget}\033[0m')
    except Exception as e:
        logging.warning(f'\033[31m[ 失败 ] {urltarget}\033[0m')


def urlcheck(target=None, ulist=None):
    if target is not None and ulist is not None:
        if target.startswith('http://') or target.startswith('https://'):
            if target.endswith('/'):
                ulist.append(target)
            else:
                ulist.append(target + '/')
        else:
            line = 'http://' + target
            if line.endswith('/'):
                ulist.append(line)
            else:
                ulist.append(line + '/')
        return ulist


def dispatcher(url_file=None, url=None, max_thread=20, dic=None):
    urllist = []
    if url_file is not None and url is None:
        with open(str(url_file)) as f:
            while True:
                line = str(f.readline()).strip()
                if line:
                    urllist = urlcheck(line, urllist)
                else:
                    break
    elif url is not None and url_file is None:
        url = str(url.strip())
        urllist = urlcheck(url, urllist)
    else:
        pass

    with open(outputfile, 'a'):
        pass

    for u in urllist:
        check_urllist = []
        cport = None
        # ucp = u.strip('https://').strip('http://')
        if u.startswith('http://'):
            ucp = u.lstrip('http://')
        elif u.startswith('https://'):
            ucp = u.lstrip('https://')
        if '/' in ucp:
            ucp = ucp.split('/')[0]
        if ':' in ucp:
            cport = ucp.split(':')[1]
            ucp = ucp.split(':')[0]
            www1 = ucp.split('.')
        else:
            www1 = ucp.split('.')
        wwwlen = len(www1)
        wwwhost = ''
        for i in range(1, wwwlen):
            wwwhost += www1[i]

        current_info_dic = deepcopy(dic)  # deep copy
        suffixFormat = ['.zip', '.rar', '.tar.gz', '.tgz', '.tar.bz2', '.tar', '.jar', '.war', '.7z', '.bak', '.sql',
                        '.gz', '.sql.gz', '.tar.tgz', '.backup']
        domainDic = [ucp, ucp.replace('.', ''), ucp.replace('.', '_'), wwwhost, ucp.split('.', 1)[-1],
                     (ucp.split('.', 1)[1]).replace('.', '_'), www1[0], www1[1]]
        domainDic = list(set(domainDic))
        for s in suffixFormat:
            for d in domainDic:
                current_info_dic.extend([d + s])
        current_info_dic = list(set(current_info_dic))
        for info in current_info_dic:
            url = str(u) + str(info)
            check_urllist.append(url)
            print("[添加进程] " + url)

        l = []
        p = ThreadPoolExecutor(max_thread)
        for url in check_urllist:
            obj = p.submit(vlun, url)
            l.append(obj)
        p.shutdown()


if __name__ == '__main__':
    usageexample = '\n       Example: python3 ihoneyBakFileScan_Modify.py -t 100 -f url.txt -o result.txt\n'
    usageexample += '                '
    usageexample += 'python3 ihoneyBakFileScan_Modify.py -u https://www.example.com/ -o result.txt'

    parser = ArgumentParser(add_help=True, usage=usageexample, description='A Website Backup File Leak Scan Tool.')
    parser.add_argument('-f', '--url-file', dest="url_file", help="Example: url.txt")
    parser.add_argument('-t', '--thread', dest="max_threads", nargs='?', type=int, default=1, help="Max threads")
    parser.add_argument('-u', '--url', dest='url', nargs='?', type=str, help="Example: http://www.example.com/")
    parser.add_argument('-d', '--dict-file', dest='dict_file', nargs='?', help="Example: dict.txt")
    parser.add_argument('-o', '--output-file', dest="output_file", help="Example: result.txt")
    parser.add_argument('-p', '--proxy', dest="proxy", help="Example: socks5://127.0.0.1:1080")

    args = parser.parse_args()
    # 使用程序默认字典，精确扫描模式，根据域名自动生成字典。
    tmp_suffixFormat = ['.zip', '.rar', '.tar.gz', '.tgz', '.tar.bz2', '.tar', '.jar', '.war', '.7z', '.bak', '.sql',
                        '.gz', '.sql.gz', '.tar.tgz']
    # 77
    tmp_info_dic = ['六合', '备份', '源码', '站点', '网站', '程序', '模板', '整站', '商城', '数据', '数据库', '服务器',
                    '网站备份', '安装文件', '数据备份', '数据库备份', '数据库文件', '新建文件夹', '新建文件夹 (1)',
                    '新建文件夹 (2)', '新建文件夹 (3)', '新建文本文档', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                    'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3',
                    '4', '5', '6', '7', '8', '9', '10', '520', '111', '123', '1234', '12345', '123456', '1980', '1981',
                    '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992', '1993',
                    '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005',
                    '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
                    '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029',
                    '2030', '1314', '111111', '123123', 'sj', 'sjk', 'wz', 'bf', 'gg', 'pic', 'rar', 'zip', 'file',
                    'files', 'new', 'temp', 'image', 'images', 'shu', 'shuju', 'shujuku', 'vip', 'scm', 'php', 'test',
                    'user', 'logo', 'root', 'good', 'users', 'admin', 'html', 'upfile', 'beian', 'beifen', 'fourm',
                    'install', 'wm123', 'upload', 'ue', 'userlist', 'we', 'Release', 'material', 'template', 'pass',
                    'password', 'error', 'err', 'oa', 'ftp', 'ftp1', 'mdb', 'mail', 'email', 'shop', 'hdocs', 'htdocs',
                    'z9v8ftp', 'z9v8flashFXP', 'flashfxp', 'dz', 'dede', 'dedecms', 'phpcms', 'bb', 'bbs', 'site',
                    'http', 'web', 'web1', 'ww', 'www', 'website', 'webroot', 'wwroot', 'wwwroot', 'wahan', 'sql',
                    'sqa', 'db', 'dev', 'bak', 'back', 'backup', 'dat', 'data', 'datad', 'databack', 'backua',
                    'databackup', 'database', 'databas', '0', '00', '000', '012', '127.0.0.1', '234', '333', '444',
                    '555', '666', '777', '888', '999', 'about', 'app', 'application', 'archive', 'asp', 'aspx', 'auth',
                    'backups', 'bin', 'cache', 'clients', 'code', 'com', 'config', 'core', 'customers', 'download',
                    'dump', 'engine', 'error_log', 'extend', 'forum', 'home', 'img', 'include', 'index', 'joomla', 'js',
                    'jsp', 'local', 'login', 'localhost', 'master', 'media', 'members', 'my', 'mysql', 'old', 'orders',
                    'output', 'package', 'public', 'runtime', 'sales', 'server', 'store', 'tar', 'vb', 'vendor',
                    'wangzhan', 'wordpress', 'wp', 'log']
    # 130
    info_dic = []
    for a in tmp_info_dic:
        for b in tmp_suffixFormat:
            info_dic.extend([a + b])

    global outputfile
    if (args.output_file):
        outputfile = args.output_file
    else:
        outputfile = 'result.txt'
    # add proxy
    global proxies
    if (args.proxy):
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
    else:
        proxies = ''
    header = Headers(
        # 生成任何浏览器和操作系统头文件
        headers=False  # 不生成其他标头
    )

    timeout = 10  #

    try:
        if args.dict_file and outputfile:
            # 自定义扫描字典
            # 不建议将此模式用于批量扫描。它容易出现误报，并可能降低程序效率。
            custom_dict = list(set([i.replace("\n", "") for i in open(str(args.dict_file), "r").readlines()]))
            info_dic.extend(custom_dict)
        if args.url:
            dispatcher(url=args.url, max_thread=args.max_threads, dic=info_dic)
        elif args.url_file:
            dispatcher(url_file=args.url_file, max_thread=args.max_threads, dic=info_dic)
        else:
            print("[!] Please specify a URL or URL file name")
    except Exception as e:
        print(e)
