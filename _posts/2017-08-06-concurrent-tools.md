---
layout: post
title: "【T】JAVA并发编程（四）并发工具与容器"
---

这里分为如下几部分：
* 同步工具
* 并发容器
* 原子变量

## 1. 同步工具

### 1.1 状态依赖
所谓的状态依赖，是指任务的执行需要一些先验条件的满足，这些条件就是任务向下执行依赖的状态。
如BlockingQueue offer操作的先验条件是队列未满。

针对这种状态依赖，通常的两种策略是：
* 状态不满足，直接返回。
* 状态不满足，阻塞。当状态满足是被唤醒继续执行。

这里只阐述第二种策略的实现方式

**1.1.1 轮询加休眠**

```java
public void doThings() throws Exception{

    while (true) {
        synchronized (this) {
            if (isStateSatisfied()) {
                // do your things
            }

            Thread.sleep(100);
        }
    }
}
```

缺点:
* 大量业务无关的代码，复杂。
* 休眠时间不好控制，太长影响响应性，太短会加大CPU消耗。

**1.1.2 条件队列**

条件队列可以让一组线程以某种方式等待条件变为真。对象 **内部条件队列** 相关的API包含 wait()/notifyAll()/notify()。

```java
public synchronized void doThings() throws Exception {

    while (!isStateSatisfied()) {
        // wait
        wait();
    }

    // do your things

    // notify
    notifyAll();
}
```

类似于显式锁Lock对内部锁synchronized的扩展，Condition也是对内部条件队列的拓展。

**1.1.3 AbstractQueuedSynchronizer**

AQS是构建锁和synchronizer的框架，像锁ReentrantLock，以及信号量、CountDownLatch、FutureTask等同步器都是
基于AQS框架构建的。

## 2. 并发容器

这里只简单的谈谈ConcurrentHashMap。

ConcurrentHashMap的产生是为了解决HashMap的线程不安全性以及HashTable的效率低下。前者在并发的情况下可能造成Entry链表
形成环形，而后者在内部使用synchronized保证线程安全但是效率低下。

ConcurrentHashMap的思路是通过数据分段为锁分段提供条件，已到达最小的锁竞争。

## 3. 原子变量与非阻塞同步机制

锁的缺点主要体现在获取不到锁时：
* 线程挂起和恢复的CPU开销
* 线程挂起后需要等待再次被调度，此时的实时性问题

与锁这种悲观的方式比较，更乐观的策略通常是冲突检测。当前的多处理器的操作系统，针对于并发通常提供了底层的原子操作的支持，
如CAS（compare and set）等。

Java提供的原子变量包括AtomicInteger/AtomicLong等变量，通常非阻塞算法与数据结构都是基于如上原子变量以及volatile变量
构建起来的。
