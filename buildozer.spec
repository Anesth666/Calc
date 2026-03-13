[app]
title = PressorCalc
package.name = PressorCalc
package.domain = org.PressorCalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json
version = 0.1
requirements = python3,kivy==2.1.0,kivymd==1.1.1,pyjnius,android,openssl,pillow,requests
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 30
minapi = 21
ndk = 25b
sdk = 30
ndk_path = 
sdk_path = 
android.accept_sdk_license = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a
android.add_src = 
android.gradle_dependencies = 'androidx.recyclerview:recyclerview:1.2.1', 'com.google.android.material:material:1.6.1'
