---
layout: post
title: "技术文档写作规范与写作模板"
---

![write](../resource/tech_article_style_guide/write.jpeg)

* 目录
{:toc}

很长时间之前，想不起是在v2ex还是哪里见过一篇介绍中文文档写作规范的文章，印象最深的是其中对中文全角引号 `「」` 的介绍，在后来接触到的都是诸如 google-java-style-guide 等的编程规范。
写作，包含技术和非技术文章或书籍，都有固定的文法和套路。这个结论最初是从公众号「老道消息」写姚明那篇文章中得到的，后来也在摩登中产写的[姜文高高在下](https://mp.weixin.qq.com/s/VS9qzlG4Wuw44rxoof3wQg)中得到了印证，我的印象是，只要是写人的，都应该是这个套路。
前段时间在地铁上看了 斯蒂芬·金 的「[写作这回事:创作生涯回忆录](https://book.douban.com/subject/3888123/)」，尽管看不懂，但是觉得就应该是这么回事。

其实本想 Google 一下各类技术文章的写作模板，但是发现，不讲文章规范，写作模板虽然是有章可循的，但是还没有形成类似 Style Guide 这类文档约束。而文档写作规范，在新闻出版领域早已经是约定俗成的事，维基百科上还有专门针对这类规范汇总的[文章](https://en.wikipedia.org/wiki/List_of_style_guides#Newspapers)。财新的王烁在电子书「有效写作十三篇」就是针对经济学人的 Style Guide 的中文翻译与解读。

# 写作规范

这里不讲规范，只列参考。

* [ruanyf Github 收集](https://github.com/ruanyf/document-style-guide/blob/master/docs/reference.md)
* [中文技术文档的写作规范-ruanyf](http://www.ruanyifeng.com/blog/2016/10/document_style_guide.html)


针对非技术类，有一些专业的文章和书籍可供参考：

* [wikipedia](https://en.wikipedia.org/wiki/List_of_style_guides#Newspapers)
* [有效写作十三篇](https://www.amazon.cn/dp/B00J94V94E/ref=sr_1_1?ie=UTF8&qid=1528634342&sr=8-1&keywords=%E6%9C%89%E6%95%88%E5%86%99%E4%BD%9C%E5%8D%81%E4%B8%89%E7%AF%87)
* [哈佛非虚构写作课](https://book.douban.com/subject/26662600/)
* ...



# 写作模板

## 使用文档

#### 1 概览（Overview）

* 一段话阐述 xx 是什么。
* Features 说明。包含什么特性。
* Table of content。如果内容 3 部分内容较多，那么可在概览部分汇总列出。
* 名词解释。如果包含较多领域名词，可以在此部分列出说明。
* 使用要求。如对 JDK 版本、操作信息有要求。
* 架构图。路程图。
* 产品优势。
* 核心场景。
* 典型案例。
* 设计哲学。

#### 2 快速开始（Quick Start）

要点是通过一定方式体现 step1-stepN。其中的方式可以是通过在代码行或者截图中标注 ① ② … 等数字标记。 

#### 3 详细内容（Details）

根据具体内容，通过递进形式阐述。比如，如果内容较零散，可以用 EhCache 这种 Basic Topic、General Topic、Advanced Topic；内容本身递进，可以用 Junit 这种 Writing Test、Running Test模式。

#### 4 补充说明
* Release Notes。
* FAQ。
* Contributors。
等


* [Ehcache](http://www.ehcache.org/documentation/3.5/index.html)
* [Caffeine](https://github.com/ben-manes/caffeine/wiki)
* [Spring Framework Overview](https://docs.spring.io/spring/docs/5.0.0.RC3/spring-framework-reference/overview.html)


## 学习文档

5W1H 法则。


----

# 扯远一点

前两天看李笑来的「新生」，其中提到一个观点：
> 概念是一切知识的基石。

当时觉得说的对，但是不是特别清晰。今天又看见这本书，觉得这句话应该这么讲：没人可以记住所有希望记住的东西，包含知识，但是可以记住关键点，而这个点就是「概念」，以点带面就是所有。既然如此，在「新生」中除了这个概念点，还有一些也很有意思：

* 模式切换：苍蝇和蜜蜂的故事。
* 研究新事物：i) 模式切换；ii) 优先关注优点而不是缺点。
* 升级：不断升级自己，调整焦点，懂得容错。 
