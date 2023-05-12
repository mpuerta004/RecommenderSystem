#!/bin/bash
set -e
mysql -u root -p mysql < /mysql/init.sql
# service mysql stop