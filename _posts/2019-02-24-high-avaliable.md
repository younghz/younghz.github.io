---
layout: post
title: "高可用思考"
---

架构设计之高可用

------

# 1 前言

先求生存在求发展。系统可用性是系统的基本。

可用性用可用性指标描述，即一般所说的「4个9」、「5个9」。可用性指标=(1-(系统不可用时间/一年总时间))x100%。一般来讲，「4个9」的一年不可用时间在1小时作用，「5个9」的不可用时间即为「4个9」的十分之一，在6分钟左右。


<p style="text-align:center">
<img src="../resource/high_aviliablity/high-aviliablity.png"  width="300"/>
</p>

高可用不但需要在设计和技术实现上保证，也需要合理的流程辅助实现。

1. 架构设计
2. 技术实现
3. 流程保证

# 2 高可用

## 2.1 架构设计



## 2.2 技术实现

<p style="text-align:center">
<img src="../resource/high_aviliablity/high_avilable_detail.png"  width="900"/>
</p>


## 2.3 流程保证

设计 -> 开发 -> 测试 -> 运维

### 2.3.1 设计

### 2.3.2 开发

代理管理。

### 2.3.3 测试

* 单元测试
* 自动化测试
* 压力测试

### 2.3.4 运维

* 发布：自动化发布、灰度发布。
* 监控。监控采集、上报、展示、报警。


# 3 总结


1. [大型网站技术架构](https://book.douban.com/subject/25723064/)
2. [亿级流量网站架构核心技术](https://book.douban.com/subject/26999243/)