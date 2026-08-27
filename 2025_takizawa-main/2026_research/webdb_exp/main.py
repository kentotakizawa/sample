from flask import Flask, render_template, request, session
import psycopg2
import uuid
import settings

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())  # セッションの暗号化に使用するキーを設定

TIME_LIMIT = 15  # 分
TIME_INTERVAL = 20  # 秒
COUNT_LIMIT = int(TIME_LIMIT * 60 / TIME_INTERVAL)  # 自動送信の回数制限


def db_insert(sql, args):
    """データベースにSQL文を実行する関数"""
    conn = psycopg2.connect(**settings.PG_CONF)
    with conn.cursor() as cur:
        cur.execute(sql, args)
        conn.commit()
    conn.close()


@app.route('/')
def start_page():
    task_id = request.args.get('task_id', '0')  # トピック番号を取得
    return render_template('index.html', task_id=task_id, time_limit=TIME_LIMIT)


@app.route('/main', methods=['POST'])
def main_page():
    """実験協力者の情報をデータベースに登録し、実験ページを表示する関数"""
    _uuid = str(uuid.uuid4())
    cw_id = request.form.get('cw_id', 'empty')  # 協力者IDを取得
    task_id = int(request.form.get('task_id', '-1'))  # トピック番号を取得

    db_insert(
        "INSERT INTO takizawa.webdb2026_participant (uuid, cw_id, task_id) VALUES (%s, %s, %s)",
        (_uuid, cw_id, task_id),
    )

    if task_id == 0:
        topic_name = "ダミータスク0"
    elif task_id == 1:
        topic_name = "飢餓をゼロ：食料価格の極端な変動に歯止めをかけるため、食料市場及びデリバティブ市場の適正な機能を確保するための措置を講じ、食料備蓄などの市場情報への適時のアクセスを容易にする。"
    elif task_id == 2:
        topic_name = "質の高い教育をみんなに：2030年までに、技術的・職業的スキルなど、雇用、働きがいのある人間らしい仕事及び起業に必要な技能を備えた若者と成人の割合を大幅に増加させる。"
    elif task_id == 3:
        topic_name = "働きがいも経済成長も：2030年までに、雇用創出、地方の文化振興・産品販促につながる持続可能な観光業を促進するための政策を立案し実施する。"
    elif task_id == 4:
        topic_name = "平和と公正をすべての人に：子供に対する虐待、搾取、取引及びあらゆる形態の暴力及び拷問を撲滅する。"

    session['uuid'] = _uuid  # 協力者のUUIDをセッションに保存
    session['save_num'] = 0  # 協力者の保存回数をセッションに保存

    return render_template('main.html', time_limit=TIME_LIMIT, time_interval=TIME_INTERVAL, topic_name=topic_name)


def common_submit(session, request):
    """メインページの入力内容を取得し、データベースに保存する関数"""
    _uuid = session.get('uuid', None)
    content = request.form.get('content', None)
    url = request.form.get('url', None)
    save_num = session.get('save_num', 0) + 1

    db_insert(
        "INSERT INTO takizawa.webdb2026_inputlog (uuid, save_num, content, url) VALUES (%s, %s, %s, %s)",
        (_uuid, save_num, content, url),
    )

    session['save_num'] = save_num  # 協力者の保存回数


@app.route('/auto_submit', methods=['POST'])
def auto_submit():
    """メインページの入力内容を定期的に取得し、データベースに保存する関数"""
    common_submit(session, request)

    # 20分（1200秒）経過したら 286 を返して htmx のタイマーを停止させる
    if session.get('save_num', 0) >= COUNT_LIMIT:
        return '', 286
    else:
        return '', 204


@app.route('/submit', methods=['POST'])
def submit():
    """メインページの入力内容を取得し、データベースに保存する関数"""
    common_submit(session, request)

    return render_template('end.html', completion_code=session.get('uuid', None))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5000, threaded=True)
