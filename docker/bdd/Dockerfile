FROM mariadb:latest
WORKDIR /tmp
COPY init.sql .
CMD mysql -u root -ppassword -h db -P 3306 < init.sql