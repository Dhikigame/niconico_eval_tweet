# coding:utf-8
from datetime import datetime, date, timedelta
import sys
sys.path.append('..')
import video_search  as vs
import sqlite3
from contextlib import closing


def db_insert(videoID):
    # タグを取得
    video_info_get = vs.Video_Eval(videoID)
    video_tags = video_info_get.tag_video()
    # 投稿日時を取得
    video_date = video_info_get.date_video()
    # タイトルを取得
    video_title = video_info_get.title_video()

    db = sqlite3.connect('./db/video_eval.db')

    with closing(db) as con:
        c = con.cursor()
        cursor = db.cursor()

        # DBに同じ動画IDがあるかFetchする
        sql = 'select video_id from video_eval_data where video_id == "' +  videoID + '"'
        cursor.execute("select video_id from video_eval_data where video_id = ?", (videoID,))
        exist = cursor.fetchone()
        # DBに同じ動画IDがなければ挿入する
        if exist is None:
            sql = 'insert into video_eval_data(video_id, title, regist_date, upload_date, tag) values (?,?,?,?,?)'
            data = (videoID, video_title, datetime.today(), video_date, video_tags[0])
            c.execute(sql, data)
            con.commit()
            print("insert:{0}".format(videoID))

            select_sql = 'select * from video_eval_data'
            for row in c.execute(select_sql):
                print(row)
        else:
            select_sql = 'select * from video_eval_data'
            for row in c.execute(select_sql):
                print(row)