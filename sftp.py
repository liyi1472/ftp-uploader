#coding:utf-8
import paramiko
import yaml
import os
import getopt
import sys

# 加载设置文件
def config(yamlPath):
    # 加载配置文件
    if yamlPath is None:
        configPath = os.path.abspath('.')
        yamlPath = os.path.join(configPath, 'config.yml')
    with open(yamlPath) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

# 判断远程目录是否存在
def exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except FileNotFoundError:
        return False

# 递归文件目录扩展文件列表
def recursive(sftp, f):
    # 全部文件路径
    files = []
    # 去掉路径字符串最后的字符'/'
    if f['LOCAL'][-1] == '/':
        f['LOCAL'] = f['LOCAL'][0:-1]
    if f['REMOTE'][-1] == '/':
        f['REMOTE'] = f['REMOTE'][0:-1]
    # 获取当前指定目录下的所有目录及文件
    if os.path.isdir(f['LOCAL']):
        if not exists(sftp, f['REMOTE']):
            sftp.mkdir(f['REMOTE'])
        for i in os.listdir(f['LOCAL']):
            files.extend(recursive(sftp, {'LOCAL':f['LOCAL'] + '/' + str(i), 'REMOTE':f['REMOTE'] + '/' + str(i)}))
    else:
        # 追加文件
        files.append(f)
    return files

# 预处理文件列表
def preprocess(sftp, files):
    tmp = []
    for f in files:
        if os.path.isdir(f['LOCAL']):
            tmp.extend(recursive(sftp, f))
        else:
            tmp.append(f)
    return tmp

# 上传文件列表
def upload(host, port, username, pkey, files):
    # 开启连接
    pkey = paramiko.RSAKey.from_private_key_file(pkey)
    t = paramiko.Transport(host, port)
    t.connect(username=username, pkey=pkey)
    sftp = paramiko.SFTPClient.from_transport(t)
    files = preprocess(sftp, files)
    # 正式上传
    print("\n")
    for f in files:
        # 去除 .DS_Store
        if f['LOCAL'].endswith('/.DS_Store'):
            continue
        print(f['LOCAL'])
        sftp.put(f['LOCAL'], f['REMOTE'])
        # print('   [OK] "' + f['LOCAL'] + '"')
    print("\n")
    # 关闭连接
    t.close()

# 程序入口
if __name__ == '__main__':
    # 自定义配置文件
    # sys.argv[0] 为脚本名, sys.argv[1] (含) 以后为要处理的参数列表
    yamlPath = None
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, 'c:', longopts=['config='])
    for opt, arg in opts:
        if opt in ('-c', '--config'):
            yamlPath = arg
    config = config(yamlPath)
    # 启动程序
    upload(config['HOST'], config['PORT'], config['USER'], config['PKEY'], config['FILES'])
