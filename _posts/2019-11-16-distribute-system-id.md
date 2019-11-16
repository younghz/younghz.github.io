---
layout: post
title: "分布式系统中之ID"
---

* 目录
{:toc}


ID，所有需要唯一标识的实体都需要包含的属性。在后端系统中，对 ID 的讨论集中在两个方面：

* 分布式 ID 服务。
* 业务 ID。

## 分布式 ID 服务

分布式系统中，每个数据节点存储不同的数据情景，需要生成ID做全局唯一标识。除了全局唯一，一般还要求满足趋势递增。

技术方案一般有两类，根据是否依赖中央分配分成本地生成&分布式 ID 服务，即统一发号器两种形式。

本地生成方案较成熟的有：

* UUID。
* SnowFlake。
* UidGenerator。百度。

本地 ID 生成方案在思路上一般是：

* 分段。每段通过固定位数标识。
* 一般都包含两段。时间段+节点段。节点段标识唯一。时间段标识唯一和递增。

统一 ID 发号器可以参考：

* 数据库递增主键。
* [微信 seqsvr](https://www.infoq.cn/article/wechat-serial-number-generator-architecture/).
* [美团 Leaf](https://tech.meituan.com/2017/04/21/mt-leaf.html).

详细的可以参考上面的说明。

中央 ID 发号器在唯一性上较好实现，并不需要本地形式中通过唯一 node 标识实现。这种形式关注点主要放在大流量下的稳定性问题。
实现方案也比较一致，即通过分段思想，将耗时的 I/O 操作取号变为内存取号。

关于「Leaf」中描述的数据库取号使用的 sql 问题，Innodb 默认隔离级别是「可重复读」，关于可重复读级别下的多事务测试可见下面。即在 Innodb
引擎下此种 SQL 没有问题。

```sql
# session 1

select @@global.tx_isolation, @@tx_isolation;

START TRANSACTION;
SELECT * FROM your_table_name WHERE id=1;
UPDATE your_table_name SET data_state=data_state+1 WHERE id=1;
# 时间点 1
SELECT * FROM your_table_name WHERE id=1;
COMMIT;
# 时间点 2
```

```sql
# session 2

START TRANSACTION;

# select 操作在时间点
SELECT * FROM your_table_name WHERE id=1;

# update 在时间点 2 之前，即 session1 commit 之前无法执行，会等锁释放
UPDATE your_table_name SET data_state=data_state+1 WHERE id=1;

# 此时 data_state 的值为 session 1 更新的值+ session 2 更新的值。
SELECT * FROM your_table_name WHERE id=1;
COMMIT;
```

## 业务ID

业务情景描述，以订单 ID 为例，在用户展示端和后端使用的要求不尽相同，形式也不一样。
后端使用要求和上方描述一致，一般是要求唯一、趋势递增、整型而非字符串等。
而用户端展示情景则一般要求：
* 唯一性。
* 业务含义。如在ID中包含下单时间，业务标识，用户标识等业务含义。
* 混淆。无法从订单号中判断出你的运营信息。关于混淆的历史，可见看看[德国坦克问题](https://zh.wikipedia.org/wiki/%E5%BE%B7%E5%9B%BD%E5%9D%A6%E5%85%8B%E9%97%AE%E9%A2%98)

关于这部分，可以看下 [电商订单号设计思考](https://www.jianshu.com/p/544ab3d60e77) 的整理。

针对于混淆的概念，又存在不同的形式：
* 只是展示端混淆，后端仍使用自己的ID，展示端基于后端 ID 混淆。且混淆后的ID可以一对一转换会后端ID。
* 展示端和后端使用同样的ID，此ID本身就有混淆的概念。


## 其它

* 32位数字混淆成另一个32位数字且可反解析的 [skip32 算法](https://github.com/boivie/skip32-java/blob/master/src/main/java/com/boivie/skip32/Skip32.java)。
* https://github.com/nlenepveu/Skip32。
* 32 位数字混淆为字符串的算法。https://hashids.org/java/