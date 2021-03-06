# coding:utf-8
import urllib.parse
import video_parse
import random
#import datetime
#from db.db_insert import 
from datetime import datetime, date, timedelta
import pytz

### 評価すべき動画の基準 ###
# 投稿されてから2年以内か
DATE = 365 * 2
# 再生数が15000以内か
VIEW = 15000
# 再生数とマイリスト割合が1.5%以上か
VIEW_MYLIST_PER = 1.5

"""
現在新しく投稿されている動画IDを取得する(smXXXXXXXX,soXXXXXXXX,nmXXXXXXXX)
@returns {str} - 最新の動画ID
"""
def new_video_search():
    keyword_set = "アニメ OR ゲーム OR 実況プレイ動画 OR 東方 OR アイドルマスター OR ラジオ OR 描いてみた OR TRPG OR\
                エンターテイメント OR 音楽 OR 歌ってみた OR 演奏してみた OR 踊ってみた OR VOCALOID OR ニコニコインディーズ OR ASMR OR MMD OR バーチャル OR\
                動物 OR 料理 OR 自然 OR 旅行 OR スポーツ OR ニコニコ動画講座 OR 車載動画 OR 歴史 OR 鉄道 OR\
                科学 OR ニコニコ技術部 OR ニコニコ手芸部 OR 作ってみた OR\
                政治 OR\
                例のアレ OR その他 OR 日記"
    # カテゴリタグから最新の動画をJSON形式で取得
    new_video_url = 'http://api.search.nicovideo.jp/api/v2/video/contents/search?q=' + urllib.parse.quote(keyword_set) + '&targets=tagsExact&fields=contentId&_sort=' + urllib.parse.quote("-") + 'startTime&_limit=100'
    # JSON形式からreadできる形式に変換
    json_video = video_parse.Json_VideoData(new_video_url)
    json_video_data = json_video.video_parse()
    # parseして動画IDを返す
    return json_video_data['data'][0]['contentId']


"""
最新動画IDからランダムで動画IDを取得する(smXXXXXXXX,soXXXXXXXX,nmXXXXXXXX)
@param {str} videoID 動画ID
@returns {str} ランダムで取得した動画ID
"""
def rand_video_search(videoID):
    # 動画IDの形式(sm,so,nm)を切り取る
    videoID = videoID[2:]

    for i in range(1, 10000):
        rand_videoID = random.randint(1, int(videoID))
        format_rand_videoID = format_video_search(rand_videoID)
        if format_rand_videoID == "novideo":
            continue
        else:
            print ("------------------------------")
            format_videoID = format_rand_videoID + str(rand_videoID)
            video_eval_analysis = Video_Eval(format_videoID)
            # 調べる動画の日付取得し、期間内に投稿されたか調べる
            date_video = video_eval_analysis.date_video()
            date_ans = Video_Eval.date_analysis(date_video)
            # 調べる動画の再生数取得し、基準内か調べる
            view_video = video_eval_analysis.view_video()
            view_ans = Video_Eval.view_analysis(view_video)
            # 調べる動画のマイリスト数取得し、再生数とマイリスト数の割合が基準以上か調べる
            vi_my_per_video = video_eval_analysis.vi_my_per_video()
            vi_my_per_ans = video_eval_analysis.vi_my_per_analysis(vi_my_per_video)
            


            if date_ans == True and view_ans == True and vi_my_per_ans == True:
                print(format_videoID)
                #video_eval_analysis = Video_Eval("sm32652273")
                #video_eval_analysis.tag()
                return format_videoID
            else:
                continue


"""
動画IDから形式を取得する(sm,so,nm)
@param {str} videoID 形式を省いた動画ID
@returns {str} 取得した形式(取得できなかったら消去・非公開にされているため、"novideo"を返す)
"""
def format_video_search(videoID):
    # 形式がsmか判定
    # XML形式からreadできる形式に変換
    xml_video = video_parse.XML_VideoData("http://ext.nicovideo.jp/api/getthumbinfo/sm", str(videoID))
    root = xml_video.video_parse()

    if "sm" in str(root[0][0].text):
        return "sm"
    # 形式がsoか判定
    else:
        # XML形式からreadできる形式に変換
        xml_video = video_parse.XML_VideoData("http://ext.nicovideo.jp/api/getthumbinfo/so", str(videoID))
        root = xml_video.video_parse()

        if "so" in str(root[0][0].text):
            return "so"
        # 形式がnmか判定
        else:
            # XML形式からreadできる形式に変換
            xml_video = video_parse.XML_VideoData("http://ext.nicovideo.jp/api/getthumbinfo/nm", str(videoID))
            root = xml_video.video_parse()

            if "nm" in str(root[0][0].text):
                return "nm"

            else:
                return "novideo"


class Video_Eval:
    def __init__(self, videoID):
        # XML形式からreadできる形式に変換
        xml_video = video_parse.XML_VideoData("http://ext.nicovideo.jp/api/getthumbinfo/", str(videoID))
        xml = xml_video.video_parse()
        self.xml = xml

    def date_video(self):
        # XML形式から取得した投稿日付を日付型に変換 (xml[0][4].text: %Y-%m-%dT%H:%M:%S+09:00 -> %Y-%m-%d %H:%M:%S)
        date = self.xml[0][4].text
        date = date[:-6]
        date = date.replace('T', ' ') 
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return date
    def date_analysis(date):
        if 7 <= (datetime.today()-date).days <= DATE:
            print("[date]True:{0}".format(date))
            return True
        else:
            print("[date]False:{0}".format(date))
            return False

    def view_video(self):
        # XML形式から再生数取得する
        view = int(self.xml[0][9].text)
        return view
    def view_analysis(view):
        if view <= VIEW:
            print("[view]True:{0}".format(view))
            return True
        else:
            print("[view]False:{0}".format(view))
            return False

    def vi_my_per_video(self):
        # XML形式から再生数マイリスト数取得する
        view = int(self.xml[0][9].text)
        mylist = int(self.xml[0][11].text)
        vi_my_per = mylist / view * 100
        return vi_my_per
    def vi_my_per_analysis(self, vi_my_per):
        mylist = int(self.xml[0][11].text)
        if mylist >= 3 and vi_my_per >= VIEW_MYLIST_PER:
            print("[vi_my_per]True:{0}".format(vi_my_per))
            return True
        else:
            print("[vi_my_per]False:{0}".format(vi_my_per))
            return False

    def tag_video(self):
        video_tags = list()

        tmp_tag = self.xml[0][17][0].text

        video_tags.append(str(tmp_tag))
        print(video_tags[0])
        
        return video_tags
    
    def title_video(self):
        return self.xml[0][1].text