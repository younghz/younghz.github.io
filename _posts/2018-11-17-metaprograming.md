---
layout: post
title: "【T】Java metaprograming"
---

WikiPedia 上对元编程的定义是：

> 元编程（英语：Metaprogramming），又译超编程，是指某类计算机程序的编写，这类计算机程序编写或者操纵其它程序（或者自身）作为它们的资料，或者在运行时完成部分本应在编译时完成的工作。多数情况下，与手工编写全部代码相比，程序员可以获得更高的工作效率，或者给与程序更大的灵活度去处理新的情形而无需重新编译。

编写元程序的语言称之为元语言。被操纵的程序的语言称之为“目标语言”。一门编程语言同时也是自身的元语言的能力称之为“反射”或者“自反”。

__元编程工具主要有以下几种：__

* 代码（.java）生成器（处理器）。
* 字节码（.class）增强（转换）。
* 运行时反射。

## 1 代码生成器
代码生成器是分析源代码生成新的代码的工具。

Spoon 就是代码生成器的一种（也可以用作运行时反射接口的替代品）。

另外一种被广泛的使用工具是 Pluggable Annotation Processing API，著名的 lombok 就是基于此实现。「 Pluggable Annotation Processing API」为 JSR269 规范的内容，在 JDK6 中被引入，意在代替 JDK5 引入的 APT「Annotation Processing Tool」。Javac 编译过程如下：

<p style="text-align:center">
<img src="../resource/java_metaprogramming/annotation_processing.jpg"  width="500"/>
</p>

* 1. javac对源代码进行分析，生成一棵抽象语法树(AST) 
* 2. 运行过程中调用实现了"JSR 269 API"的A程序
* 3. 此时A程序就可以完成它自己的逻辑，包括修改第一步骤得到的抽象语法树(AST)
* 4. javac使用修改后的抽象语法树(AST)生成字节码文件

使用例子：
* lombok。
* Spoon（还有其它功能）。

## 2 反射
如 WikiPedia 中对元编程的定义一样，所谓的反射就是 语言自己编写自己代码 的过程。

通过反射，可以获取到类内部属性、方法等信息。同时可以实例新的类，如「动态代理」。

关于代理模式以及动态代理，可见 代理模式原理及实例讲解。

使用例子：
* Spring AOP 中基于JDK代理的实现就是这种方式（使用限制为需要时接口类）。
* Junit/TestNG 使用反射来处理注解。

## 3 字节码增强
和 2.1 中的生成代码不一样，字节码工具是分析并修改/生成字节码的工具。如 Spring AOP 中，如果对象类没有实现接口，那么会使用 CGlib，通过继承对象类进行动态代理。

使用例子：
* Javassist。
* ASM。基于 ASM 的 CGLIB 等。

<p style="text-align:center">
<img src="../resource/java_metaprogramming/asm_cglib.png"  width="500"/>
</p>


## 3 总结
如上所说的三种形式（代码生成，字节码增强，反射）可以在不同阶段（编译期、运行期）做元编程的实现工具。Java 注解为元编程的形式之一，上述方式同样适用于注解的实现。

参考：

* [John Heintz谈如何向Java注解添加行为](http://www.infoq.com/cn/news/2008/08/nfjs2008-annotations)
* [https://tech.youzan.com/java-metaprograming/](https://tech.youzan.com/java-metaprograming/)