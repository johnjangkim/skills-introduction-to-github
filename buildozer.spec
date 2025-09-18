[app]
title = BibleSearch
package.name = bible_search
package.domain = org.example

# Use bible_search_mobile.py as entry point
source.dir = .
source.include_exts = py,kv,png,jpg,ttf
source.main = bible_search_mobile.py

version = 0.1
# Expanded requirements to support semantic search (Gemini)
requirements = python3,kivy,sqlite3,google-generativeai,requests,urllib3,certifi,protobuf,google-api-python-client,google-auth,google-auth-httplib2,httplib2,cachetools,grpcio,grpcio-status,pyasn1,pyasn1-modules,uritemplate,proto-plus,typing-extensions,pydantic,tqdm
orientation = portrait
fullscreen = 0

android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1