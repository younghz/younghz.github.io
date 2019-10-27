---
layout: post
title: "Netty:核心实现"
---

* 目录
{:toc}

# 核心概念

Netty 核心实现包含下面几种：
* BootStrap、ServerBootStrap。用于创建 channel 的引导程序，或者叫做 helper class。其中前者用于创建 Channel，后者用于创建
ServerChannel(用于服务端接收连接并为连接创建 channel)。
* EventLoopGroup。EventLoop 集合，管理 EventLoop，对外提供 channel 注册接口，将 channel 轮询绑定到多个 EventLoop 上。
* EventLoop。处理注册到此 EventLoop 上的 channel 的 I/O 操作。一个 EventLoop 通常会绑定多个 channel 以达到多路复用的目的，也就是
I/O 模型中的多路复用模型。
* ChannelHandler。Channel 上的 I/O 事件处理器，也可进行 write 等 I/O 操作。其中 ChannelInboundHandler 用于处理 inbound I/O events，
ChannelOutboundHandler 用于进行 outbound I/O operations.
* ChannelHandlerContext。ChannelHandler 并不单独对外提供服务，而是通过 ChannelHandlerContext 封装提供，ChannelHandlerContext
将 Channel、EventLoop 和 ChannelHandler 绑定到一起，并将 ChannelHandler 和 ChannelPipeline 联系到一起，从而达到将 I/O 处理可以
从当前 ChannelHandler 传递到下一个 ChannelHandler 的目的。利用 ChannelHandlerContext 还可以达到动态修改 ChannelPipeline 的目的。
* ChannelPipeline。ChannelHandler 集合，I/O 事件和 I/O 操作都会在 pipeline 中的逐个 ChannelHandler 中传递。
* ByteBuf。提供更易用的 byte buffer API，以及更完善的内存泄露监控与处理。其实现包含基于 ByteBuffer 以及 byte[] 数组等形式的实现。
* Channel。是 Socket 的抽象，Netty 中使用其进行 I/O 操作，如连接、读写等。
* ChannelFuture。Channel I/O 操作的异步结果。Netty 中所有的 I/O 操作都是异步的，其操作异步结果便是 ChannelFuture。

# 详细分析

## EventLoop

EventLoop 有不同的实现，如 NioEventLoop，EpollEventLoop 等，不同的实现对应不同的底层系统调用，如 NioEventLoop 基于 select 系统调用，
而后者基于 epoll。下面以 NioEventLoop 为例说明 EventLoop 核心元素与接口实现。

NioEventLoop 核心属性为 Selector，即基于 select 系统调用的多路复用器。JDK 的 nio 包中已经提供了实现。
核心方法包含两个：
* register 方法。将 Channel 和此 EventLoop 绑定，其实是将 Channel 和多路复用器 Selector 绑定。
* run 方法。内部是一个无限循环，使用 Selector 进行 select 调用，找到所有准备就绪的 channel，
并判断当前是 connect read 还是 write 操作。以 read 为例，如果是 read ,那么会调用此 channel read 方法，
见 AbstractNioByteChannel#read()，其中会将数据读取到 ByteBuf 中并调用此 Channel
pipeline 的 `pipeline.fireChannelRead(byteBuf)` 方法将数据传递给每个 ChannelHandler 处理。


## EventLoopGroup

其常用核心属性有两个。
```java
    public NioEventLoopGroup(int nThreads, ThreadFactory threadFactory) {
        this(nThreads, threadFactory, SelectorProvider.provider());
    }
```

分别是 nThreads 和 threadFactory.

nThreads 表示当前 EventLoopGroups 会创建的 EventLoop 的个数，因为 EventLoop 都是单线程（SingleThreadEventLoop子类）的，估计因此
此参数不叫 nEventLoop 而叫 nThreads。

threadFactory 为创建 EventLoop 线程的线程工厂，一般用来定制线程名字。

## ChannelPipeline

在 EventLoop 部分内容已经说过，当 channel 事件来临后，会交给 channel 的 pipeline 处理，下面看下 pipeline 的内容。

下图展示的是一个 I/O 事件如何在 ChannelPipeline 中流转，被 ChannelHandler 处理。

```text
                                                I/O Request
                                            via {@link Channel} or
                                        {@link ChannelHandlerContext}
                                                      |
  +---------------------------------------------------+---------------+
  |                           ChannelPipeline         |               |
  |                                                  \|/              |
  |    +---------------------+            +-----------+----------+    |
  |    | Inbound Handler  N  |            | Outbound Handler  1  |    |
  |    +----------+----------+            +-----------+----------+    |
  |              /|\                                  |               |
  |               |                                  \|/              |
  |    +----------+----------+            +-----------+----------+    |
  |    | Inbound Handler N-1 |            | Outbound Handler  2  |    |
  |    +----------+----------+            +-----------+----------+    |
  |              /|\                                  .               |
  |               .                                   .               |
  | ChannelHandlerContext.fireIN_EVT() ChannelHandlerContext.OUT_EVT()|
  |        [ method call]                       [method call]         |
  |               .                                   .               |
  |               .                                  \|/              |
  |    +----------+----------+            +-----------+----------+    |
  |    | Inbound Handler  2  |            | Outbound Handler M-1 |    |
  |    +----------+----------+            +-----------+----------+    |
  |              /|\                                  |               |
  |               |                                  \|/              |
  |    +----------+----------+            +-----------+----------+    |
  |    | Inbound Handler  1  |            | Outbound Handler  M  |    |
  |    +----------+----------+            +-----------+----------+    |
  |              /|\                                  |               |
  +---------------+-----------------------------------+---------------+
                  |                                  \|/
  +---------------+-----------------------------------+---------------+
  |               |                                   |               |
  |       [ Socket.read() ]                    [ Socket.write() ]     |
  |                                                                   |
  |  Netty Internal I/O Threads (Transport Implementation)            |
  +-------------------------------------------------------------------+

```

围绕 Inbound/Outbound 两个概念，有 Inbound/Outbound 事件、Inbound/Outbound 传播方法、Inbound/Outbound 处理器这几个概念。
其中 Inbound/Outbound 事件由传播方法触发，并经过处理器处理。

其中 Inbound event 传播方法如下，即以 fire 开头的方法。在当前的 ChannelHandlerContext 调用此方法，会将时间传递给下一个 Handler。

* ChannelHandlerContext#fireChannelRegistered()}
* ChannelHandlerContext#fireChannelActive()}
* ChannelHandlerContext#fireChannelRead(Object)}
* ChannelHandlerContext#fireChannelReadComplete()}
* ChannelHandlerContext#fireExceptionCaught(Throwable)}
* ChannelHandlerContext#fireUserEventTriggered(Object)}
* ChannelHandlerContext#fireChannelWritabilityChanged()}
* ChannelHandlerContext#fireChannelInactive()}
* ChannelHandlerContext#fireChannelUnregistered()}


其中 outbound event 传播方法如下，非 fire 开头的方法。同样的在当前的 ChannelHandlerContext 调用此方法，会将时间传递给下一个 Handler。

* ChannelHandlerContext#bind(SocketAddress, ChannelPromise)}
* ChannelHandlerContext#connect(SocketAddress, SocketAddress, ChannelPromise)}
* ChannelHandlerContext#write(Object, ChannelPromise)}
* ChannelHandlerContext#flush()}
* ChannelHandlerContext#read()}
* ChannelHandlerContext#disconnect(ChannelPromise)}
* ChannelHandlerContext#close(ChannelPromise)}
* ChannelHandlerContext#deregister(ChannelPromise)}

ChannelPipeline 的默认实现是 DefaultChannelPipeline，其会在你配置的 ChannelHandler 之前增加 HeadHandler，在之后增加 TailHandler。
二者会自动的增加一些操作，如你并不用在你的 ChannelHandler 中实现真正调用 socket 的write 发送数据，这个在 HeadHandler 中已经默认
为你做了，可见 HeadHandler(HeadContext)的 write 方法的实现，岂会调用 channel 的 unsafe 代理发送数据。

## ByteBuf

ByteBuf 是 Netty 的I/O byte 数据 buffer 实现，其没有直接使用 JDK nio 下的 ByteBuffer。
ByteBuf 较 JDK 的 ByteBuffer 的优势是：
* 读和写用不同的索引。
* 读和写可以随意的切换，不需要调用flip()方法。
* 容量能够被动态扩展，和StringBuilder一样。
* 用其内置的复合缓冲区可实现透明的零拷贝。
* 支持方法链。
* 支持引用计数。count == 0,release。
* 支持池。

ByteBuf 使用了读写双指针的实现，下面是一个 Buffer 的双指针分割效果。

```text

+-------------------+------------------+------------------+
| discardable bytes |  readable bytes  |  writable bytes  |
|                   |     (CONTENT)    |                  |
+-------------------+------------------+------------------+
|                   |                  |                  |
0      <=      readerIndex   <=   writerIndex    <=    capacity

```

ByteBuf 核心 API:
* readableBytes()。当前可读字节数。
* isReadable()。当前是否可读，有内容。
* readxxx()。读取对应内容。
* writexxx()。向 buffer 中写入内容。
* readBytes(byte[] dst，xxx)。将 ByteBuf 内容读到 dst 数组中。
* writeBytes(byte[] src,xxx)。将 src 数组内容写入到 ByteBuf 中。


Derived buffers API 包含：
* duplicate()：直接拷贝整个buffer。
* slice()：拷贝buffer中已经写了的数据。
* slice(index,length): 拷贝buffer中从index开始，长度为length的数据。
* readSlice(length): 从当前readIndex读取length长度的数据。

我对上面这几个方法的形容虽然是拷贝，但是这几个方法并没有实际意义上去复制一个新的buffer出来，它和原buffer是共享数据的。
所以说调用这些方法消耗是很低的，并没有开辟新的空间去存储，但是修改后会影响原buffer。这种方法也就是咱们俗称的浅拷贝。
要想进行深拷贝，这里可以调用copy()和copy(index,length)方法，使用方法和上面介绍的一致，但是会进行内存复制工作，效率很低。

ByteBuf 的创建尽量使用工厂方法 Unpooled, 而不是 new 出来。


## ChannelFuture

如前所述，Channel I/O 操作的异步结果。Netty 中所有的 I/O 操作都是异步的，其操作异步结果便是 ChannelFuture。

从 ChannelFuture 的 API 中可以判断对应的操作是否已经完成，是否成功等。可见。

```text
                                     +---------------------------+
                                     | Completed successfully    |
                                     +---------------------------+
                                +---->      isDone() = true      |
+--------------------------+    |    |   isSuccess() = true      |
|        Uncompleted       |    |    +===========================+
+--------------------------+    |    | Completed with failure    |
|      isDone() = false    |    |    +---------------------------+
|   isSuccess() = false    |----+---->      isDone() = true      |
| isCancelled() = false    |    |    |       cause() = non-null  |
|       cause() = null     |    |    +===========================+
+--------------------------+    |    | Completed by cancellation |
                                |    +---------------------------+
                                +---->      isDone() = true      |
                                     | isCancelled() = true      |
                                     +---------------------------+
```

也可以向 ChannelFuture 中注册监听器GenericFutureListener来达到结果被动通知的效果。


# 总结
如上。
