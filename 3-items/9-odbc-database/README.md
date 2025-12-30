# database

```sh
psql -U postgres

CREATE DATABASE mydb;

\l


# CREATE USER myuser WITH PASSWORD 'strong_password';

CREATE ROLE myuser WITH LOGIN PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;



# install postgresql client on rocky linux
sudo dnf install -y postgresql

psql -h 192.168.85.71 -p 5432 -U myuser -d mydb 



# or you can install pgcli
mkdir python-pgcli && cd python-pgcli

python -m venv venv
source venv/bin/activate

pip install -U pgcli

pgcli postgres://postgres:test222@192.168.96.141:5432/

pgcli -h 192.168.85.71 -p 5432 -d mydb -U myuser  -W

select version();






```