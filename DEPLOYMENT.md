# Production Deployment Guide

This guide outlines the steps to deploy the Msb_python_APIS application in a production environment (Ubuntu/Linux).

## 1. System Dependencies
Ensure your server has the required system packages installed. **FFmpeg is critical** for media processing (video/audio submissions).

### Install FFmpeg & Python Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip python3-dev build-essential git ffmpeg libmysqlclient-dev
```

> **Critical Validation:** Verify FFmpeg is installed correctly.
> ```bash
> ffmpeg -version
> ```
> *If this command fails, the application will crash during media uploads.*

## 2. Database Setup (MySQL/MariaDB)
Ensure your MySQL/MariaDB server is running and you have created the database (e.g., `local_msb_uat`).

```bash
sudo systemctl enable mariadb
sudo systemctl start mariadb
```

If you are setting up the database schema manually, ensure all tables are created. Specifically, verify that the `Talentgrades` table exists and `sub_categories` has the `Talentgrade_id` column.

## 3. Application Setup

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd Msb_python_APIS
    ```

2.  **Create Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python Packages**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory.
    ```bash
    nano .env
    ```
    Example configuration:
    ```ini
    DATABASE_URL=mysql+pymysql://<user>:<password>@localhost/local_msb_uat
    APP_URL=http://your-domain.com:5566
    SECRET_KEY=your_secret_key
    # Add other required variables
    ```

## 4. Running the Application

For production, use **Gunicorn** with Uvicorn workers to manage the process reliably.

### Run with Gunicorn
```bash
# Run on port 5566 with 4 workers
./venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:5566 --daemon
```

### (Recommended) Run as Systemd Service
Create a service file to keep the app running automatically.

1.  Create file: `/etc/systemd/system/msb_api.service`
    ```ini
    [Unit]
    Description=Gunicorn instance to serve MSB API
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/path/to/Msb_python_APIS
    Environment="PATH=/path/to/Msb_python_APIS/venv/bin"
    ExecStart=/path/to/Msb_python_APIS/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:5566

    [Install]
    WantedBy=multi-user.target
    ```

2.  Start and Enable Service
    ```bash
    sudo systemctl start msb_api
    sudo systemctl enable msb_api
    ```

## 5. Troubleshooting Common Issues

### "FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'"
This error occurs when `ffmpeg` is not installed on the server.
**Fix:** Run `sudo apt-get install -y ffmpeg` and restart the application service.

### Database Connection Errors
If you see "OperationalError" or stuck requests:
1.  Check your database credentials in `.env`.
2.  Restart the database service: `sudo systemctl restart mariadb`.
3.  Restart the application: `sudo systemctl restart msb_api`.
