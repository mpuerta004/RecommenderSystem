FROM mysql:8.0.32


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

EXPOSE 3307

#RUN /mysql/setup.sh
# ENTRYPOINT ["tail", "-f", "/dev/null"]