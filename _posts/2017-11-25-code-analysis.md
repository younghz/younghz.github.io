---
layout: post
title: "Java代码分析与工具"
---

* 目录
{:toc}

规范和自动化总是好东西，通常有「深陷shi谭」的感觉时，要么是方向错了，要么是方法错了。

# 1 代码分析

自以为，代码分析无非事前、事中和事后三种，在官方一点就叫静态分析、运行分析、离线分析。

静态代码分析主要关注三面两点，三面：「语法」「结构」「过程」，两点：「规范」「BUG」。语法就不说了，结构和过程就比如内部变量声明和使用个了十万八千里、switch没有default、嵌套太深等等。在这几点的检查中想要发现的也是代码规不规范的问题以及有没有潜在BUG这个问题。运行分析，通常用来解决对不对、美不美（是否是CPU/Memory/IO友好）这两个问题。「对不对」的问题就是验证逻辑，而「美不美」的分析又可以分为两种：Microbenchmark，Profiling。离线分析就更简单了，但这个时候明显是已经有了问题或者有了问题的苗头。

# 2 静态分析
### 2.1 工具
* CheckStyle
* FindBugs
* 阿里规约

### 2.2 原理
根据内置的缺陷模式、规则对Java源文件或者Class文件（字节码）进行分析，或者通过收集变量进行数据流分析，这种主要解决的主要就是那种比如实例化但是无使用这种问题。

### 2.3 实施

```
public void staticCheck(String param) {

    int index;

    String temp = null;
    System.out.println(temp.length());

    for (index=0;index<10;index++) {

        if (true) {
            if (temp == param) {
                break;
            }
        }

    }
}
```

以上面的代码为例，可以用CheckStyle和FindBugs检测一下，看看结果。

# 3 运行分析

### 3.1 运行分析之单元测试

> 如果你没有用Mock工具写测试代码，要么是你的工程太简单了，要么是你根本不会写单测。

静态检查工具发现的是技术上的问题，单测则专注于发现业务上的问题。

**工具**

Junit Mockito TestNG...

### 3.2 运行时分析之Microbenchmark

**What**
> [A microbenchmark attempts to measure the performance of a "small" bit of code. These tests are typically in the sub-millisecond range. The code being tested usually performs no I/O, or else is a test of some single, specific I/O task](https://github.com/google/caliper/wiki/JavaMicrobenchmarks)

**When**
* 数据结构 or 算法的选择
* 三方包 or 类 or 方法的选择

**注意点**
平台、硬件环境、参数、其他影响。实践时多跑几次看平均结果。

**工具**
JMH、Caliper、Contiperf...

**实施**
JMH JDK团队出品，权威性无需质疑，一个非常好的[ABC文档](http://tutorials.jenkov.com/java-performance/jmh.html)。诸如

```
@BenchmarkMode(Mode.AverageTime)
@Warmup(iterations = 3)
@Measurement(iterations = 10)
@Fork(2)
public class MicroBenckMark {

    @Benchmark
    public void testDateTime(Blackhole blackhole) {
        for (int i=0;i<10000000;i++) {
            long mills = DateTime.now().getMillis();
            blackhole.consume(mills);
        }
    }

    @Benchmark
    public void testSystemTime(Blackhole blackhole) {
        for (int i=0;i<10000000;i++) {
            long mills = System.currentTimeMillis();
            blackhole.consume(mills);
        }
    }
}
```

### 3.2 运行时分析之系统工具

**CPU**

系统工具top/vmstat.

CPU指标：
1. CPU使用率
简单粗暴的讲，CPU使用率体现在Max(user/sys)这个值上，其中用户态CPU使用率为CPU执行应用程序代码的时间占用CPU总时间的比例，系统态CPU使用率为CPU执行操作系统调用的时间占用CPU总时间的比例，所谓系统调用包含IO、资源竞争等操作。
2. 除了CPU使用率之外，CPU另一个关键指标是负载也就是Load指标，注意与使用率不同，Load描述的是进程或者线程等待使用CPU的排队情况。使用率和Load之间并没有强相关的关系。一个非常经典的例子
> 某公用电话亭，有一个人在打电话，四个人在等待，每人限定使用电话一分钟，若有人一分钟之内没有打完电话，只能挂掉电话去排队，等待下一轮。电话在这里就相当于CPU，而正在或等待打电话的人就相当于任务数。
在电话亭使用过程中，肯定会有人打完电话走掉，有人没有打完电话而选择重新排队，更会有新增的人在这儿排队，这个人数的变化就相当于任务数的增减。为了统计平均负载情况，我们5分钟统计一次人数，并在第1、5、15分钟的时候对统计情况取平均值，从而形成第1、5、15分钟的平均负载。
有的人拿起电话就打，一直打完1分钟，而有的人可能前三十秒在找电话号码，或者在犹豫要不要打，后三十秒才真正在打电话。如果把电话看作CPU，人数看作任务，我们就说前一个人（任务）的CPU利用率高，后一个人（任务）的CPU利用率低。

3. CPU switches，这个指标通常也叫Context Switches，指的是在操作系统进程调度过程中进程切换的频率，具体可见：http://www.linfo.org/context_switch.html。在操作系统层面进程调度基本有如下几种：基于时间片、基于优先级的调度。Switch行为的发生情景有：i.当前线程时间片用完。ii.当前线程分配到时间片，但是由于线程阻塞（如Java中lock,sleep,wait）等导致无法利用时间片，switch到下一个线程。


**IO**
iostat -xm 1

**JVM**
* GC：jstat
* 线程：包含堆栈和忙线程查找。jstack top
* 堆：jmap, jmap -histo:live pid; jmap -dump:format=b,file=dump.file

线程热点分析：
找到占用CPU或者内存比较大的线程。
top H模式 线程PID 转换为 printf “%x/n” pid，jstack pid | grep threadId

### 3.3 运行时分析之Profiling

**分析工具**
JProfiler  YourKit  NetBeansProfiler

基本使用这里不在说，比较高频使用的一点是Hot Spot(Methods that consumed the most time)分析。

**原理**

* 事件方法：对于 Java，可以采用 JVMTI（JVM Tools Interface）API 来捕捉诸如方法调用、类载入、类卸载、进入 / 离开线程等事件，然后基于这些事件进行程序行为的分析。
* 统计抽样方法（sampling）: 该方法每隔一段时间调用系统中断，然后收集当前的调用栈（call stack）信息，记录调用栈中出现的函数及这些函数的调用结构，基于这些信息得到函数的调用关系图及每个函数的 CPU 使用信息。由于调用栈的信息是每隔一段时间来获取的，因此不是非常精确的，但由于该方法对目标程序的干涉比较少，目标程序的运行速度几乎不受影响。
* 植入附加指令方法（BCI）: 该方法在目标程序中插入指令代码，这些指令代码将记录 profiling 所需的信息，包括运行时间、计数器的值等，从而给出一个较为精确的内存使用情况、函数调用关系及函数的 CPU 使用信息。该方法对程序执行速度会有一定的影响，因此给出的程序执行时间有可能不准确。但是该方法在统计程序的运行轨迹方面有一定的优势。

>  https://www.ibm.com/developerworks/cn/java/j-lo-profiling/index.html

**采样形式**
* 快照，如stack dump
* 持续采样。

**展示形式**
* 趋势图
* 火焰图, 一个非显而易见的结论是：只要有"平顶"（plateaus），就表示该函数可能存在性能问题。
* 热点堆栈
