---
layout: post
title: "Java 热加载/热部署技术"
---

* 目录
{:toc}

# 1 概念

热部署：一般指容器（支持多应用）不重启，单独启动单个应用。

热加载：一般指不重启应用（JVM），单独重新更新某个类或者配置文件。

# 2 技术


热加载热部署一般基于以下三方面技术实现：

* 基于 JPDA 中的 JVMTI 接口（可以参考[这里](https://younghz.github.io/java-debug-architecture)），如 HotSwap。限制是只能修改方法体。
* JRebel。使用基本无限制，并且能和大部分 IDE 以及框架融合。商用、收费。
* 基于 ClassLoader，如 OSGi，Tomcat。针对这种，考虑到 JVM 规范中单个类只能被 load/define 一次的约束，一般实现都是关闭旧的 ClassLoader 并创建新 ClassLoader 来实现。

针对上面几种产品的介绍，详细可见：
* [HotSwap vs JRebel](https://jrebel.com/rebellabs/reloading_java_classes_401_hotswap_jrebel/)。
* [Tomcat 热加载配置](http://www.importnew.com/26156.html)  或 [Tomcat](https://tomcat.apache.org/tomcat-9.0-doc/config/context.html)
* [漫谈JVM热加载技术](https://yq.aliyun.com/articles/65023)
* OSGi 热加载可以参考 [深入理解OSGi](https://book.douban.com/subject/21324330/) 的 3.2.4 与 4.7 部分内容。

# 3 总结

需要注意的是，热加载与热部署是用来解决「频繁发布」情景下的耗时问题，另外由于 JVM 的 GC 机制，在设计热加载流程时需要考虑原有卸载模块的内存清理问题，否则可能会造成 OOM。

线上环境既不会频繁发布，又有比较高的安全性要求，所以一般不建议在线上应用这种技术。