### New Server Setup

sudo apt update && sudo apt upgrade -y
sudo apt install nginx python3 python3-venv python3-pip git -y

##  Static Website (mysuperbrain.com)
sudo mkdir -p /var/www/mysuperbrain
sudo chown -R $USER:$USER /var/www/mysuperbrain

## nginx

sudo nano /etc/nginx/sites-available/mysuperbrain

server {
    listen 80;
    server_name mysuperbrain.com www.mysuperbrain.com;

    root /var/www/mysuperbrain;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}


sudo ln -s /etc/nginx/sites-available/mysuperbrain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx


## fast api 

cd /var/www
sudo git clone https://github.com/amar-r9/Msb_python_APIS service
cd service


python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000


pip install gunicorn uvicorn
sudo nano /etc/systemd/system/fastapi.service

[Unit]
Description=FastAPI app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/service
ExecStart=/var/www/service/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 127.0.0.1:8001

[Install]
WantedBy=multi-user.target



sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl restart fastapi

sudo nano /etc/nginx/sites-available/service.mysuperbrain.com


server {
    listen 80;
    server_name service.mysuperbrain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}



sudo ln -s /etc/nginx/sites-available/service.mysuperbrain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
