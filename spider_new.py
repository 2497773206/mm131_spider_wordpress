import mimetypes,json
import requests
import re,os,threading,time,pymysql
class wordpress_post:
    def __init__(self,tittle,content):
        self.tittle=tittle
        self.content=content
    def mysql_con(self):
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pwd', db='wordpress', charset='utf8') #在此修改数据库信息
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
    APIKey = "apikey" #在此修改apikey
    format = "json"
    url = "https://domain.com/api/1/upload/?key="+ APIKey + "&format=" + format #在此修改图床地址
    r = requests.post(url, files = files)
    time.sleep(1)
    return json.loads(r.text)
def formatSource(filename):
    imageList = []
    type = mimetypes.guess_type(filename)[0]
    imageList.append(('source' , (filename , open(filename , 'rb') , type)))
    return imageList
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
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':'http://www.mm131.com/'}
    req=requests.get(url=url,headers=headers)
    if req.status_code==200:
        with open('temp/'+str(filename)+'.jpg','wb') as f:
            f.write(req.content)

def get_page_url_info(flag):
    infos=[]
    if flag==1:
        url='http://www.mm131.com/xinggan/'
    else:
        url='http://www.mm131.com/xinggan/list_6_'+str(flag)+'.html'
    get=requests.get(url)
    infos=re.findall(r'<dd><a target="_blank" href="http://www.mm131.com/xinggan/([0-9]*).html"><img src=',get.text)
    print(infos)
    return infos
def get_page_img_info(a):
    getpage=requests.get('http://www.mm131.com/xinggan/'+str(a)+'.html')
    tittle=re.findall(r'<h5>(.*)</h5>',str(getpage.content,'gb2312',errors='ignore'))
    pages=re.findall(r'<span class="page-ch">共(.*?)页</span>',str(getpage.content,'gb2312',errors='ignore'))
    return tittle,pages
def get_img(a,page,tittle):
    threads=[]
    download_url='http://img1.mm131.me/pic/'+str(a)+'/'
    for t in tittle:
            print('开始上传：'+t)
            for page_img in range(int(page)):
                download_img_url=download_url+str(page_img)+'.jpg'
                thread=myThread(download_img_url,t,page_img)
                thread.start()
                threads.append(thread)
                for ts in threads:
                    ts.join()
           
def upload_img(page,tittle):
    print(tittle[0])
    for i in range(int(page)):
        file_s='temp/'+str(i)+'.jpg'
        print(file_s)
        b=upload(formatSource(file_s))
        os.remove(file_s)
        img_hc='<img src="'+b['image']['url']+'">'       
        with open('temp/temp.txt','a+') as f:
            f.write(img_hc)
def post_article(info,tittle):
    with open('temp/log.txt','a+') as f:
        f.write(str(info)+'\n')
    with open('temp/temp.txt','r') as f:
        wz_content=f.read()
    os.remove('temp/temp.txt')
    a=wordpress_post(str(tittle[0]),wz_content)
    conn=a.mysql_con()
    cursor = conn.cursor()
    c=a.up()
    effect_row = cursor.execute(c)
    new_id = cursor.lastrowid
    d=a.cat(new_id,'1')
    effect_row = cursor.execute(d)
    a.close_mysql(cursor,conn)
def main():
    flag=1
    while True:
        
        try:
            info_s=get_page_url_info(flag)
        except:
            print('获取初始信息错误')
            continue
        for info in info_s:
            img_info=[]
            img_tittle=[]
            img_page=[]
            with open('temp/log.txt','r') as f:
                b=f.read()
                
                if info not in b:
                    try:
                        img_info=get_page_img_info(info)
                    except:
                        print('获取图片信息出错')
                        continue
                    img_tittle=img_info[0]
                    img_page=img_info[1]
                    try:
                        get_img(info,img_page[0],img_tittle)
                    except:
                        print('下载图片出错')
                        continue
                    try:
                        upload_img(img_page[0],img_tittle)
                    except:
                        print('图床错误')
                        continue
                    post_article(info,img_tittle)
                else:continue
        flag+=1
if __name__='__main__':
    try:
        main()
    except:
        print('程序运行错误，请重新运行脚本')
