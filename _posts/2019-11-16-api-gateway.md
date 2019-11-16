---
layout: post
title: "分布式系统之 API 网关"
---

* 目录
{:toc}


## 1 概念

在 API 网关之前，先看下单纯「网关」的概念，维基百科中对于「网关」描述是：

> 在计算机网络中，网关（英语：Gateway）是转发其他服务器通信数据的服务器，接收从客户端发送来的请求时，
它就像自己拥有资源的源服务器一样对请求进行处理。有时客户端可能都不会察觉，自己的通信目标是一个网关。
网关也经常指把一种协议转成另一种协议的设备，比如语音网关。

从上面的概念中，可以找到网关的几个特性：业务无关、数据转发、无感知、协议转换。

API 网关以 API 为核心，且具有网关特性。在[腾讯云的 API 网关产品](https://cloud.tencent.com/product/apigateway#scenarios)
中，对 API 网关的描述为：

> API 网关（API Gateway）是 API 托管服务。提供 API 的完整生命周期管理，包括创建、维护、发布、运行、下线等。您可使用 API Gateway 
封装自身业务，将您的数据、业务逻辑或功能安全可靠的开放出来，用以实现自身系统集成、以及与合作伙伴的业务连接。

## 2 情景

从上述 API 网关的定义中，也可以发现 API 网关的使用场景，一般是：（以下来自[阿里云API网关产品](https://www.aliyun.com/product/apigateway/)描述）

* 轻松实现系统集成，规范化、标准化。企业发展，唯快不破。但是在快速发展的过程中往往不成体系、重复开发、烟囱式建设，造成资源冗余和浪费，通API网关可轻松实现企业内的系统集成。
* 多端兼容。安全实现多端统一，一套服务，多端输出。随着移动、物联网的普及，API 需要支持更多的终端设备，以扩充业务规模，但同时也带来系统复杂性的提升。通过 API 网关可以使 API 适配多端，企业只需要在 API 网关调整 API 定义，无需做额外工作。
* 建立 API 生态，合作伙伴深度协同。如今企业面临更多的挑战，企业发展需要可靠的合作伙伴。企业与合作伙伴以 API 的形式进行服务、能力和数据的交互，系统与系统直接对接，达成深度合作，建立牢固的合作关系。
* 拥抱 API 经济，开拓新商业模式。面对用户日益膨胀而又碎片化的需求，企业需要不断探索新的商业模式，来解决客户一系列的场景化问题。通过API网关提供标准的 API 服务，让其他开发者将不同 API 服 务组合整合到自己的应用中，衍生出新的服务，促进企业建立商业生态、跨界创新。


## 3 特性

<p style="text-align:center">
<img src="../resource/api_gateway/kong_api_feature.jpg" alt="sample" width="500"/>
</p>
从 API 网关产品 [Kong](https://github.com/Kong/kong) 的介绍中，可以找到网关产品的主要特性。除此之外，任何 API 相关的通用
特性都可以集成在网关中。

## 4 解决方案


* Kong kong是基于Nginx+Lua进行二次开发的方案， https://konghq.com/
* Netflix Zuul，Spring cloud 中有完善开箱即用的集成，https://github.com/Netflix/zuul
* orange， http://orange.sumory.com/


* Amazon API Gateway，https://aws.amazon.com/cn/api-gateway/
* 阿里云API网关，https://www.aliyun.com/product/apigateway/
* 腾讯云API网关， https://cloud.tencent.com/product/apigateway

