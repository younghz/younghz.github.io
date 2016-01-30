--- 
layout: post 
title: "elasticsearch重启" 
tagline: "记一次重启记录" 
description: "" 
category: search 
tags: [search] 
--- 
{% include JB/setup %}

## 0 准备工作
###0.1 安装elasticsearch-sql
任意一台

```java
./bin/plugin -u https://github.com/NLPchina/elasticsearch-sql/releases/download/1.4.8/elasticsearch-sql-1.4.8.zip --install sql
```

有可能报错， 重试即可。还报错，就直接搞个包上去，目录为sql

```java
Failed: UnknownHostException[github-cloud.s3.amazonaws.com]
Trying https://github.com/null/sql/archive/master.zip...
Failed to install sql, reason: failed to download out of all possible locations..., use --verbose to get detailed information
```

###0.2 增加配置项

所有机器

```java
action.disable_delete_all_indices:true
```

###0.3 安装 es-falcon插件

所有机器   es-falcon

##1 Disable shard allocation

```
PUT /_cluster/settings
    {
    “transient” : {
    “cluster.routing.allocation.enable” : “none”
    }
}
```

##2 shutdown

```java
curl -XPOST ‘http://localhost:8416/_cluster/nodes/_local/_shutdown’
```
                   
##3 启动
手动bin目录下启动，并在head上确认其已经加入集群。

##4 启动 shard allocation

```java
PUT /_cluster/settings
{
    “transient” : {
    “cluster.routing.allocation.enable” : “all”
    }
}
```

观察并等待集群状态为green后继续操作。

## 5 重复1-4
