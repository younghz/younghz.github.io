---
layout: post
title: "【Es】Elasticsearch 乐观锁"
---

> 并发啊？    
> 锁！

## 1 问题情景
和多线程并发问题一样，在Es的读写过程中，同样会出现如下的情景。

同时 Get, 先后 Put.

## 2 方案
在数据库领域，一般有两种方案来解决这种并发update问题：    

* 悲观锁
* 乐观锁


Es的策略使用的是乐观锁。在create/deleted/update过程中， 文档的 version 都会增加。
方案是使用 `_version` 字段。

### 2.1 使用 源文档 version

** 要求：更新操作使用的version必须和源文档version一致。**

如：

```
PUT /website/blog/1?version=1
{
  "orderId": "1",
  "userId": "10"
}
```


如果源文档 version 为 1，那么更新文档， version自增 1。

此时，当 version 也就是 1 并不是当前 Es 中这个文档的version值时，会返回如下error:

```
{
  "error" : "VersionConflictEngineException[[website][2] [blog][1]:
             version conflict, current [2], provided [1]]",
  "status" : 409
}
```

### 2.2 使用 external version

** 要求：指定一个 long 类型的 version, 并指定 `version_type` 为 `external`, 此时，只要更新操作使用的version比 当前 doc 的version 大（不包含等于），那么就可以成功，否则失败。 **

如：

```
PUT /website/blog/1?version=10&version_type=external
{
  "orderId": "1",
  "userId": "10"
}
```

成功，那么当前 doc 的 version 变为 10， 失败的话，异常信息如上。

## 3 其他

测试，可直接使用。

参考：
https://www.elastic.co/blog/elasticsearch-versioning-support
