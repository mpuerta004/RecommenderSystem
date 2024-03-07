# FROM mysql as init-data-mysql-mve

# COPY Model/init.sql /docker-entrypoint-initdb.d/
# COPY Model/setup.sh /mysql/setup.sh

# RUN chmod +x /mysql/setup.sh
# RUN chmod +x /docker-entrypoint-initdb.d/init.sql

# # Set environment variables
# ENV MYSQL_ALLOW_EMPTY_PASSWORD=true
# #mysql -u root -p mysql < /docker-entrypoint-initdb.d/init.sql
# CMD ["mysqld" , "--init-file=/docker-entrypoint-initdb.d/init.sql" , "--user=root"]

# EXPOSE 3306

FROM mysql:8.0.32 as default

# Copy the database file to the init directory
# COPY init.sql /docker-entrypoint-initdb.d/
# FROM mysql:8.0.32


# Copy the database file to the init directory
# COPY init.sql /docker-entrypoint-initdb.d/

# Set environment variables
# ENV MYSQL_ROOT_PASSWORD=mypasswd
# ENV MYSQL_DATABASE=SocioBeeMVE
COPY setup.sh /mysql/setup.sh
COPY init.sql /mysql/init.sql   
#COPY sociobee-mve-20-09-2023.sql /mysql/sociobee-mve-20-09-2023.sql   


ADD init.sql /docker-entrypoint-initdb.d

EXPOSE 3306

#RUN /mysql/setup.sh
# ENTRYPOINT ["tail", "-f", "/dev/null"]
