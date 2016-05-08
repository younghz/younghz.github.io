---
layout: post
title: "【code】Elasticsearch 缓存"
---

## 1 Filter cache

所谓的 filter cache 就是负责缓存查询中filter的结果的。默认的 filter cache的实现就是 **node filter cache**。

### 1.1 node filter cache(默认的filter cache 类型)

所谓的 nodel filter cache 就是节点(node)维度的cache，节点上所有的shard 共用这个cache。使用LRU作为其失效策略。

##### 配置

**配置方式一**

~~~~
// 无需配置是否使用，默认使用
indices.cache.filter.size //这个配置默认值是总内存的 %10

// 可以配置为 %10或者实际的数量如 512mb
~~~~

参考：
https://www.elastic.co/guide/en/elasticsearch/reference/1.7/index-modules-cache.html

**配置方式二**
网上很多资料的配置方式都是使用的都是 `index.cache.filter.type` 等配置。

首先，应该使用配置一方式，在1.7的文档中并未对此种配置有说明。在 Master Elasticesarch书中找到的说明如下：

`index.cache.filter.type` 配置为node时（这也是这个参数的默认配置），就等同于使用 `indices.cache`, 正如配置一种所述的，node cache 是无需配置是否使用的，他是默认使用。所以仍然推荐方式一的配置方式。

参考：    
《Master elasticsearch》的Index-level filter cache configuration 章节

## 2 Query cache

### 2.1 Shard query cache

shard-level 的 cache 缓存每次执行在当前shard上的结果。

需要要注意的是：    
query cache 只缓存count类型的搜索，不会缓存 hits。

##### 配置

~~~~
index.cache.query.enable: true //默认配置是false，也就是默认没有这个配置
indices.cache.query.size: 2%  //默认配置 1%
indices.cache.query.expire // 失效时间, 不需要设置，因为本身是是是更新的
~~~~

##### 监控

监控API
~~~~
curl 'localhost:9200/_stats/query_cache?pretty&human'
~~~~


参考：
https://www.elastic.co/guide/en/elasticsearch/reference/1.7/index-modules-shard-query-cache.html#_cache_invalidation

## 3 Field data cache

Field data 缓存主要是在字段 sort 或者 aggregating时被用到。

使用这个缓存时，ES会吧这个字段的所有值都load出来，所以一定要确保有足够的缓存处理它，并且使缓存一直保留，避免多次重建。

##### 配置

~~~~
indices.fielddata.cache.size    // 缓存的大小 %10或者512mb, 默认是unbounded
indices.fielddata.cache.expire // -1为没有过期时间（推荐设置）
~~~~

------
ES本身包含多种 Circuit Breaker（熔断器）来避免诸如 导致OOM这类的情景的操作。 每个熔断器致命可使用内存的大小，一个父熔断器可指明所有子熔断器的可使用内存大小。

父熔断器的设置：    
indices.breaker.total.limit  // 默认的设置是70%
------

同理，fielddata的熔断器设置如下

~~~~
indices.breaker.fielddata.limit // 默认值为JVMheap的60%
~~~~

监控API：

~~~~
curl -XGET 'http://localhost:9200/_stats/fielddata/?fields=field1,field2&pretty'
~~~~

所有的监控API见：    
https://www.elastic.co/guide/en/elasticsearch/reference/1.7/cluster-nodes-stats.html


#### 参考文章:
https://abhishek376.wordpress.com/2014/11/24/how-we-optimized-100-sec-elasticsearch-queries-to-be-under-a-sub-second/
