---
layout: post
title: "架构可视化"
---

* 目录
{:toc}

# 1 前言

架构可视化是指通过一套轻量但有效的草图对软件架构以更直观的方式描绘出来。

架构可视化比较成体系的表述模式有两种。

其一是 「RUP 4+1 视图」。

> 1995年，Philippe Kruchten在《IEEE Software》上发表了题为《The 4+1 View Model of Architecture》的论文，引起了业界的极大关注，并最终被RUP采纳。该方法的不同架构视图承载不同的架构设计决策，支持不同的目标和用途:
>
* 逻辑视图：当采用面向对象的设计方法时，逻辑视图即对象模型。
* 开发视图：描述软件在开发环境下的静态组织。
* 处理视图：描述系统的并发和同步方面的设计。
* 物理视图：描述软件如何映射到硬件，反映系统在分布方面的设计。

关于 4+1 的详细描述，可以参考下面两篇文章：
1. [运用RUP 4+1视图方法进行软件架构设计](https://www.ibm.com/developerworks/cn/rational/06/r-wenyu/index.html)
2. [架构蓝图--软件架构 "4+1" 视图模型](https://www.ibm.com/developerworks/cn/rational/r-4p1-view/index.html)

其二是 「C4」。下面详述。

# 2 可视化模式 - C4

C4 代表上下文（Context）、容器（Container）、组件（Component）和代码（Code）——一系列分层的图表，可以用这些图表来描述不同缩放级别的软件架构，每种图表都适用于不同的受众。

这种从大到小，从概括到详细可以比喻为 google 地图的不同 zoom 范围。

<p style="text-align:center">
<img src="../resource/architecture_visualization/google_map_example.jpg"  width="900"/>
</p>

也可用金字塔原理描述这种思路。金字塔图如下。

<p style="text-align:center">
<img src="../resource/architecture_visualization/c4.jpg"  width="900"/>
</p>


## 2.1 Context

它显示了你正在构建的软件系统，以及系统与用户及其他软件系统之间的关系。

## 2.2 Container

将软件系统放大，显示组成该软件系统的容器（应用程序、数据存储、微服务等）。

## 2.3 Component

将单个容器放大，以显示其中的组件。

## 2.4 Code

代码元素与类。

关于以上每部分的详细描述，可以参考 [https://www.infoq.cn/article/C4-architecture-model](https://www.infoq.cn/article/C4-architecture-model)。其中有比较详细的说明以及每部分的说明图。

# 3 总结

和设计模式一样。架构需要模式，架构可视化可有固定模式。

# 4 参考

* [C4 Model](https://c4model.com/)
* [用于软件架构的 C4 模型](https://www.infoq.cn/article/C4-architecture-model)
* [程序员必读之软件架构](https://book.douban.com/subject/26248182/)
