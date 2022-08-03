# flask 기본코드------------------------------
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import json
import jwt
import datetime
import hashlib

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
# 아래코드는 서버에 배포시
#client = MongoClient('mongodb://test:test@localhost', 27017) # Connection Setting시 유저 네임과 비밀번호를 입력해줘야되요 ex) MongoClient('mongodb://아이디:비번@localhost',27017)
db = client.mbti

# 성윤님 -----------------------------------------------------

# 병찬님 -----------------------------------------------------

# 민진님 -----------------------------------------------------

# HTML 보여주기
@app.route('/')
def home():
    return render_template('sign_up.html')

@app.route('/feature')
def feature_page():
    return render_template('feature_post.html')

@app.route('/discussion')
def discussion():
    return render_template('discussion_post.html')

# 테스트용 - 논의게시판 포스트 바로가기
@app.route('/discussion/post')
def discussion_page():
    return render_template('discussion_post_comments.html')

# < 특징 게시판 - 선택한 MBTI의 특징들 가져오기 API >
@app.route('/api/mbti_features_posts', methods=['POST'])
def select_mbti_feature():
    mbti_receive = request.form['mbti_give']
    features = list(db.Feature.find({'feature_mbti': mbti_receive},{'_id':False}).sort('like', -1))
    return jsonify({'the_mbti_features': features, 'msg': f'{mbti_receive}의 특징으로 이동합니다.'})

# < 논의 게시판 - 포스트 삭제 API >
@app.route('/api/free_posts', methods=['DELETE'])
def delete_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        post_id_receive = request.form['post_id_give']
        db.Post.delete_one({'user_id': payload['id'], 'Post._id': post_id_receive})
        return jsonify({'msg': '삭제 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# < 논의 게시판 - 댓글 불러오기 API >
@app.route('/api/comments', methods=['GET'])
def show_comments():
    post_id = request.args.get('post_id')
    comments = list(db.Comment.find({'': post_id}))
    return jsonify({'all_comments': comments})

# 수진님 -----------------------------------------------------

# 수민님 -----------------------------------------------------

# [논의 게시판 댓글 쓰기]
@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']

    doc = {
        'comment': comment_receive
    }

    db.comment.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})


@app.route("/comment", methods=["GET"])
def comment_get():
    comment_list = list(db.comment.find({}, {'_id': False}))
    return jsonify({'comments': comment_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)