import requests
import re
import threading
import os
from Crypto.Cipher import AES

def get_ts_address(url_m3u8):
    pa0=r'\w+.m3u8'
    res0=re.findall(pa0,url_m3u8)[0]
    url_m3u8_new=url_m3u8.rstrip(res0)
    response=requests.get(url_m3u8)
    res=response.text
    pa=r'\w+\.ts'
    address=re.findall(pa,res)
    return address,url_m3u8_new
def download(url_ts):
    while True:
        try:
            response=requests.get(url_ts)
            ts_content=response.content
        except:
            continue
        else:
            break
    return ts_content
def download_group(url_m3u8_new,addressi,directory,i,input2,key):
    num=len(addressi)
    j=1
    fl=open('%s/%s/%s-%s.mp4'%(directory,input2,input2,i),'ab')
    cryptor = AES.new(key, AES.MODE_CBC, key)
    for item in addressi:
        url_ts=url_m3u8_new+item#每个片段的完整下载地址
        ts_content=download(url_ts)
        fl.write(cryptor.decrypt(ts_content))
        print('%s-%s-已下载%s/%s'%(input2,i,j,num))
        j+=1
    fl.close()
def main():
    print('###############################################################')
    print('')
    print('    m3u8格式下载器')
    print('')
    print('    下载速度想要多快自己调')
    print('')
    print('    Made by Chipeyown')
    print('')
    print('###############################################################')
    input1=input('请输出电影对应的m3u8网址：')
    input2=input('请输入电影的名字：')
    input3=input('请输入电影的加密key的链接：')
    key = requests.get(input3).content
    directory=os.getcwd().replace('\\','/')
    os.mkdir('%s/%s'%(directory,input2))#建立对应的文件夹
    address_raw=get_ts_address(input1)[0]#获取m3u8源对应的片段下载地址的后缀
    length=len(address_raw)
    print('视频共分为%d段'%length)#得知该视频被分为了多少段
    url_m3u8_new=get_ts_address(input1)[1]#获取m3u8源对应的片段下载地址的前缀
    thread_number=input('请问要开几个线程(一般为10个，越多下载越快)：')
    size=int(length/(int(thread_number)-1))
    address=[address_raw[i:i+size] for i in range(0,len(address_raw),size)]#分组下载
    thread_list=[]
    for i in range(0,len(address)):
        t=threading.Thread(target=download_group,args=(url_m3u8_new,address[i],directory,i,input2,key))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()
    print('%s下载完成'%input2)
    print('***将分段进行合并***')
    fo=open('%s/%s/%s.mp4'%(directory,input2,input2),'ab')
    for i in range(0,len(address)):
        fl=open('%s/%s/%s-%s.mp4'%(directory,input2,input2,i),'rb')
        fo.write(fl.read())
        fl.close()
        os.remove('%s/%s/%s-%s.mp4'%(directory,input2,input2,i))
    fo.close()
    print('%s-合并完成'%input2)
    print('文件保存在:%s'%directory)
if __name__=='__main__':
    main()
