import os
import re
import threading
from queue import Queue

import requests


def downm3u8(m3u8_url, name, directory, t_num):
    def get_content(url):
        while True:
            try:
                content = requests.get(url).content
                return content
            except:
                continue

    def download(n):
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
            dict[number] = get_content(ts_url)
            task.task_done()

    try:
        os.mkdir('%s/%s' % (directory, name))
    except:
        pass
    pre = m3u8_url.rstrip(m3u8_url.split('/')[-1])
    res = requests.get(m3u8_url).text
    ts_list = re.findall(r'\w+\.ts', res)
    n = len(ts_list)
    count = [0]
    dict = {}
    lock = threading.Lock()
    task = Queue()
    for i in range(int(t_num)):
        t = threading.Thread(target=download, args=(n,))
        t.daemon = True
        t.start()
    for ts in ts_list:
        task.put(ts)
    task.join()
    print('\n' + '%s has downloaded successfully' % name)
    print('***Merging film***')
    film = b''
    for i in range(n):
        film += dict[i]
    fo = open('%s/%s/%s.mp4' % (directory, name, name), 'ab')
    fo.write(film)
    fo.close()
    print('Film is in %s' % directory)


if __name__ == '__main__':
    input1 = input('m3u8 link:')
    input2 = input('film name:')
    thread_number = input('threading number:')
    directory = os.getcwd().replace('\\', '/')
    downm3u8(input1, input2, directory, thread_number)
