start mongod --dbpath="c:\production_svelte\mongodb"

timeout /t 2

cd /d c:\production_svelte\server_new
start c:\Python37-32\Scripts\flask.exe run -h 0.0.0.0 --port 5001

timeout /t 2

cd /d c:\production_svelte\vue_client
npm run serve