[app]
title = Rassegna Lavoro
package.name = rassegnalavoro
package.domain = it.consulentedellavoro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy,requests,beautifulsoup4,urllib3,chardet,idna,certifi,android,pyjnius
android.permissions = INTERNET, FOREGROUND_SERVICE, POST_NOTIFICATIONS, WAKE_LOCK
android.services = rassegnamonitor:service.py
android.archs = arm64-v8a, armeabi-v7a
