#! /bin/sh

heroku auth:login

heroku run -a still-coast-06295 python truncate_db.py
