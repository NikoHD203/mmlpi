# Usage: bash installJava.sh <arm32|arm64>
if [ $1 = "arm32" ]; then
    wget https://www.dropbox.com/s/p4mt1r2cbhv2obf/jdk-8u221-linux-arm32-vfp-hflt.tar.gz?dl=1 -O java.tar.gz
fi
if [ $1 = "arm64" ]; then
    wget https://www.dropbox.com/s/g5q7bh2r7et5ym8/jdk-8u221-linux-arm64-vfp-hflt.tar.gz?dl=1 -O java.tar.gz
fi
if [ -f java.tar.gz ]; then
    mkdir /usr/lib/jvm
    tar -C /usr/lib/jvm -zxf java.tar.gz 
    update-alternatives --install "/usr/bin/java" "java" "/usr/lib/jvm/jdk1.8.0_221/bin/java" 0
    update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/jvm/jdk1.8.0_221/bin/javac" 0
    update-alternatives --set java /usr/lib/jvm/jdk1.8.0_221/bin/java
    update-alternatives --set javac /usr/lib/jvm/jdk1.8.0_221/bin/javac
    rm java.tar.gz
else
    echo 'Error Installing Java!'
fi