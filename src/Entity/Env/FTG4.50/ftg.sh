#!/bin/bash

#SCRIPT_DIR=$(cd $(dirname $0); pwd)

#cd $SCRIPT_DIR

# for linux
java  -Dai.djl.logging.level=debug -cp ./Entity/Env/FTG4.50/FightingICE.jar:./Entity/Env/FTG4.50/lib/lwjgl/*:./Entity/Env/FTG4.50/lib/natives/linux/*:./Entity/Env/FTG4.50/lib/*:./Entity/Env/FTG4.50/lib/erheajar/* Main --a1 EmcmAi --a2 BlackMamba --c1 ZEN --c2 ZEN -n 1 --mute --fastmode --disable-window
#java -cp FightingICE.jar:./lib/lwjgl/*:./lib/natives/linux/*:./lib/*:./lib/jars-dl4j/* Main  --a1 ERHEA_PI --a2 BCP --c1 ZEN --c2 ZEN -n 1 --mute

# for macos
#java -XstartOnFirstThread -cp FightingICE.jar:./lib/lwjgl/*:./lib/natives/macos/*:./lib/*  Main --py4j --mute --port 4242

# java -classpath /usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/charsets.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/cldrdata.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/dnsns.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/icedtea-sound.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/jaccess.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/java-atk-wrapper.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/localedata.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/nashorn.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunec.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunjce_provider.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunpkcs11.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/zipfs.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jce.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jfr.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jsse.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/management-agent.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/resources.jar:/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/rt.jar:/home/llt/lrq/erhea_mvn/target/classes:/home/llt/lrq/FTG450train/AIToolKit.jar:/home/llt/lrq/FTG450train/FightingICE.jar:/home/llt/.m2/repository/ai/djl/mxnet/mxnet-native-auto/1.7.0-backport/mxnet-native-auto-1.7.0-backport.jar:/home/llt/.m2/repository/ai/djl/api/0.8.0/api-0.8.0.jar:/home/llt/.m2/repository/com/google/code/gson/gson/2.8.6/gson-2.8.6.jar:/home/llt/.m2/repository/net/java/dev/jna/jna/5.3.0/jna-5.3.0.jar:/home/llt/.m2/repository/org/apache/commons/commons-compress/1.20/commons-compress-1.20.jar:/home/llt/.m2/repository/ai/djl/mxnet/mxnet-engine/0.8.0/mxnet-engine-0.8.0.jar:/home/llt/.m2/repository/ai/djl/mxnet/mxnet-native-mkl/1.7.0-backport/mxnet-native-mkl-1.7.0-backport-linux-x86_64.jar:/home/llt/.m2/repository/ai/djl/mxnet/mxnet-native-mkl/1.7.0-backport/mxnet-native-mkl-1.7.0-backport-osx-x86_64.jar:/home/llt/.m2/repository/ai/djl/basicdataset/0.8.0/basicdataset-0.8.0.jar:/home/llt/.m2/repository/org/apache/commons/commons-csv/1.8/commons-csv-1.8.jar:/home/llt/.m2/repository/ai/djl/model-zoo/0.8.0/model-zoo-0.8.0.jar:/home/llt/.m2/repository/tech/tablesaw/tablesaw-jsplot/0.30.4/tablesaw-jsplot-0.30.4.jar:/home/llt/.m2/repository/io/pebbletemplates/pebble/2.6.0/pebble-2.6.0.jar:/home/llt/.m2/repository/com/google/guava/guava/16.0.1/guava-16.0.1.jar:/home/llt/.m2/repository/com/coverity/security/coverity-escapers/1.1/coverity-escapers-1.1.jar:/home/llt/.m2/repository/tech/tablesaw/tablesaw-core/0.30.4/tablesaw-core-0.30.4.jar:/home/llt/.m2/repository/com/fasterxml/jackson/core/jackson-databind/2.9.8/jackson-databind-2.9.8.jar:/home/llt/.m2/repository/com/fasterxml/jackson/core/jackson-annotations/2.9.0/jackson-annotations-2.9.0.jar:/home/llt/.m2/repository/com/fasterxml/jackson/core/jackson-core/2.9.8/jackson-core-2.9.8.jar:/home/llt/.m2/repository/com/github/wnameless/json-flattener/0.6.0/json-flattener-0.6.0.jar:/home/llt/.m2/repository/com/eclipsesource/minimal-json/minimal-json/0.9.5/minimal-json-0.9.5.jar:/home/llt/.m2/repository/org/apache/commons/commons-text/1.4/commons-text-1.4.jar:/home/llt/.m2/repository/org/apache/commons/commons-lang3/3.7/commons-lang3-3.7.jar:/home/llt/.m2/repository/com/univocity/univocity-parsers/2.7.5/univocity-parsers-2.7.5.jar:/home/llt/.m2/repository/org/apache/commons/commons-math3/3.6.1/commons-math3-3.6.1.jar:/home/llt/.m2/repository/org/jsoup/jsoup/1.11.3/jsoup-1.11.3.jar:/home/llt/.m2/repository/it/unimi/dsi/fastutil/8.2.1/fastutil-8.2.1.jar:/home/llt/.m2/repository/org/roaringbitmap/RoaringBitmap/0.7.14/RoaringBitmap-0.7.14.jar:/home/llt/.m2/repository/org/slf4j/slf4j-api/1.7.26/slf4j-api-1.7.26.jar:FightingICE.jar:./lib/lwjgl/*:./lib/natives/linux/*:./lib/*:./lib/jars-dl4j/* Main --a1 ERHEA_PI_DJL --a2 EmcmAi --c1 ZEN --c2 ZEN -n 1 --mute 


