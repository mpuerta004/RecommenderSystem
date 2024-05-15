FROM mysql


# Copy the database file to the init directory
# COPY init.sql /docker-entrypoint-initdb.d/
# FROM mysql:8.0.32


# Copy the database file to the init directory
# COPY init.sql /docker-entrypoint-initdb.d/

# Set environment variables
# ENV MYSQL_ROOT_PASSWORD=mypasswd
# ENV MYSQL_DATABASE=SocioBeeMVE
COPY Model/setup.sh /mysql/setup.sh
COPY Model/init.sql /mysql/init.sql 
#COPY sociobee-mve-20-09-2023.sql /mysql/sociobee-mve-20-09-2023.sql   


ADD Model/init.sql /docker-entrypoint-initdb.d

EXPOSE 3306

#RUN /mysql/setup.sh
# ENTRYPOINT ["tail", "-f", "/dev/null"]