---
layout: post
title: "【T】TcpListenOverFlows问题与解决方法"
---

### 问题现象

TcpListenOverflows报警

### 问题分析

#### 什么是TcpListenOverflows

就是应用提供的tcp连接处理数超过了tcp请求数。

#### TcpListenOverFlows由什么因素决定

由两个因素决定：

* 服务器的线程池大小，这个在jetty中是由org.eclipse.jetty.util.thread.QueuedThreadPool设置。    
* 系统层级的socket队列等待长度。这个是在/proc/sys/net/core/somaxconn文件中设置。    

当前者设置的最大线程数满时，这时在来请求就会进入socket等待队列，当socket等待队列满时，这时在来连接就会计入TcpListenOverflows。计数不断增加，可能就会触发报警。

#### 观察方法

1. 观察当前的tcplistenoverflows数量是不是在一直增长。`watch netstat -s : grep listen`。    
2. `jmap -histo:live pid` 看下当前的socket实例数是不是很多，并`jstack pid > stack.log`保存堆栈数据，有必要的话dump下内存以备分析`jmap -dump:format=b,file=filename pid`。
。    

### 解决方案

既然知道了原因，那么解决方法也就明了。

1. 提高jetty的Queuedthreadpool设置的最大线程数，我们这里默认设置的是200，order这里没有设置自己的jetty.xml文件，默认加载的是mms-boot包里的jetty8.xml，在那里设置的maxThreads
为200，可以考虑配置自己的配置文件，因为除了这一点需要灵活配置外，在默认的jetty8.xml中也没有配置java.util.concurrent.ArrayBlockingQueue，这个是决定连接是否会被丢弃
的参数，当超过配置的数时，连接自动被丢弃，这样就不会造成tcplistenoverflows了。配置教程及方法如下：[https://wiki.eclipse.org/Jetty/Howto/High_Load#Thread_Pool](https://wiki.eclipse.org/Jetty/Howto/High_Load#Thread_Pool)。    


2. 优化somaxconn的设置，这个是SRE做的。

3. 在系统内部还可以通过设置超时时间，尽快丢掉不重要的连接,不要让过多的线程处于timewait/wait状态，以处理新的连接。
