# 下記コードを参考(Flask 公式リファレンス)
# Patterns for Flask(Uploading Files)：https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

# request：フォームから送信されたデータの処理に使用：
# request 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/api/?highlight=request#flask.request
# redirect：ページの移動に使用
# url_for：ページ遷移の際のURLを指定
# secure_filename：ハックの危険が無いかファイル名をチェックするのに使用
from flask import send_from_directory
import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

# result.htmlでの画像表示用
# 保存せずに表示するために、htmlのimgタグの仕様を利用時、base64で変換した画像情報を与えて表示させる
import io
import base64


# 以下は推論用ライブラリのimport
from keras.models import Sequential, load_model
import keras
import numpy as np
from PIL import Image

# フォームで送信された画像の格納パスを定数で定義
#　※定数定義は慣例的に大文字で書く
UPLOAD_FOLDER = './uploads'

# 受け入れる拡張子をセットで定義
ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}

# Flaskの初期化
# ※FlaskはPython標準インターフェース定義であるWSGI(ウィズギー：Web Server Gateway Interface)を利用している。
# 　WSGIではサーバがクライアントとやり取りする際にcallableオブジェクト(__call__ が定義されたオブジェクト)を用いるが、
# 　FlaskではFlaskクラスがcallableオブジェクトにあたるため、必ず定義しなければならない。
# 　また、FlaskはPythonグローバル変数の__name__を元に動作するため、それを引数として渡す必要がある。
app = Flask(__name__)


# flash用にsecret keyを設定　※これが無いとflashが動かない
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# config(辞書型)でFlaskアプリケーションの設定を追加する。標準で定義されている設定もある。
# 日本語公式リファレンス(旧)：https://a2c.bitbucket.io/flask/config.html
# 公式リファレンス(最新)：https://flask.palletsprojects.com/en/1.1.x/config/
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ファイルのアップロード可否判断
def allowned_file(filename):

    # ファイル名にピリオドがあるか(拡張子があるか)、その拡張子が受け入れ拡張子セットに含まれているものかを検証
    # and条件の二つ目は、ファイル名を右から「.」でsplitし、二個目の要素を取得(拡張子の名前を取得)し、受け入れ拡張子セットにあるか確認している
    # rsplit 公式リファレンス：https://docs.python.org/ja/3/library/stdtypes.html?highlight=rsplit#str.rsplit
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @(デコレート)について：Helloworldをrouteメソッドでデコレートし、route関数内でhello_worldメソッドが実行されるようにする
# 参考：https://qiita.com/mtb_beta/items/d257519b018b8cd0cc2e#fn1

# routeメソッドの引数に渡したURL('/'はサーバのページ最上層)にGET/POSTでアクセスされたら、下記のメソッドを実行する
# route() 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/api/?highlight=route#flask.Flask.route
# route()及びその他方法によるURL Route Registrations：https://flask.palletsprojects.com/en/1.1.x/api/?highlight=route#url-route-registrations
@app.route('/', methods=['GET', 'POST'])
def upload_file():

    # POSTだった場合、ファイルが添付されているかを判断
    if request.method == 'POST':

        # リクエストにファイルがなければflashメソッドを用いflashメッセージでその旨を出し、元のページへ遷移させる
        #　※request.filesには、input type="file"のformのname要素の値と渡されたファイルがMultiDicで格納されている。
        # 　最下部で定義しているHTMLのformでnameに"file"を指定しているため、そのformから渡されたファイルがあるかを見ている。
        # flash 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
        # request.files 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/api/?highlight=files#flask.Request.files
        if 'file' not in request.files:
            flash('ファイル部分のデータがありません')
            return redirect(request.url)

        # リクエストで、HTMLの<input type=file name=file>のフォームから渡されたファイルを変数に格納
        file = request.files['file']

        # リクエストのファイルにファイル名が無ければ、同様にメッセージを出し、元のページへ遷移させる
        if file.filename == '':
            flash('ファイルが選択されていません')
            return redirect(request.url)

        #　変数fileの中に値が存在し、かつ上述した許容拡張子であるかをIF判断→セキュアなファイル名かを検証
        # ※変数fileはrequest.files(FileStorage型)であるため、下記リファレンスのフィールドが使える
        # 　Werkzeug FileStorage object　公式リファレンス：https://werkzeug.palletsprojects.com/en/0.16.x/datastructures/#werkzeug.datastructures.FileStorage
        if file and allowned_file(file.filename):
            filename = secure_filename(file.filename)

            # os.path.joinメソッドでsaveメソッドに渡すパスを生成(引数を結合して'/'を補完しパスを作成する)し、
            # saveメソッドに与えたパスにファイルを保存
            # os.path.join　公式リファレンス：https://docs.python.org/ja/3/library/os.path.html?highlight=os%20path%20join#os.path.join
            # save 公式リファレンス：https://werkzeug.palletsprojects.com/en/0.16.x/datastructures/#werkzeug.datastructures.FileStorage
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # file.save(filepath)

            # 推論し、結果をreturnしていく

            #動物のラベル (取得した動物種)
            classes = ["サル", "イノシシ", "カラス"]

            # 変換後の画像ピクセル数
            image_size = 50

            # PillowのImageクラスで画像を開き加工していく
            # 公式リファレンス：https://pillow.readthedocs.io/en/stable/
            #image = Image.open(filepath)
            image = Image.open(file)
            image_clear = image
            #image = Image.open('crow_pretest.jpg')

            # 256階調のRGB色へ画像色を変換
            # 公式リファレンス：https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.convert
            image = image.convert("RGB")

            # 画像サイズを50×50ピクセルに揃える
            # ※ダウンロードしてきた画像は150×150ピクセルだが、計算高速化のために50×50ピクセルに変換する
            image = image.resize((image_size, image_size))

            # TensorFlow用に、Listからndarray型への変換&255で正規化　※この場合は特にnp.array()の変換と動きは変わらない
            # なお、ndarray型→ndarray型への変換(この場合はコピーの動作をする)を行うと、
            # 変換(コピー)元の配列に対する変更が変換(コピー)後の配列にも適用される
            data = np.asarray(image)/255

            # predictメソッドに渡すための配列を定義
            X = []

            # 先ほど定義した配列に入力されてきた画像データを格納し、predictメソッドへ渡すためndarray型へ変換
            X.append(data)
            X = np.array(X)

            # 自作のbuild_modelメソッドでモデル定義と学習済みの重みをロードし、推論用modelを構築
            model = load_model('./animal_cnn_aug2.h5')

            # kerasのpredictメソッドを用い、推論処理を行い、結果を変数へ格納
            # 公式リファレンス：
            result = model.predict([X])[0]

            # 推論された値の中で最も値が大きいもの(正解思われるもの)のインデックスを格納
            predicted = result.argmax()

            # ソフトマックス関数を用いているため、結果を百分率に変換し、ラベル名と値を表示
            percentage = int(result[predicted] * 100)

            # アップロードされた画像をresult.html表示するために変換
            # 参考：https://teratail.com/questions/89341
            encode_image = base64.b64encode(
                image_to_byte_array(image_clear)).decode("utf-8")
            encode_image = f'data:image/JPEG;base64,{encode_image}'

            return render_template('result.html', classes=classes, predicted=predicted, encode_file=encode_image, percentage=percentage)

            # url_forメソッドでfilename変数の値を用いて動的にURLを生成し、それを用いてredirectメソッドでページを遷移させる
            # url_for：第一引数として与えられた関数から返却された値と、第二引数以降に渡された変数を用いてURLを生成する
            # url_for 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/api/?highlight=url_for#flask.url_for
            # url_forを用いたURL Building：https://flask.palletsprojects.com/en/1.1.x/quickstart/#url-building
           # return redirect(url_for('uploaded_file', filename=filename))

    # form enctype：エンコードタイプの略。form methodがPOSTの時のみ使え、formの送信データのエンコード方法を表す。
    # multipart/form-dataは複数の種類のファイルを送信するの意。
    # ※他にも全ての文字をURLエンコード(application/x-www-form-urlencoded)したり、
    # 　スペースのみを「+」にするエンコード(text/plain)がある。

   # 下記ではflashメッセージが出ないので使用しない
   # return
    '''
    <!doctype html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Upload new File</title>
    </head>
    <body>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file></p>
      <p><input type=submit value=Upload></p>
    {%set message = get_flashed_messages() %}
    {%if message%}
    <p>{{messages}}</p>
    </form>
    </body>
    </html>
    '''

    # 下記でjinja2 Templateを用いてレンダリングすれば、flashが表示されるようになる。
    # 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
    # jinja2のTemplateを用いたファイルは必ずtemplatesフォルダに格納すること。jinja2のフレームワークでの決まりらしい。
    return render_template('index.html')


# ディレクトリにあるファイルをブラウザ送信(表示)する
# send_from_directory：引数で与えられたディレクトリからファイルを送る
# 公式リファレンス：https://flask.palletsprojects.com/en/1.1.x/api/?highlight=send_from_directory#flask.send_from_directory
# route()追加情報： <>(angular brackets：山かっこ)を用いると、メソッドに渡された変数値をそこにいれることができる。
# 　※型の変換も可能。例：<string:filename>
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Pillowのimage型をbyte型へ変換
# アップロードされた画像をresult.html表示するために、byte型→base64型への変換が必要なため


def image_to_byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='JPEG')
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr
