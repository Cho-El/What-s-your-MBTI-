# flask 기본코드------------------------------
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
app = Flask(__name__)

import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
# 아래코드는 서버에 배포시
#client = MongoClient('mongodb://test:test@localhost', 27017) # Connection Setting시 유저 네임과 비밀번호를 입력해줘야되요 ex) MongoClient('mongodb://아이디:비번@localhost',27017)
db = client.mbti

# HTML 보여주기 - 수민 + 민진 -------------------------------------
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('feature_post.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("start", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("start", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/start')
def start():
    msg = request.args.get("msg")
    return render_template('sign_up.html', msg=msg)

# discussion_post.html 렌더링
@app.route('/discussion_post')
def discussion():
    discussion_posts = list(db.Post.find({},{'_id':False}))
    return render_template('discussion_post.html', discussion_posts = discussion_posts)


# 성윤님 -----------------------------------------------------

# discussion_post_comments.html 렌더링
# 성윤님꺼와 충돌 ------------------------------------ 성윤님이 구현하신 기능 있는지 확인
@app.route('/discussion_post/<post_id>')
def discussion_post_comments(post_id):
    post_info = list(db.Post.find({'post_id': post_id}, {'_id': False}))
    comments = list(db.Comment.find({'post_id':post_id}, {'_id':False}))
    return render_template('discussion_post_comments.html', post_info = post_info, comments = comments)

# 병찬님 -----------------------------------------------------
@app.route('/discussion_post_add')
def discussion_post_add():
    return render_template('discussion_post_add.html')

@app.route('/discussion_post_back')
def discussion_back():
    return render_template('discussion_post.html')


@app.route('/discussion_post_complete')
def discussion_post():
    return render_template('discussion_post.html')

@app.route("/api/mbti_features_posts", methods=["POST"])
def board_post():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms = ['HS256'])
        user_info = payload["id"]
        post_title_receive = request.form['post_title_give']
        post_content_receive = request.form['post_content_give']

        doc = {
            'user_id': user_info,
            'post_title': post_title_receive,
            'post_content': post_content_receive
        }
        db.free_posts.insert_one(doc)
        return jsonify({"result":"success",'msg':"성공"})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/api/comments", methods=["PUT"])
def modify_comment():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms = ['HS256'])
        post_id = request.args.get('post_id')
        user_info = payload["id"]
        modify_comment_receive = request.form['modify_comment_give']

        db.Post.update_one({'post_id': post_id, 'user_id': user_info}, {'$set': {'comment_content': modify_comment_receive}})
        return jsonify({"result": "success", 'msg': "성공"})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 민진님 -----------------------------------------------------

# < 특징 게시판 - 선택한 MBTI의 특징들 가져오기 API >  ---------  삭제??? 성윤님이 이미 구현한 기능??
@app.route('/api/mbti_features_posts', methods=['POST'])
def select_mbti_feature():
    mbti_receive = request.form['mbti_give']
    features = list(db.Feature.find({'feature_mbti': mbti_receive},{'_id':False}).sort('like', -1))
    return jsonify({'the_mbti_features': features, 'msg': f'{mbti_receive}의 특징으로 이동합니다.'})

# < 논의 게시판 - 포스트 삭제 API >
@app.route('/api/free_posts', methods=['DELETE'])
def delete_post():
    post_id_receive = request.form['post_id_give']
    db.Post.delete_one({'post_id': post_id_receive})
    return jsonify({'msg': '삭제 완료!'})

# < 논의 게시판 - 댓글 불러오기 API >
@app.route('/api/comments', methods=['GET'])
def show_comments():
    post_id = request.args.get('post_id')
    comments = list(db.Comment.find({'': post_id}))
    return jsonify({'all_comments': comments})

# 수진님 -----------------------------------------------------

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# 로그인 API
@app.route('/api/login', methods=['POST'])
def log_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.User.find_one({'user_id': username_receive, 'user_pw': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입 API
@app.route('/api/signup/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    mbti_receive = request.form['mbti_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_id": username_receive,                               # 아이디
        "user_pw": password_hash,                                  # 비밀번호
        "user_nickname": nickname_receive,                          # 닉네임
        "user_mbti": mbti_receive                                  # mbti
    }
    db.User.insert_one(doc)
    return jsonify({'result': 'success'})

# 중복확인 API
@app.route('/api/signup/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.User.find_one({"user_id": username_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

# 수민님 -----------------------------------------------------
# [논의 게시판 게시글 수정 바로 가기]
@app.route('/discussion/post/comments')
def discussion_page():
    return render_template('discussion_post_add.html')

# [논의 게시판 댓글 쓰기]
@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']

    doc = {
        'comment': comment_receive
    }

    db.Comment.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})


@app.route("/comment", methods=["GET"])
def comment_get():
    comment_list = list(db.Comment.find({}, {'_id': False}))
    return jsonify({'comments': comment_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)