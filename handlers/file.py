from bottle import route, static_file


@route('/favicon.ico')
def favicon(app):
    return static_file('favicon.ico', root='files')


@route('/files/<filename>')
def file(app, filename):
    return static_file(filename, root='files')
