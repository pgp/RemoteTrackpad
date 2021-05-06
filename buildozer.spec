[app]

# (str) Title of your application
title = RemoteTrackpad

version = 0.1

# (str) Source code where the main.py live
source.dir = .

# (str) Package name
package.name = remotetrackpad

# (str) Package domain (needed for android/ios packaging)
package.domain = it.pgp

# Android options
fullscreen = 0

# android.arch = x86
android.arch = armeabi-v7a

android.api = 28
android.minapi = 21

android.permissions = INTERNET

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = all

requirements = python3,kivy,openssl