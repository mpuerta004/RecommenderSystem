#!/bin/bash
set -e
sudo service mysql start
sudo mysql < /mysql/init.sql
sudo service mysql stop