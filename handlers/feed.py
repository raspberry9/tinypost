# -*- coding: utf-8 -*-
import time
import logging
from bottle import route, response
from error import ApplicationError, PostNotExistError
from http import get_response, get_request
from utilities import TimeUtil

req_proto = {'num': int, }  # 보고싶은 포스팅 번호

res_proto = {'code': int,
             'msg': str, }


@route('/feed', method='GET')
def feed(app):
    """
    rss link를 연결했을 때 화면을 보여 줍니다.

    호출
    http://localhost:8080/feed?num=1

    결과
    html 형식의 문서
    """
    try:
        req = get_request(req_proto)
        try:
            session = req['session']
            readerid = str(session['userid'])
        except:
            # 세션이 없는 경우는 로그인 하지 않았으므로 public 글만 볼 수 있다.
            readerid = None

        num = int(req['num'])

        with app.postdb() as db:
            post = app.postmgr.get_post(db, num, readerid)

        response.content_type = 'text/html'

        if post:
            url = "http://{0}".format(app.publichost)
            html = _generate_html(url, post.num, post.wid, post.wnick, post.wtime, post.status, post.images, post.context)
        else:
            raise PostNotExistError("post not exist. readerid=%s, post_num=%s" % (readerid, num))

        return html

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)


def _get_top_menus(top_menus):
    """
    top_menus = {"Forum": "http://localhost:8080/feed?num=1",
                 "Contact": "http://localhost:8080/feed?num=2",
                 "Test": "http://localhost:8080/feed?num=3"}
    """
    return " | ".join(['<a href="{1}">{0}</a>'.format(k, v) for k, v in top_menus.iteritems()])


def _generate_html(url, num, userid, wnick, wtime, status, images, context):

    print "wtime!!!!!!!!!!!!!!!!!!!!!!!!!", type(wtime), wtime

    title = "TinyPost"
    css_path = url + "/files/style.css"
    date_img_path = url + "/files/timeicon.gif"
    comment_img_path = url + "/files/comment.gif"
    top_menus = {"Forum": url + "/feed?num=1",
                 "Contact": url + "/feed?num=2",
                 "Test": url + "/feed?num=3", }
    comment_link = url + "/feed?num=4"
    comment_count = 0
    hrtime = TimeUtil.get_human_readable_time(time.mktime(time.strptime(wtime, "%Y-%m-%d %H:%M:%S")))

    if status == 1:
        post_type = "나의 포스팅"
    elif status == 2:
        post_type = "친구 공개 포스팅"
    elif status == 3:
        post_type = "전체 공개 포스팅"
    else:
        raise Exception("status is not valid. status" % (status,))

    args = (title,
            css_path,
            _get_top_menus(top_menus),
            title,
            post_type,
            "%s(%s)" % (userid, wnick),
            context,
            comment_img_path,
            comment_link,
            comment_count,
            date_img_path,
            hrtime,)

    html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>{0}</title>
<meta http-equiv="Content-type" content="text/html; charset=UTF-8" />
<style type="text/css" media="all">
    @import url({1});
</style>
</head>
<body>
<div id="page-container">
  <div id="top"> {2}
  <h1>{3}</h1>
  </div>
  <div id="content">
    <div class="padding">
      <h2>{4}</h2>
      <br />
      <h4><a href="#">{5}</a></h4>
      <br />
      {6}
      <p class="date"><img src="{7}" alt="" /> <a href="{8}">Comments({9})</a> <img src="{10}" alt="" /> {11}.</p>
    </div>
  </div>
  <div id="footer"> <a href="#">RSS Feed</a> | <a href="#">Contact</a> | <a href="#">Accessibility</a> | <a href="#">Products</a> | <a href="#">Disclaimer</a> | <a href="http://jigsaw.w3.org/css-validator/check/referer">CSS</a> and <a href="http://validator.w3.org/check?uri=referer">XHTML</a> <br />
    Copyright &copy; 2014 Koo - Design: Green Grass <a href="http://www.free-css-templates.com">David Herreman</a> </div>
</div>
</body>
</html>
    """.format(*args)

    return html
