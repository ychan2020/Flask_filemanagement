# Development Team Project: Coding Output

# Prerequisite

The following should be installed already before setup.
- Python3

Requirements:
```
pip install -r requirements.txt
```
# Program

Running in Linux from the downloaded directory:
```
export FLASK_APP=__init__.py
flask run --cert=./keystore/cert.pem --key=./keystore/key.pem
```

Running in Windows from the downloaded directory:
Change to downloaded directory
```
set FLASK_APP=__init__.py
flask run --cert=./keystore/cert.pem --key=./keystore/key.pem
```
User management page (Admin role required)

Change to admin directory
```
flask run --port=8888 --cert=./keystore/cert.pem --key=./keystore/key.pem
```
Admin user: admin@test.com
Default user password: P@ssw0rd

Client page: https://localhost:5000/
Admin page: https://localhost:8888/

# Program test

After the program ran
```
set otp=XXXXXX
pytest -vv client.py
pytest -vv admin.py
```

# Database

DB details:
```
Host: sql5.freesqldatabase.com:3306
Database user: sql5495299
Database name: sql5495299
Database password: hz7bDRYNPh
Web console: https://www.phpmyadmin.co/
```


Database Query:

Code to recreate the 2 x NASA database tables:
```
CREATE TABLE `document` (
  `fileid` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(50) NOT NULL,
  `data` mediumblob NOT NULL,
  `role` enum('ISS','Ground Staff','Government','Admin','Disabled') NOT NULL,
  `key` varchar(50) NOT NULL,
  `timestamp` datetime NOT NULL,
  `owner` varchar(50) NOT NULL,
  PRIMARY KEY (`fileid`)
) 

CREATE TABLE `user` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  `role` enum('ISS','Ground Staff','Government','Admin','Disabled') NOT NULL,
  `otp_secret` varchar(16) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
)
```

# MFA Setup
Install FreeOTP app on your device

Google Play:
https://play.google.com/store/apps/details?hl=en&id=org.fedorahosted.freeotp

iOS:
https://apps.apple.com/us/app/freeotp-authenticator/id872559395

Scan QRcode using FreeOTP app during user creation
