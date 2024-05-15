FROM mysql:8.0.32


# Copy the initialization scripts and configuration file
COPY Model/setup.sh /mysql/setup.sh
COPY Model/init.sql /docker-entrypoint-initdb.d/
COPY Model/my.cnf /etc/mysql/my.cnf

# Expose the MySQL port
EXPOSE 3306

# Default command
CMD ["mysqld"]
