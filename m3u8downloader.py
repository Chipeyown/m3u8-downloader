import os
import threading
from queue import Queue
from Crypto.Cipher import AES
import requests


def downm3u8(m3u8_url, name, directory, t_num):
    def get_content(url):
        while True:
            try:
                content = requests.get(url).content
                return content
            except:
                continue

    def download(pre, n, key, out_folder):
        while True:
            ts = task.get()
            lock.acquire()
            count[0] += 1
            print('[' + '#' * int((count[0] + 1) / (n / float(100))) + ' ' * (
                    100 - int((count[0] + 1) / (n / float(100)))) + ']' + '--[' + str(count[0]) + '/' + str(
                n) + ']', end='\r', flush=True)
            lock.release()
            ts_url = pre + ts
            number = count[0] - 1
            content = get_content(ts_url)
            if len(key) != 0:
                cryptor = AES.new(key, AES.MODE_CBC, key)
                content = cryptor.decrypt(content)
            with open('%s/%s.mp4' % (out_folder, number), 'ab') as f:
                f.write(content)
            task.task_done()

    try:
        os.mkdir('%s/%s' % (directory, name))
    except:
        pass
    pre = m3u8_url.rstrip(m3u8_url.split('/')[-1])
    lines = requests.get(m3u8_url).text.strip().split('\n')
    ts_list = [line.split('/')[-1] for line in lines if line.startswith('#') == False]
    key = b''
    for line in lines:
        if 'AES-128' in line:
            key_url = pre + line.split('"')[1].split('/')[-1]
    key = requests.get(key_url).content
    n = len(ts_list)
    count = [0]
    dict = {}
    lock = threading.Lock()
    task = Queue()
    for i in range(int(t_num)):
        t = threading.Thread(target=download, args=(pre, n, key, '%s/%s' % (directory, name)))
        t.daemon = True
        t.start()
    for ts in ts_list:
        task.put(ts)
    task.join()

    print('\n' + '%s has downloaded successfully' % name)
    print('***Merging film***')
    fo = open('%s/%s/%s.mp4' % (directory, name, name), 'ab')
    for i in range(n):
        fl = open('%s/%s/%s.mp4' % (directory, name, i), 'rb')
        fo.write(fl.read())
        fl.close()
        os.remove('%s/%s/%s.mp4' % (directory, name, i))
    fo.close()
    print('Film is in %s' % directory)


if __name__ == '__main__':
    input1 = input('m3u8 link:')
    input2 = input('film name:')
    thread_number = input('threading number:')
    directory = os.getcwd().replace('\\', '/')
    downm3u8(input1, input2, directory, thread_number)
