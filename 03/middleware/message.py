#-*- coding:utf-8 -*-
import os, datetime, cgi, StringIO
from wsgiref import util, simple_server
from xml.sax import saxutils


class MessageBoard(object):
    ''' メッセージボードサービスを提供するアプリケーション '''

    def __init__(self):
        ''' 初期化 '''

        # メッセージを保存するリストを定義
        self.messages = []


    def __call__(self, environ, start_response):
        ''' WSGI アプリケーション '''

        # リクエストメソッドを取得
        method = environ['REQUEST_METHOD']

        if method == 'GET':
            # GET の場合
            return self.listMessages(environ, start_response)

        elif method == 'POST':
            # POST の場合
            return self.addMessage(environ, start_response)

        else:
            # それ以外の場合は 501 を返す
            start_response('501 Not Implemented', [('Content-type', 'text/plain')])
            return 'Not Implemented'


    def listMessages(self, environ, start_response):
        ''' 一覧表示 '''

        fp = StringIO.StringIO()

        # ヘッダを出力
        fp.write(r'''<html>
<head><title>Message Board</title>
<meta http-equiv="Content-type" content="text/html; charset=utf-8">
</head>
<body>
''')

        # メッセージ数分繰り返し
        for msg in reversed(self.messages):

            esc = saxutils.escape

            tmp = {}

            # 入力を全てエスケープして出力
            for key, value in msg.iteritems():
                value = str(value)
                tmp[key] = str(esc(unicode(value, 'utf-8', 'ignore')))


            # メッセージの内容を書き出す
            fp.write('''<dl>
<dt>title</dt>
<dd>%(title)s</dd>
<dt>name</dt>
<dd>%(name)s</dd>
<dt>date</dt>
<dd>%(date)s</dd>
<dt>message</dt>
<dd>%(body)s</dd>
</dl><hr />''' % tmp)

        # 書込み用フォームを出力
        fp.write('''<form action="%s" method="POST" AcceptEncoding="utf-8">
<dl>
<dt>name</dt>
<dd><input type="text" name="name"/></dd>
<dt>title</dt>
<dd><input type="text" name="title"/></dd>
<dt>body</dt>
<dd><textarea name="body"></textarea></dd>
</dl>
<input type="submit" name="save" value="Post" />
</form>
</body></html>''' % util.request_uri(environ))

        # シーク位置を先頭にしておく
        fp.seek(0)

        start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
        return fp


    def addMessage(self, environ, start_response):
        ''' メッセージを追加する '''

        # POST データを取得
        inpt = environ['wsgi.input']
        length = int(environ.get('CONTENT_LENGTH', 0))

        # 取得したデータをパースして辞書オブジェクトに変換
        query = dict(cgi.parse_qsl(inpt.read(length)))
        
        # POST メッセージを保存
        msg = {'name':query['name'],
               'title':query['title'],
               'body':query['body'],
               'date':datetime.datetime.now()}

        self.messages.append(msg)

        # リダイレクトを行う
        start_response('303 See Other', [('Content-type', 'text/plain'),
                                         ('Location', util.request_uri(environ))])

        return ''



from wsgiref import simple_server

application = MessageBoard()


if __name__ == '__main__':

    srv = simple_server.make_server('', 8080, application)

    srv.serve_forever()

    
