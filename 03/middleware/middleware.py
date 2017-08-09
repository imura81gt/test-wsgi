#-*- coding:utf-8 -*-

import wsgiref, StringIO, datetime
from wsgiref import util


class Nop(object):
    ''' 何もしないミドルウェア (クラス版) '''
    
    def __init__(self, application):
        self.application = application


    def __call__(self, environ, start_response):
        return self.application(environ, start_response)



def notFound(environ, start_response):

    start_response('404 NotFound', [('Content-type', 'text/plain')])

    return '%s is not found' % util.request_uri(environ)



class SelectApp(object):
    ''' パスによるアプリケーション振り分けを行う '''

    def __init__(self, table, notfound=notFound):

        # パスは長い順にマッチさせたいので、あらかじめソートしておく
        tmp = sorted(table, key=lambda x:len(x), reverse=True)

        # 扱いやすいように、タプルのリストにしておく
        table = [(x, table[x]) for x in tmp]

        self.table = table

        # 割り振るパスが見つからなかったときに呼び出すアプリケーション
        self.notfound = notfound


    def __call__(self, environ, start_response):
        ''' リクエストのパスを見て振り分ける '''

        name = 'SCRIPT_NAME'
        info = 'PATH_INFO'

        scriptname = environ.get(name, '')
        pathinfo = environ.get(info, '')

        for p, app in self.table:

            if p == '' or p == '/' and pathinfo.startswith(p):
                return app(environ, start_response)

            # 同じパスならそのまま
            # 同じパスで始まっていて、その後にスラッシュがある
            if pathinfo == p or pathinfo.startswith(p) and \
                    pathinfo[len(p)] == '/':

                scriptname = scriptname + p
                pathinfo = pathinfo[len(p):]

                # リクエスト情報を書き換える
                environ[name] = scriptname
                environ[info] = pathinfo

                return app(environ, start_response)

        return self.notfound(environ, start_response)



if __name__ == '__main__':

    from wsgiref import simple_server
    import sample1, message

    # /message に MessageBoard を、 /hello に Hello, world を割り当て
    application = SelectApp({'/message':message.MessageBoard(),
                             '/hello':sample1.application})

    # 何もしないミドルウェアを使用
    application = Nop(application)

    srv = simple_server.make_server('', 8080, application)
    srv.serve_forever()
