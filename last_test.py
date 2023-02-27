# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 00:42:57 2023

@author: bianca
"""

#%%小说网整合
# '''方式：获取即将爬取小说网的所有书籍链接：书名，同时按照
# 无忧书城：书名-书籍链接-类别（可全部获得）https://www.51shucheng.net/fenlei
# 映月网站：书名-书籍类别-类别（可全部获得）

# '''
import streamlit as st
import requests
import re
from lxml import etree
import random
import time
import pandas as pd
import datetime

import numpy as np
import os

st.set_page_config(page_title='明月傍窗好读书')
st.title('欢迎来到免费小说下载平台')



user_agent=['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41',
'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36',
 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36',
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
]
#%%获取时间（仅用做记录登陆时间）
SHA_TZ = datetime.timezone(datetime.timedelta(hours=8),name='Asia/Shanghai')
utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)#协调世界时
beijing_now = utc_now.astimezone(SHA_TZ)
time_login=beijing_now.strftime('%Y-%m-%d %H:%M:%S')
st.write(time_login)
#%%函数板块
def get_51_class(url,user_agent):
    header={'user-agent':random.choice(user_agent)}
    resp=requests.get(url,headers=header)
    resp.encoding='utf-8'
    title=re.findall('<a href=".*?" title="(.*?)">.*?</a><span>',resp.text,re.S)
    href=re.findall('<li><a href="(.*?)" title=".*?">.*?</a><span>',resp.text,re.S)
    print(title,href)
    return title,href
def get_51_class_book(href,user_agent):
    header={'user-agent':random.choice(user_agent)}
    resp1=requests.get(href,headers=header)
    resp1.encoding='utf-8'
    href_list1=re.findall('<li class=".*"><a href="(.*)">.*</a>\n</li>',resp1.text)
    title_list1=re.findall('<li class=".*"><a href=".*">(.*)</a>\n</li>',resp1.text)
    print(title_list1,href_list1)
    return title_list1,href_list1
@st.cache_data
def get_51_all_book(user_agent):
    
    title_class=[]
    title_class_book=[]
    href_class_book=[]
    data51=pd.DataFrame()
    #%% 51书城
    url='https://www.51shucheng.net/fenlei'
    title,href=get_51_class(url,user_agent)
    time.sleep(30)
    for i in range(len(href)):
        st.sidebar.write(i)
        title_list1,href_list1=get_51_class_book(href[i],user_agent)
        time.sleep(5)
        title_class=title_class+[title[i]]*len(title_list1)
        title_class_book=title_class_book+title_list1
        href_class_book=href_class_book+href_list1
        time.sleep(5)
        
    data51['书名']=title_class_book
    data51['网址']=href_class_book
    data51['类别']=title_class
    data51.to_excel('./51书城所有书目.xlsx',index=False)
#%% 拿笔趣阁的小说来
#获得笔趣所有分类
def get_biqu_allclass(url,user_agent):
    header={'user-agent':random.choice(user_agent)}
    resp=requests.get(url,headers=header)
    resp.encoding='gbk'
    e=etree.HTML(resp.text)
    
    fenlei=e.xpath('/html/body/div[2]/div[1]/ul/li/a/@href')
    leibie=e.xpath('/html/body/div[2]/div[1]/ul/li/a/text()')[1:]
    fenlei_url=[]
    for i in range(len(fenlei)):
        fenlei_url.append(fenlei[0]+fenlei[i+1])
        if i==len(fenlei)-2:
            break
    return fenlei_url,leibie
#%%获取该分类总页数
def get_biqu_fenlei_page(url,user_agent):
    header={'user-agent':random.choice(user_agent)}
    resp=requests.get(url,headers=header)
    resp.encoding='gbk'
    all_page=int(re.findall('<a href=".*" class="last">(.*)</a></div>',resp.text)[0])
    return all_page
#%%获取该分类单页所有小说
def get_biqu_onepage_book(url,user_agent):
    header={'user-agent':random.choice(user_agent)}
    resp=requests.get(url,headers=header)
    resp.encoding='gbk'
    e=etree.HTML(resp.text)
    book_list=e.xpath('/html/body/div[3]/div[1]/div[2]/div/div[2]/ul/li/div[1]/a/@href')
    name_list=e.xpath('/html/body/div[3]/div[1]/div[2]/div/div[2]/ul/li/div[1]/a/@title')
    author_list=e.xpath('/html/body/div[3]/div[1]/div[2]/div/div[2]/ul/li/div[3]/text()')
    return book_list,name_list,author_list
# #%%初始化笔趣阁的数据
# def chushihua():
#     book=[]
#     name=[]
#     author=[]
#     leibie=[]
#     return book,name,author,leibie
#%%导入列表中
def daoru(list1,list2):
    for  b in list1:
        list2.append(b)
#%% 获取单页的源代码
def get_book_danye(user_agent,url):
    proxy='117.93.108.82:49215'

    proxies={'http':'http://'+proxy}
    header={'user-agent':random.choice(user_agent)}
    resp=requests.get(url,headers=header,proxies=proxies)
    resp.encoding='gbk'
    #超过一页的小说
    e=etree.HTML(resp.text)
    return e
#%% 获取一本书的正文加标题
def get_book(user_agent,proxies,url,name,author):
    count=0
    time_waste=time.time()
    url_title='https://www.bbiquge.net'
    st.sidebar.write('正在下载')
    # st.write(url)
    # st.write(name)
    #获取小说的所有页数
    e=get_book_danye(user_agent,proxies,url)
    #获取残缺的网址
    all_page=e.xpath('/html/body/div[4]/div/select/option/@value')
    if all_page==[]:
        url_2=e.xpath('/html/body/div[4]/dl/dd/a/@href')
        for k in (range(len(url_2))):
            url_3=url+url_2[k]
            e=get_book_danye(user_agent,proxies,url_3)
            info='\n'.join(e.xpath('/html/body/div[3]/div[2]/div[1]/text()')[2:])
            title=e.xpath('/html/body/div[3]/h1/text()')[0]
            st.sidebar.write(f'{title}--------ok')
            time.sleep(0.5)
            with open(f'{name}--{author}.txt','a',encoding="utf-8")as f:
                f.write(title+'\n\n'+info+'\n\n')
            count+=1
        time_need=time.time()-time_waste
    else:
        for i in all_page:
            #获得每页完整网址
            url_1=url_title+i
            #每页单独进行
    
            #获取每页源代码
            e=get_book_danye(user_agent,proxies,url_1)
            #获取每页章节
            url_2=e.xpath('/html/body/div[4]/dl/dd/a/@href')
            #获取所有章节链接 和章节名
            for k in (range(len(url_2))):
                url_3=url+url_2[k]
                e=get_book_danye(user_agent,proxies,url_3)
                info='\n'.join(e.xpath('/html/body/div[3]/div[2]/div[1]/text()')[2:])
                title=e.xpath('/html/body/div[3]/h1/text()')[0]
                st.sidebar.write(f'{title}--------ok')
                time.sleep(0.5)
                with open(f'{name}--{author}.txt','a',encoding="utf-8")as f:
                    f.write(title+'\n\n'+info+'\n\n')
                count+=1
        time_need=time.time()-time_waste
    st.write('全部下载完毕')
    return time_need,count
#%%重新爬
def get_book_again(user_agent,proxies,url,name,author):
    count=0
    time_waste=time.time()
    url_title='https://www.bbiquge.net'
    st.sidebar.write('正在下载')
    # st.write(url)
    # st.write(name)
    #获取小说的所有页数
    e=get_book_danye(user_agent,proxies,url)
    #获取残缺的网址
    all_page=e.xpath('/html/body/div[4]/div/select/option/@value')
    if all_page==[]:
        url_2=e.xpath('/html/body/div[4]/dl/dd/a/@href')
        for k in (range(len(url_2))):
            url_3=url+url_2[k]
            e=get_book_danye(user_agent,proxies,url_3)
            info='\n'.join(e.xpath('/html/body/div[3]/div[2]/div[1]/text()')[2:])
            title=e.xpath('/html/body/div[3]/h1/text()')[0]
            st.sidebar.write(f'{title}--------ok')
            time.sleep(0.5)
            with open(f'{name}--{author}-副本.txt','a',encoding="utf-8")as f:
                f.write(title+'\n\n'+info+'\n\n')
            count+=1
        time_need=time.time()-time_waste
    else:
        for i in all_page:
            #获得每页完整网址
            url_1=url_title+i
            #每页单独进行
    
            #获取每页源代码
            e=get_book_danye(user_agent,proxies,url_1)
            #获取每页章节
            url_2=e.xpath('/html/body/div[4]/dl/dd/a/@href')
            #获取所有章节链接 和章节名
            for k in (range(len(url_2))):
                url_3=url+url_2[k]
                e=get_book_danye(user_agent,proxies,url_3)
                info='\n'.join(e.xpath('/html/body/div[3]/div[2]/div[1]/text()')[2:])
                title=e.xpath('/html/body/div[3]/h1/text()')[0]
                st.sidebar.write(f'{title}--------ok')
                time.sleep(0.5)
                with open(f'{name}--{author}-副本.txt','a',encoding="utf-8")as f:
                    f.write(title+'\n\n'+info+'\n\n')
                count+=1
        time_need=time.time()-time_waste
    st.write('全部下载完毕')
    return time_need,count
#%%爬取笔趣阁所有小说信息
@st.cache_data
def get_biqu_all_book(user_agent):
    
    url='https://www.bbiquge.net/'
    
    #获取分类
    fenlei_url,leibie1=get_biqu_allclass(url,user_agent)
    book=[]
    name=[]
    author=[]
    leibie=[]
    
    #获取分类下总页数
    
    for i in range(len(fenlei_url)):
        
        all_page=get_biqu_fenlei_page(fenlei_url[i],user_agent)
        time.sleep(10)
        
        for j in (range(all_page)):
            if i<=5:
                url=(fenlei_url[i].split('_')[0]+"_"+f"{j+1}"+'/')
            elif i==6:
                url=(fenlei_url[i]+f'{j+1}')
            elif i==7:
                url=(fenlei_url[i]+f'{j+1}'+'.html')
                break
            
            time.sleep(0.7)
            book_list,name_list,author_list=get_biqu_onepage_book(url,user_agent)
            daoru(book_list,book)
            daoru(name_list,name)
            daoru(author_list,author)
            
            daoru([leibie1[i]]*len(book_list),leibie)
    #%% 保存爬取到的数据
    data222=pd.DataFrame()
    n1=len(book)
    n=0
    data222['书名']=name[n:n1]
    data222['网址']=book[n:n1]
    data222['类别']=leibie[n:n1]
    data222['作者']=author[n:n1]
    data222.to_csv('./笔趣阁所有书目all.csv',index=False)
#%%查看数据
def show_data():
    data=pd.read_table('./用户数据.txt',header=None,sep=',')
    st.table(data)
def show_book(book_list):
    book_list1=[]
    for i in book_list:
        if '用户数据'  not in i:
            if 'requirements' not in i:
                book_list1.append(i)
    st.sidebar.table(book_list1)
#%%删除数据
def delete_data(file,book_list):
    for i in book_list:
        if '用户数据' in i:
            txt=os.path.join(file,f'{i}')
            os.remove(txt)
#%%加载数据
def user_data_load(column):
    for c in range(len(column)):
        if c!=len(column)-1:
            with open('./用户数据.txt','a',encoding='utf-8') as U:
                U.write(column[c])
                U.write(',')
        else:
            with open('./用户数据.txt','a',encoding='utf-8') as U:
                U.write(column[c])
                U.write('\n')
def tool_box():
    #一键更新51书城所有书目
    choose=st.sidebar.selectbox('功能选择', ['查看用户数据','更新51书目','更新笔趣书目','一键删除用户数据','一键插入标题行','查看已下载小说'])
    if choose=='查看用户数据':
        show_data()
    elif choose=='一键删除用户数据':
        delete_data(file,book_list)
    elif choose=='一键插入标题行'  :
        user_data_load(column)
    elif choose=='更新笔趣书目':
        get_biqu_all_book(user_agent)
    elif choose=='更新51书目':
        get_51_all_book(user_agent)
    elif choose=='查看已下载小说':
        show_book(book_list)
#%% 字典去重
func=lambda data:dict([x,y] for y,x in data.items())
#%%导入数据库
#@st.cache_data
def get_all_book():
    data=pd.read_csv('./笔趣阁所有书目1.csv')
    return data
#%%导入笔趣阁
#%%检索内存是否有该小说
file=os.getcwd()
file_local=os.listdir(file)
book_list=[]
for b in file_local:
    if '.txt' in b:
        book_list.append(b)
#%%
# data=get_all_book()
# name_list=list(data['书名'])
# url_list=list(data['网址'])
# author_list=list(data['作者'])
# class_list=list(data['类别'])
st.subheader('请搜小说名或者作家名')
# col1,col2=st.columns(2)
# with col1:
#     name=st.text_input('您想查看什么小说(不要空值搜索)：','请输入')
#     candiate_name={0:'请选择'}
#     candiate=[]

#     if name!=None:
#         for i in range(len(name_list)):
#             if name in name_list[i]:
#                 candiate_name[i]=f'《{name_list[i]}》------{author_list[i]}'
#         da=func((candiate_name))
#         need=st.radio('请选择',da)

#         st.sidebar.write(name_list[da[need]])
#         if f'{name_list[da[need]]}--{author_list[da[need]]}.txt' in book_list:
#             st.write('已有该小说啦')
#             f=open(f'{name_list[da[need]]}--{author_list[da[need]]}.txt','r',encoding='utf-8')
#             st.download_button('保存到本地',f)
        
#             if st.button('也可重新爬取---->'):
#                 with open(f'{name_list[da[need]]}--{author_list[da[need]]}-副本.txt','w') as f:
#                     f.close()
#                 i=int(da[need])
#                 time_need,count=get_book_again(user_agent,proxies,url_list[i],name_list[i],author_list[i])
#                 data=[f'{time_login}',f'{name_list[i]}',f'{author_list[i]}',f'{class_list[i]}',f'{count}',f'{time_need}']
#                 user_data_load(data)
#                 f=open(f'{name_list[da[need]]}--{author_list[da[need]]}-副本.txt','r',encoding='utf-8')
#                 st.download_button('保存到本地',f)
#         else:
#             i=int(da[need])
#             st.sidebar.write(url_list[i])
#             if st.sidebar.button('爬取---->'):
#                 time_need,count=get_book(user_agent,proxies,url_list[i],name_list[i],author_list[i])
#                 data=[f'{time_login}',f'{name_list[i]}',f'{author_list[i]}',f'{class_list[i]}',f'{count}',f'{time_need}']
#                 user_data_load(data)
#                 f=open(f'{name_list[da[need]]}--{author_list[da[need]]}.txt','r',encoding='utf-8')
#                 st.download_button('保存到本地',f)
# with col2:
#     author=st.text_input('您想看哪个作家的小说(不要空值搜索)','请输入')
#     if author!="请输入":
        
#         try:
#             index=data['作者']==author
#             da1=pd.DataFrame(data.loc[index,'书名'])
#             da1=da1.drop_duplicates('书名')
#             # choose='天王'
#             choose=st.radio('该作家书目如下', da1)
#             index1=int(da1[da1['书名']==choose].index.tolist()[0])
#             st.sidebar.write(name_list[index1],index1)
#             st.sidebar.write(url_list[index1])
#             if st.sidebar.button('爬取----->'):
#                 get_book(user_agent,proxies,url_list[i],name_list[i])
#         except:
#             st.write('抱歉丫————当前书城没有收录该作家任何书籍')

#%%设置管理系统

        

column=['搜索时间','书名','作者','类别','共多少章节','耗费时长']
code='曾文正'
code1=st.sidebar.text_input('输入密码，解锁管理功能')
if code!=code1:
    st.stop()
st.success(
    tool_box()
    
    )
    