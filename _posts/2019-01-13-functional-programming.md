---
layout: post
title: "函数式编程"
---

* 目录
{:toc}

Java8 较之前版本 Java 最主要的改变是「函数式编程」的引入与实践。

# 1 函数式编程

函数式编程的定义（[wikipedia](https://zh.wikipedia.org/wiki/%E5%87%BD%E6%95%B8%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80)）：

> 函数式编程（英语：functional programming）或称函数程序设计，又称泛函编程，是一种编程范式，它将计算机运算视为数学上的函数计算，并且避免使用程序状态以及易变对象。函数编程语言最重要的基础是λ演算（lambda calculus）。而且λ演算的函数可以接受函数当作输入（引数）和输出（传出值）。    
比起指令式编程，函数式编程更加强调程序执行的结果而非执行的过程，倡导利用若干简单的执行单元让计算结果不断渐进，逐层推导复杂的运算，而不是设计一个复杂的执行过程。

函数式编程可能产生的副作用（[wikipedia](https://zh.wikipedia.org/wiki/%E5%87%BD%E6%95%B8%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80)）：

> 函数式编程常被认为严重耗费CPU和存储器资源。主因有二   
* 在实现早期的函数式编程语言时并没有考虑过效率问题。    
* 面向函数式编程特性（如保证函数参数不变性等）的独特数据结构和算法。   

从函数式编程的定义看，函数式编程思想的核心在于：

1. 函数。
2. 声明式编程。

## 1.1 函数

需要注意的是，「函数式编程」对「函数」的定义不是通常所讲的「类中的方法」，这里的函数是指数学中的函数定义：对于同样参数的输入，总会返回同样的结果，结果不会随调用次数的改变而改变。从这个角度，可以说「函数」是无状态的。

从另一个角度讲，函数是无副作用的，函数应避免修改共享状态或执行其它有副作用的操作（如改变输入）。

举个例子来讲：

```java
static List<List<Integer>> concat(List<List<Integer>> a,
                                      List<List<Integer>> b) {
        a.addAll(b);
        return a; 
}

```

```java
    static List<List<Integer>> concat(List<List<Integer>> a,
                                      List<List<Integer>> b) {
        List<List<Integer>> r = new ArrayList<>(a);
        r.addAll(b);
        return r;
}
```

在上面两段代码中，下面的是一种纯粹的函数式编程方式。（这里只说风格与编程范式，忽略方式二带来的内存和时间消耗弊端）

## 1.2 声明式编程

「声明式编程」是针对「命令式编程」而言，如函数式编程的定义所述，函数式编程关注的是执行的结果而非过程，而声明式编程就是拿到结果的阐述过程。如下，针对于第一种命令式编程方式，第二段声明式编程代码以一种「做什么的陈述过程」简洁方式得到结果，其他的交给函数库和内部迭代。

代码一
```java
Transaction mostExpensive = transactions.get(0);
    if(mostExpensive == null)
throw new IllegalArgumentException("Empty list of transactions")
for(Transaction t: transactions.subList(1, transactions.size())){ if(t.getValue() > mostExpensive.getValue()){
            mostExpensive = t;
        }
}
```

代码二
```java
Optional<Transaction> mostExpensive =
    transactions.stream()
                .max(comparing(Transaction::getValue));
```

# 2 函数式编程实践

## 2.1 行为参数化

行为参数化是指将行为（代码）通过参数传递给类或方法。

下面是一个 filter 的例子：

```java
public static List<Apple> filterApplesByWeight(List<Apple> inventory, int weight) {
        List<Apple> result = new ArrayList<Apple>();
        For (Apple apple: inventory){
if ( apple.getWeight() > weight ){ result.add(apple);
} }
        return result;
    }
```

下面将过滤行为（代码）封装起来，并以参数形式传递给 filter 方法，实现更好的「扩展」。

```java
 public interface ApplePredicate{
        boolean test (Apple apple);
} 

public class AppleHeavyWeightPredicate implements ApplePredicate { 
    public boolean test(Apple apple){
        return apple.getWeight() > 150;
    }
}

public static List<Apple> filterApples(List<Apple> inventory,
                                           ApplePredicate p){
        List<Apple> result = new ArrayList<>();
        for(Apple apple: inventory){
            if(p.test(apple)){
                result.add(apple);
            }
        }
    return result;
}
```

更进一步，如果传递的行为代码只会使用一次，可以使用 __匿名类__ 完成，如

```java
List<Apple> redApples = filterApples(inventory, new ApplePredicate() {
     public boolean test(Apple a){
        return "red".equals(a.getColor()); 
    }
});
```

在 Java8 中，可以借助 lambda 进一步简化上述代码：

```java
List<Apple> result =
    filterApples(inventory, (Apple apple) -> "red".equals(apple.getColor()));
```

## 2.2 lambda

什么是 lambda？

lambda 通常是指 lambda表达式，其概念来源于[lambda演算](https://baike.baidu.com/item/%CE%BB%E6%BC%94%E7%AE%97)，lambda 表达式可以支持以简洁的形式 __表示一个行为或者传递代码__。

在 Java 中，所有的 __函数式接口__ 都可以用 lambda 表达式表示，那么什么是函数式接口呢？简单来说，就是「只定义一个抽象方法的接口」。可以在 `java.util.function` 找到所有 JDK 自带的函数式接口。如：

* 两个输入一个输出的 BiFunction。
* 包含一个输入，返回空的 Consumer。
* 一个输入一个输出的 Function。
* 用于验证的 Predicate。
* 抽象提供逻辑的 Supplier。
* ...

## 2.3 Stream - 函数式数据处理

Java8 中提供了流式数据处理 API - Stream。Stream API 支持以声明式进行数据处理。如：

```java
List<String> lowCaloricDishesName =
            menu.stream()
            .filter(d -> d.getCalories() < 400) 
            .sorted(comparing(Dish::getCalories))
            .map(Dish::getName)
            .collect(toList());
```

`流` 的概念包含以下几部分：

> * 源。流会使用一个提供数据的源，如集合、数组或输入/输出资源。 请注意，从有序集 合生成流时会保留原有的顺序。由列表生成的流，其元素顺序与列表一致。
* 数据处理操作。流的数据处理功能支持类似于数据库的操作，以及函数式编程语言中 的常用操作，如filter、map、reduce、find、match、sort等。流操作可以顺序执行，也可并行执行。
* 流水线。很多流操作本身会返回一个流，这样多个操作就可以链接起来，形成一个大的流水线。这让我们下一章中的一些优化成为可能，如延迟和短路。流水线的操作可以看作对数据源进行数据库式查询。
* 内部迭代。与使用迭代器显式迭代的集合不同，流的迭代操作是在背后进行的。我们在第1章中简要地提到了这个思想，下一节会再谈到它。

流的使用一般包括三件事:

* 一个数据源(如集合)来执行一个查询;
* 一个中间操作链，形成一条流的流水线; filter/map/sort/limit
* 一个终端操作，执行流水线，并能生成结果。foreach/count/collect

# 3 总结

函数式编程是一种使用数学意义上函数进行编程的思想。其关注无状态、声明式。Java8 引入了 lambda 作为对函数式编程的支持，并内置了流式处理库 Stream 支持数据的函数式处理。

# 4 其它

Java 8 还提供了新的日期和时间 API。众所周知，Java8 之前的关于时间的API除了不具有线程安全性，在易用性方面也大打折扣，比如你希望在一个日期的基础上增加一天，在之前的API中，这个简单的要求却引入一个复杂的实现。所以，在涉及到日期或时间处理时，大部分都会使用三方包如 joda-time。

新的 java.time 包中提供了 LocalDate、LocalTime、Instant、Duration和Period。

LocalDate 与 LocalTime 分别为日期与时间 API。

Period:  A date-based amount of time in the ISO-8601 calendar system, such as '2 years, 3 months and 4 days'.

Duration: A time-based amount of time, such as '34.5 seconds'.

Instant:  An instantaneous point on the time-line. This class models a single instantaneous point on the time-line. This might be used to record event time-stamps in the application.