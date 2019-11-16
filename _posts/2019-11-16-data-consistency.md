---
layout: post
title: "分布式系统之数据一致性"
---

* 目录
{:toc}

## 1 概念

「分布式系统概念与设计」中分布式系统概念描述为：

> 分布式系统是一个硬件或软件组件，分布在不同计算机上，彼此之间仅仅通过消息传递进行协调的系统。
 
分布式在没有任何业务逻辑约束情况下有如下系统特性：
* 分布行。机器在空间上随机分布。
* 对等性。机器之间无主从关系。
* 并发性。
* 缺乏全局时钟。
* 故障总会发生。

分布式环境中的典型问题是：
* 通信异常。消息丢失，延时等。
* 网络分区。如BJ 和SH 机房通信断掉，只能机房内通信。此种情景也叫脑裂。
* 三态。一次通信的结果可能是成功、失败或者超时。在超时情况下，请求有可能被执行也有可能没有执行。
* 节点故障。


## 2 数据一致性协议


## 资料

* [从Paxos到Zookeeper](https://book.douban.com/subject/26292004/)
* [分布式系统的事务处理](https://coolshell.cn/articles/10910.html)
* [CAP理论与分布式系统设计](https://mp.weixin.qq.com/s/gV7DqSgSkz_X56p2X_x_cQ?)
* [拜占庭将军问题](https://zh.wikipedia.org/wiki/%E6%8B%9C%E5%8D%A0%E5%BA%AD%E5%B0%86%E5%86%9B%E9%97%AE%E9%A2%98)
* [两阶段提交](https://zh.wikipedia.org/wiki/%E4%BA%8C%E9%98%B6%E6%AE%B5%E6%8F%90%E4%BA%A4#%E7%BC%BA%E7%82%B9)
* [三阶段提交](https://zh.wikipedia.org/wiki/%E4%B8%89%E9%98%B6%E6%AE%B5%E6%8F%90%E4%BA%A4)
* [Raft 一致性协议](https://www.infoq.cn/article/raft-paper)
