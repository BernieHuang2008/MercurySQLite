# 使用官方的 Ubuntu 基础镜像
FROM ubuntu:latest

# 安装必要的工具
RUN apt-get update && apt-get install -y \
    mysql-server \
    && rm -rf /var/lib/apt/lists/*

# 配置 MySQL（root密码：root）
RUN service mysql start && \
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'; FLUSH PRIVILEGES;"

# 暴露 MySQL 端口
EXPOSE 3306
