#!/bin/bash

echo "$(date+'%Y-%m-%d %H:%M:%S')"
source activate credit
cd /home/finnou/Credit_All_In_One
python --version

gunicorn application:app -w 4 --bind 0.0.0.0:8000 --timeout 120 --log-level debug