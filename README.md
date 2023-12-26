--process server起動 port9999 python mainProcess.py

--websoekct server起動 port5555 python websocketserver.py

--flask 起動 python flaskServer.py port8888

http://localhost:9999でアクセス

proxyserverがリクエストヘッダを確認し、 ①flaslServer ②websocketserver のどちらかにリクエストをそのまま送る
