[app]
title = GreenSummarizer
package.name = greensummarizer
package.domain = org.greensummarizer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pypdf==4.0.0,networkx==3.2.1
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
[buildozer]
log_level = 2
warn_on_root = 1
