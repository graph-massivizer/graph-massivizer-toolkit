# Use the same lightweight Python base image
FROM python:3.10-slim

# Add the Debian 11 (bullseye) repository to access OpenJDK 11
RUN echo "deb http://deb.debian.org/debian bullseye main contrib non-free" > /etc/apt/sources.list.d/bullseye.list

# Pin openjdk-11-jdk to the Bullseye repository
RUN echo "Package: openjdk-11-jdk\nPin: release n=bullseye\nPin-Priority: 1001" > /etc/apt/preferences.d/openjdk-11-jdk

# Update package lists and install openjdk-11-jdk, wget, and other tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    wget \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for the Java runtime
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install Hadoop client libraries (version 2.7.1 to match your HDFS cluster)
ENV HADOOP_VERSION=2.7.1
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION /usr/local/hadoop && \
    rm hadoop-$HADOOP_VERSION.tar.gz

# Set Hadoop environment variables
ENV HADOOP_HOME=/usr/local/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HADOOP_HOME/lib/native

# Set working directory to /app, as in your original
WORKDIR /app

# Copy the entire repository from 3 levels up, matching your original COPY
COPY . /app

# Upgrade pip, setuptools, and wheel, as in your original
RUN python -m pip install --upgrade pip setuptools wheel

# Install project dependencies using setup.py/setup.cfg, as in your original
RUN pip install --no-cache-dir .

# Install PyArrow with HDFS support, as in your original
RUN pip install --no-cache-dir "pyarrow[hdfs]"

# Expose environment variable for HDFS, unchanged from your original
ENV HDFS_NAMENODE="hdfs://namenode:8020"

# Make the start script executable, using the same path as your original
RUN chmod +x /app/src/graphmassivizer/runtime/start.sh

# Default command to run the start script, unchanged from your original
CMD ["/app/src/graphmassivizer/runtime/start.sh"]