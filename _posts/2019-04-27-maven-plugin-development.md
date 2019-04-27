---
layout: post
title: "Maven Plugin Development"
---

* 目录
{:toc}

# 1 前言

和之前说过的 JetBrains 插件一样，Maven Plugin 也是用于提高效率的开发工具，只是在应用上，各有各的适用情景。
开发工具主要有两方面的作用，其一是标准化，其二是自动化。自动化的目的与结果都是为了提高生产效率，提高生产质量。

# 2 开发实践

## 2.0 基本概念

开发 Maven 插件主要关注以下几个点：
1. 插件开发周期。即建立工程、开发、测试、打包、发布、使用。
2. 接口与数据结构。即使用哪些 API，有哪些数据模型。

下面 step by step 说一下过程与注意点。

## 2.1 搭建工程

可以手动通过 archetype 生成一个插件骨架工程，如下：

```text
mvn archetype:generate \
 -DgroupId=sample.plugin \
 -DartifactId=hello-maven-plugin \
 -DarchetypeGroupId=org.apache.maven.archetypes \
 -DarchetypeArtifactId=maven-archetype-plugin
```

一般 IDE 中集成了插件工程的创建流程，可以在 IDE 中 new project 新建。

## 2.2 依赖

插件开发主要关注四个依赖。

### I) 插件 API

其中包含插件开发所需实现的 API，如 Mojo。每个插件都需要实现这个接口实现 execute 方法编排执行逻辑。

```text
<dependency>
           <groupId>org.apache.maven</groupId>
           <artifactId>maven-plugin-api</artifactId>
           <version>3.6.0</version>
       </dependency>
```

### II) 注解包

可以使用注解定义插件 goal，执行声明周期等属性。包含如 @Mojo、@Execute 注解。

```text
       <dependency>
           <groupId>org.apache.maven.plugin-tools</groupId>
           <artifactId>maven-plugin-annotations</artifactId>
           <version>3.6.0</version>
           <scope>provided</scope>
       </dependency>
```

### III) 核心包

包含了插件开发中所有的数据结构。如 MavenSession，MavenProject 等。

```text
       <dependency>
           <groupId>org.apache.maven</groupId>
           <artifactId>maven-core</artifactId>
           <version>3.6.0</version>
       </dependency>
```

### IV) 其它插件包、工具包

一般来讲，大部分你想要的功能都可以找到对应的实现，如果你希望基于某个插件的功能包装或者定制，那么可以依赖
相应的插件包并继承相应的类，增加定制参数与逻辑。


## 2.3 开发

### 2.3.1 execute 

核心概念：
* Mojo。即插件 goal/task。

插件通过 Mojo 注解定义自己身份、执行时间点等属性，在 execute 中实现插件逻辑。

```java
@Mojo( name = "sayhi")
public class GreetingMojo extends AbstractMojo
{
   public void execute() throws MojoExecutionException
   {
       getLog().info( "Hello, world." );
   }
}
```

Mojo 注解的核心属性可以通过其属性注释查看。
如果希望 fork 进程执行，可以使用 @Execute 注解标记在 Mojo 上。

### 2.3.2 parameters

参数分两种：
1. 框架参数。你可以注入 Maven 框架提供的属性，如通过 @Parameter(defaultValue = "${project}", readonly = true) protected MavenProject project; 方式
注入MavenProject属性，可以通过此种方式注入的属性包含 https://maven.apache.org/ref/current/maven-core/apidocs/org/apache/maven/plugin/PluginParameterExpressionEvaluator.html。
2. 自定义参数。

自定义参数如：

```text
   @Parameter( property = "greeting", defaultValue = "Hello World!" )
   private String greeting;
```

可以通过如下方式配置注入：

```text
<plugin>
 <groupId>sample.plugin</groupId>
 <artifactId>hello-maven-plugin</artifactId>
 <version>1.0-SNAPSHOT</version>
 <configuration>
   <greeting>Welcome</greeting>
 </configuration>
</plugin>
```

其它类型参数的配置形式可以参考 https://maven.apache.org/guides/plugin/guide-java-plugin-development.html。

### 2.3.2 核心数据结构

核心数据结构都可以在 https://maven.apache.org/ref/current/maven-core/apidocs/org/apache/maven/plugin/PluginParameterExpressionEvaluator.html。
找到并通过表达式方式注入。

整体上下文为 MavenSession，最常使用到的应该是 MavenProject，MavenProject 是对 Maven 管理项目的抽象，如源码路径、构建路径、pom 信息等等。

## 2.4 测试

Maven 提供了 [Maven Plugin Testing Harness](https://maven.apache.org/shared/maven-plugin-testing-harness/)
作为测试工具。

更为直接的方式是直接在项目中引用通过 Maven Debug 形式测试。测试步骤为：
1. 配置 RemoteDebug，端口为 8000。
2. 本地执行 MvnDebug，如 MvnDebug clean package。

## 2.5 打包

和正常 jar 打包方式一样，执行 clean package/deploy 。

## 2.7 使用

使用分两种形式：
1. pom 形式。在 pom 中声明并配置插件。此种形式可以和生命周期绑定，也可以不绑定。
2. command line 形式。`mvn groupId:artifactId:version:goal`。

# 3 总结 & 参考

* [已有插件](https://maven.apache.org/plugins/)
* [Guide Java Plugin Development](https://maven.apache.org/guides/plugin/guide-java-plugin-development.html)
