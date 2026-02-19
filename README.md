### DataBase Details
- DB_NAME=instabee_msb
- DB_USERNAME=instabee_root
- DB_PASSWORD=Gonda@@1123

Live API is : https://msb.instabee.pro/docs

#ubuntu 

sudo apt update
sudo apt install -y build-essential cmake pkg-config libcairo2-dev

sudo apt install -y build-essential cmake pkg-config libcairo2-dev libgirepository1.0-dev python3-gi python3-gi-cairo gir1.2-gtk-3.0
sudo apt install -y libcups2-dev libacl1-dev build-essential python3-dev pkg-config libsystemd-dev


pip install --upgrade pip setuptools wheel






pip freeze > requirements.txt

pip install -r requirements.txt


run aplication 

sudo systemctl daemon-reload

sudo systemctl enable fastapi.service
sudo systemctl start fastapi.service
sudo systemctl restart fastapi.service

uvicorn app.main:app --host 0.0.0.0 --port 8000

uvicorn app.main:app --host 0.0.0.0 --port 5566

uvicorn app.main:app --reload


backgroud
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
nohup uvicorn app.main:app --host 0.0.0.0 --port 5566 > uvicorn.log 2>&1 &

ps aux | grep uvicorn
kill -9 1508948

ATBBLJa6LCuXkpQGVmEZctNQsM7CC8852DA9

logins

monishvd@gmail.com 

1234567890

sudo systemctl restart mysqld

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyYWphZ29uZGFAaG90bWFpbC5jb20iLCJleHAiOjE3Mzc4Mzk1Nzd9.OWKBFEKhF-pghXZ1nuUVUodx60Qnkgz8b419IIvVTXk