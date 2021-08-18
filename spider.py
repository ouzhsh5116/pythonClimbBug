# -*- codeing = utf-8 -*-
# @Time : 2021/8/7 15:45
# @Author : ozs
# @File : spider.py
# @Software : PyCharm


from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式，文字匹配
import urllib.error, urllib.request  # 指定url获取网页数据
import xlwt  # excel操作
import sqlite3  # 数据库操作

'''
    1.爬取网页
    2.解析网页
    3.保存数据
'''


def main():
    baseUrl = "https://movie.douban.com/top250?start="
    # 1.爬取网页
    dataList = getData(baseUrl)
    # savePath = "豆瓣电影Top250.xls"
    dbPath = "movie.db"
    # 3.保存数据
    # saveData(dataList, savePath)
    saveData2DB(dataList, dbPath)


findLink = re.compile(r'<a href="(.*?)">')  # 创建正则表达式规则
findName = re.compile(r'<span class="title">(.*?)</span>')  # 创建查找电影名的正则表达式
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')  # 评分
findCommentP = re.compile(r'<span>(\d*)人评价</span>')  # 评价人数
findInq = re.compile(r'<span class="inq">(.*?)</span>')  # 概要
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 通过url获取网页的数据
def getData(baseurl):
    dataList = []
    for i in range(0, 10):  # 获取10次页面的html源码信息
        url = baseurl + str(i * 25)
        html = askURL(url)

        # 2.解析网页数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):  # 查找复合要求的字符串，形成列表
            # print(item)  # 查看一个电影item的全部信息
            data = []  # 保存电影的全部信息
            item = str(item)

            # 获取连接
            link = re.findall(findLink, item)[0]
            data.append(link)
            # 获取图片
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)
            # 获取电影名
            name = re.findall(findName, item)
            if (len(name) == 2):
                ctitle = name[0]
                data.append(ctitle)
                otitle = name[1].replace("/", "")  # 去斜杆
                data.append(otitle)
            else:
                data.append(name[0])
                data.append('')

            # 评分
            rating = re.findall(findRating, item)[0]
            data.append(rating)

            CommentP = re.findall(findCommentP, item)[0]
            data.append(CommentP)

            inq = re.findall(findInq, item)

            if (len(inq) != 0):
                inq = inq[0].replace("。", "")
            else:
                inq = ''
            data.append(inq)

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)  # 替换字符串
            bd = re.sub('/', " ", bd)
            bd = re.sub(r'\xa0', "", bd)
            bd = bd.strip()  # 去掉前后空格
            data.append(bd)
            dataList.append(data)  # 处理完的一部电影放到dataList
    return dataList


# 获取单个url的网页信息
def askURL(url):
    # 伪装浏览器访问
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    }
    req = urllib.request.Request(headers=header, url=url)
    html = ""
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    html = response.read().decode("utf-8")
    return html


def saveData(dataList, savePath):
    '''
    保存数据
    :param savePath:
    :return:
    '''
    print("save...")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet("豆瓣Top250", cell_overwrite_ok=True)
    col = ('电影详情链接', '图片链接', '影片中文名', '外文名', '评分', '评分数', '概况', '相关信息')
    for i in range(0, 8):
        sheet.write(0, i, col[i])  # 列名

    for i in range(0, 250):
        for j in range(0, 8):
            sheet.write(i + 1, j, dataList[i][j])
    book.save(savePath)
    print("...")


# 创建数据库
def init_db(dbPath):
    sql = '''
        create table movie250(
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric ,
        rated numeric ,
        instroduction text,
        info text
        )
    '''
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()


def saveData2DB(dataList, dbPath):
    sql = ""
    init_db(dbPath)
    con = sqlite3.connect(dbPath)
    cur = con.cursor()

    for data in dataList:
        for index in range(len(data)):
            if(index==4 or index == 5):
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''insert into movie250(info_link,pic_link,cname,ename,score,rated,instroduction,info) values (%s)''' % (",".join(data))
        print(sql)
        cur.execute(sql)
        con.commit()
    cur.close()
    con.close()


if __name__ == "__main__":  # 程序执行时的入口函数 默认是main （当程序执行到名字是main的时候）
    main()
