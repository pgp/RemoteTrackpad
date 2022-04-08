#!/bin/bash

export APP_ANDROID_SDK_PATH=/home/pgp/Android/Sdk
export APP_ANDROID_NDK_PATH=/home/pgp/Android/Sdk/ndk/21.3.6528147

conda activate buildozer

buildozer -v android debug