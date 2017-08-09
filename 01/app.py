# -*- coding: utf-8 -*-
from __future__ import print_function
from wsgiref import simple_server

#この関数がwsgiに準拠した書き方をされているらしい
# * environ: dictオブジェクト。クライアントから送られてきたリクエスト情報が入っている。
# *
def application(environ, start_response):
    for key, value in environ.iteritems():
        print(key, value)
    start_response('200 OK', [('Content-type', 'text/plan')])
    return 'Hello, WSGI!'

if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
