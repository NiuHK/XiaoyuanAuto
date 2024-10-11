　　adb kill-server

　　adb connect 127.0.0.1:5555

　　adb root

　　adb connect 127.0.0.1:5555

　　adb push xxxx.0 /system/etc/security/cacerts

　　adb shell "chmod 664 /system/etc/security/cacerts/d0c556f7.0"
