---
layout: post
title: "【T】监控 Agent 技术点"
---

1. 抽象 collector -> store
2. MBean MxBean ManagementFactory JMX，jconsole
3. Durid,c3p0 内部都注册了 MXBean，方便第三方监控
4. 初始化 synchronized
5. 实时直接统计，累积reset and get
6. 队列，随机上报 HttpAgentSender
