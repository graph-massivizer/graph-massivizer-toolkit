# syntax=docker/dockerfile:1.4

FROM python:3.10-slim

# 1) Install OpenJDK 17 plus wget/ca-certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        wget \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2) Set JAVA_HOME for Java 17 on Debian 12
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV LD_LIBRARY_PATH="${JAVA_HOME}/lib/server:${LD_LIBRARY_PATH}"

# 3) Download & Install Hadoop 3.3.6
ENV HADOOP_VERSION=3.4.1
RUN wget "https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz" \
    && tar -xzf "hadoop-$HADOOP_VERSION.tar.gz" \
    && mv "hadoop-$HADOOP_VERSION" /usr/local/hadoop \
    && rm "hadoop-$HADOOP_VERSION.tar.gz"

ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH="$PATH:$HADOOP_HOME/bin"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HADOOP_HOME/lib/native"

# 4) **Manually** set CLASSPATH to cover Hadoop config and jars
#    This is crucial so PyArrow's native 'libhdfs' can find all needed classes
ENV CLASSPATH="$HADOOP_CONF_DIR:\
$HADOOP_HOME/share/hadoop/common/*:\
$HADOOP_HOME/share/hadoop/common/lib/*:\
$HADOOP_HOME/share/hadoop/hdfs/*:\
$HADOOP_HOME/share/hadoop/hdfs/lib/*:\
$HADOOP_HOME/share/hadoop/mapreduce/*:\
$HADOOP_HOME/share/hadoop/mapreduce/lib/*:\
$HADOOP_HOME/share/hadoop/yarn/*:\
$HADOOP_HOME/share/hadoop/yarn/lib/*"

# 5) Copy your project + install Python dependencies
WORKDIR /app
COPY . /app

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir "pyarrow[hdfs]"

# 6) Optional environment variable for your HDFS
ENV HDFS_NAMENODE="hdfs://namenode:8020"

# 7) Make your start script executable + default command
RUN chmod +x /app/src/graphmassivizer/runtime/start.sh
CMD ["/app/src/graphmassivizer/runtime/start.sh"]
