#coding=utf-8
import mimetypes,json
import requests
import re,os,threading,time,pymysql
class wordpress_post:
    def __init__(self,tittle,content):
        self.tittle=tittle
        self.content=content
    def mysql_con(self):
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pw', db='wordpress', charset='utf8') #修改这里
        return conn
    def up(self):
        times=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sql="INSERT INTO wp_posts(post_author,post_date,post_content,post_title,post_excerpt,post_status,comment_status,ping_status,post_name,to_ping,pinged,post_modified,post_content_filtered,post_parent,menu_order,post_type,comment_count) VALUES ('1','%s','%s','%s','','publish','open','open','%s','','','%s','','0','0','post','0')" % (str(times),str(self.content),str(self.tittle),str(self.tittle),str(times))
        return sql
    def cat(self,ids,cat):
        sql="INSERT INTO wp_term_relationships(object_id,term_taxonomy_id,term_order) VALUES (%s,%s,'0')"%(ids,cat)
        return sql
    def close_mysql(self,cursor,conn):
        conn.commit()
        cursor.close()
        conn.close()

def upload(files):
    APIKey = "key" #修改这里
    format = "json"
    url = "https://domain.com/api/1/upload/?key="+ APIKey + "&format=" + format #修改这里
    r = requests.post(url, files = files)
    time.sleep(1)
    return json.loads(r.text)
def formatSource(filename):
    imageList = []
    type = mimetypes.guess_type(filename)[0]
    imageList.append(('source' , (filename , open(filename , 'rb') , type)))
    return imageList
class myThread (threading.Thread):  
    def __init__(self, url, dir, filename):
        threading.Thread.__init__(self)
        self.threadID = filename
        self.url = url
        self.dir = dir
        self.filename=filename
    def run(self):                
        download_pic(self.url,self.dir,self.filename)
        
def download_pic(url,dir,filename):
    req=requests.get(url=url,headers=headers)
    if req.status_code==200:
        with open('temp/'+str(filename)+'.jpg','wb') as f:
            f.write(req.content)

flag=1
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://www.mm131.com/'}

while True:
    if flag==1:
        try:
            get=requests.get('http://www.mm131.com/xinggan/')
        except:
            continue
        b=re.findall(r'<dd><a target="_blank" href="http://www.mm131.com/xinggan/([0-9]*).html"><img src=',get.text)
        for a in b:
            try:
                getpage=requests.get('http://www.mm131.com/xinggan/'+str(a)+'.html')
            except:
                continue
            tittle=re.findall(r'<h5>(.*)</h5>',str(getpage.content,'gb2312',errors='ignore'))
            pages=[]
            threads=[]
            pages=re.findall(r'<span class="page-ch">共(.*?)页</span>',str(getpage.content,'gb2312',errors='ignore'))
            page=pages[0]
            download_url='http://img1.mm131.me/pic/'+str(a)+'/'
            for t in tittle:
                if os.path.exists(str(t)+'.txt')==False:
                    try:   
                        print('开始上传：'+t)
                        for page_img in range(int(page)):
                            download_img_url=download_url+str(page_img)+'.jpg'
                            thread=myThread(download_img_url,t,page_img)
                            thread.start()
                            threads.append(thread)
                        for ts in threads:
                            ts.join()
                        for i in range(int(page)):
                            file_s='temp/'+str(i)+'.jpg'
                            print(file_s)
                            b=upload(formatSource(file_s))
                            os.remove(file_s)
                            img_hc='<img src="'+b['image']['url']+'">'
                            
                            with open(str(t)+'.txt','a') as f:
                                f.write(img_hc)
                        print('上传完成，开始发布')
                        with open(str(t)+'.txt','r') as f:
                            wz_content=f.read()
                        a=wordpress_post(str(t),wz_content)
                        conn=a.mysql_con()
                        cursor = conn.cursor()
                        c=a.up()
                        effect_row = cursor.execute(c)
                        new_id = cursor.lastrowid
                        d=a.cat(new_id,'1')
                        effect_row = cursor.execute(d)
                        a.close_mysql(cursor,conn)
                        print('发布成功')
                    except:
                        continue
                else:
                    print('文件夹已存在，跳过')
        flag=flag+1
        print('这一页的任务已经完成了')
    else:
        get=requests.get('http://www.mm131.com/xinggan/list_6_'+str(flag)+'.html')
        if get.status_code==200:
            b=re.findall(r'<dd><a target="_blank" href="http://www.mm131.com/xinggan/([0-9]*).html"><img src=',get.text)
            for a in b:
                getpage=requests.get('http://www.mm131.com/xinggan/'+str(a)+'.html')
                if getpage.status_code==200:    
                    tittle=re.findall(r'<h5>(.*)</h5>',str(getpage.content,'gb2312',errors='ignore'))
                    pages=[]
                    threads=[]
                    pages=re.findall(r'<span class="page-ch">共(.*?)页</span>',str(getpage.content,'gb2312',errors='ignore'))
                    page=pages[0]
                    download_url='http://img1.mm131.me/pic/'+str(a)+'/'
                    for t in tittle:
                        if os.path.exists(str(t)+'.txt')==False:
                            try:
                                print('开始上传：'+t)
                                for page_img in range(int(page)):
                                    download_img_url=download_url+str(page_img)+'.jpg'
                                    thread=myThread(download_img_url,t,page_img)
                                    thread.start()
                                    threads.append(thread)
                                for ts in threads:
                                    ts.join()
                                for i in range(int(page)):
                                    file_s='temp/'+str(i)+'.jpg'
                                    print(file_s)
                                    b=upload(formatSource(file_s))
                                    os.remove(file_s)
                                    img_hc='<img src="'+b['image']['url']+'">'
                                
                                    with open(str(t)+'.txt','a') as f:
                                        f.write(img_hc)
                                print('上传完成，开始发布')
                                with open(str(t)+'.txt','r') as f:
                                    wz_content=f.read()
                                a=wordpress_post(str(t),wz_content)
                                conn=a.mysql_con()
                                cursor = conn.cursor()
                                c=a.up()
                                effect_row = cursor.execute(c)
                                new_id = cursor.lastrowid
                                d=a.cat(new_id,'1')
                                effect_row = cursor.execute(d)
                                a.close_mysql(cursor,conn)
                                print('发布成功')
                            except:
                                continue
                        else:
                            print('文件夹已存在，跳过')
                else:
                    continue
            flag=flag+1
            print('这一页的任务已经完成了')
        else:
            continue
       
