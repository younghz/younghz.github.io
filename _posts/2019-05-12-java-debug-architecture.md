---
layout: post
title: "Java Debug 原理与体系"
---

* 目录
{:toc}


# 1 前言

Debug 是问题排查最有效的方式之一。通常，在开发或者测试过程中，都会依赖 IDE 做 debug。比如常用的 IntelliJ IDEA 就提供了完备
的 debug 工具供开发者使用。但是，在 debug 过程中，我们只和 IDE 打交道，IDE 和 JVM 之间在 debug 过程中有什么样的交互？
进一步讲，如果是非本机 debug，一般使用 `remote debug` 模式调试远端代码，那么本地调试和远程调试有什么异同吗？它们都是怎么
实现的？

# 2 Java Debug 原理

在 Debug 领域，JDK 有一套规范与体系来支持，即 `Java Platform Debugger Architecture`，JPDA 体系。在 JPDA 体系中定义了
三个角色：

* Debuggge。被调试者。
* 传输纽带。
* Debugger。调试者。

每个角色又对应着不同的技术模块支撑，分别为 JVMTI/JDWP/JDI。如下。

// todo 这里是个图。https://www.ibm.com/developerworks/cn/java/j-lo-jpda1/index.html?ca=drs-

# 3 JPDA 体系

在 [ORACLE 文档中](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/) 对 JPDA 组成部分的描述：

> The Java Platform Debugger Architecture (JPDA) consists of three interfaces designed for use by debuggers in development environments for desktop systems. The Java Virtual Machine Tools Interface (JVM TI) defines the services a VM must provide for debugging. The Java Debug Wire Protocol (JDWP) defines the format of information and requests transferred between the process being debugged and the debugger front end, which implements the Java Debug Interface (JDI). The Java Debug Interface defines information and requests at the user code level.

## 3.1 JVMTI

> JVMTI（Java Virtual Machine Tool Interface）即指 Java 虚拟机工具接口，它是一套由虚拟机直接提供的 native 接口，它处于整个 JPDA 体系的最底层，所有调试功能本质上都需要通过 JVMTI 来提供。通过这些接口，开发人员不仅调试在该虚拟机上运行的 Java 程序，还能查看它们运行的状态，设置回调函数，控制某些环境变量，从而优化程序性能。我们知道，JVMTI 的前身是 JVMDI 和 JVMPI，它们原来分别被用于提供调试 Java 程序以及 Java 程序调节性能的功能。在 J2SE 5.0 之后 JDK 取代了 JVMDI 和 JVMPI 这两套接口，JVMDI 在最新的 Java SE 6 中已经不提供支持，而 JVMPI 也计划在 Java SE 7 后被彻底取代。

## 3.2 JDWP

> JDWP（Java Debug Wire Protocol）是一个为 Java 调试而设计的一个通讯交互协议，它定义了调试器和被调试程序之间传递的信息的格式。在 JPDA 体系中，作为前端（front-end）的调试者（debugger）进程和后端（back-end）的被调试程序（debuggee）进程之间的交互数据的格式就是由 JDWP 来描述的，它详细完整地定义了请求命令、回应数据和错误代码，保证了前端和后端的 JVMTI 和 JDI 的通信通畅。比如在 Sun 公司提供的实现中，它提供了一个名为 jdwp.dll（jdwp.so）的动态链接库文件，这个动态库文件实现了一个 Agent，它会负责解析前端发出的请求或者命令，并将其转化为 JVMTI 调用，然后将 JVMTI 函数的返回值封装成 JDWP 数据发还给后端。
> 另外，这里需要注意的是 JDWP 本身并不包括传输层的实现，传输层需要独立实现，但是 JDWP 包括了和传输层交互的严格的定义，就是说，JDWP 协议虽然不规定我们是通过 EMS 还是快递运送货物的，但是它规定了我们传送的货物的摆放的方式。在 Sun 公司提供的 JDK 中，在传输层上，它提供了 socket 方式，以及在 Windows 上的 shared memory 方式。当然，传输层本身无非就是本机内进程间通信方式和远端通信方式，用户有兴趣也可以按 JDWP 的标准自己实现。
## 3.3 JDI

> JDI（Java Debug Interface）是三个模块中最高层的接口，在多数的 JDK 中，它是由 Java 语言实现的。 JDI 由针对前端定义的接口组成，通过它，调试工具开发人员就能通过前端虚拟机上的调试器来远程操控后端虚拟机上被调试程序的运行，JDI 不仅能帮助开发人员格式化 JDWP 数据，而且还能为 JDWP 数据传输提供队列、缓存等优化服务。从理论上说，开发人员只需使用 JDWP 和 JVMTI 即可支持跨平台的远程调试，但是直接编写 JDWP 程序费时费力，而且效率不高。因此基于 Java 的 JDI 层的引入，简化了操作，提高了开发人员开发调试程序的效率。

关于这部分的详细介绍可以参考 [这个系列的四篇文章](https://www.ibm.com/developerworks/cn/java/j-lo-jpda1/index.html?ca=drs-)。

# 4 IDE 调试技巧

以 IntelliJ IDEA 为例，在 debug 方面提供了一系列的能力：

* Breakpoints in Java .
* Breakpoints in JavaScript.
* Multiple simultaneous debugging sessions.
* Customizable breakpoint properties: conditions, pass count, and so on.
* Frames, variables, and watches views in the debugger UI.
* Runtime evaluation of expressions.

IDEA 的 debug toolbar 包含了所有能力的实现，详细的使用方式可以参考：

* https://www.cnblogs.com/chiangchou/p/idea-debug.html
* https://www.jetbrains.com/help/idea/debugging-code.html

比较有用的几个调试技巧：

* 计算表达式。
* 回退断点。
* 线程堆栈。
* 断点条件设置。
* 变量查看与 watch。

# 5 总结

回头看在前言中的两个问题。问题一：在 debug 过程中，我们只和 IDE 打交道，IDE 和 JVM 之间在 debug 过程中有什么样的交互？

这个问题很明确，IDE 实现了 debug 的 ui,并且使用 JPDA 的一套接口实现了 debug 流程。

问题二：如果是非本机 debug，一般使用 `remote debug` 模式调试远端代码，那么本地调试和远程调试有什么异同吗？它们都是怎么
实现的？

其实本地和远程 debug 都是基于 JPDA，并且默认在 JDWP 层都是使用 socket 通信，只不过本地方式下链接的 targetVM 为 localhost，
远程 debug 连接的 targetVM 为远端机器。这个可以从启动参数看到，以直接在 IDE 中点击 debug 按钮为例，在本地 debug 时会输出如下日志：

> Connected to the target VM, address: '127.0.0.1:51267', transport: 'socket'。

并且在应用启动参数中同样包含如下配置：

> -agentlib:jdwp=transport=dt_socket,address=127.0.0.1:51267,suspend=y,server=n