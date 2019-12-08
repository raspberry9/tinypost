tinypost 설명서

tinypost는 python gevent bottle을 이용한 WSGI 서버 입니다.
피드를 올리고 RSS리더 등으로 구독할 수 있는 기능이 있습니다.
아직 클라이언트는 개발되어 있지 않으나 아래와 같은 API를 통해 테스트 가능 합니다.

*실행 방법*
1. virtual env로 python 2.7.x 환경을 만든다.
virtualenv env
. env/bin/activate

2. Python 라이브러리 설치
pip install -r requirements.txt

3. 실행 
python server.py


*API 예제*
- 가입하기
http://localhost:8080/join?nickname=abcd&password=1234&userid=test@abc.com

- 로그인
http://localhost:8080/login?password=1234&userid=test@abc.com

- 피드 올리기
http://localhost:8080/post?userid=test@abc.com&images=&context=Hi~

- 피드 보기
http://localhost:8080/show?num=1

- RSS피드 보기(RSS리더로 볼 수 있으며, 사전에 로그인을 해야 함)
http://localhost:8080/rss?userid=test@abc.com

- 로그아웃
http://localhost:8080/logout

- 그 밖에 친구 맺기/끊기 및 피드 공개 범위 설정 등의 기능이 있습니다.