---
layout: post
title: "Http Client"
---

* 目录
{:toc}

在基于 HTTP 的通信中，存在 HTTP Client 和 HTTP Server 两个角色，在 Java 中，无需三方依赖就可以构建出简单点的 Client 和 Server。Client 可以基于 `java.net` 下的HtttpUrlConnection 实现，而 Server 可以基于 `com.sun.net.httpserver` 下的 HttpServer 构建。

当谈到 HTTP Client 的三方实现类时，通常会基于以下标准对其进行评价：

1. 协议支持。是否实现了完整的 HTTP 协议（如支持所有 HTTP Method）以及是否支持高版本的协议等。
2. API易用性。
3. 性能。是否高效，如支持连接池等。
4. 异步支持。每个通信客户端都想要的属性。
5. 持续更新。代码是否持续维护与更新。

基于以上标准，下面列举当前 Java 中所有流行的 HTTPClient 实现并进行对比。在此之前，需要一个 HTTP Server 的实现做测试准备，如下是一个基于 Jetty 构建的 HTTP server。

```java
   @Test
   public void initJettyServer() throws Exception {

       Server server = new Server(8000);

       // 1. ServletContextHandler
       ServletContextHandler handler = new ServletContextHandler();

       // 2. ServletHolder -> HttpServlet
       // add HttpServlet to contextHandler
       handler.addServlet(new ServletHolder(new HttpServlet() {
           @Override
           protected void doPost(HttpServletRequest req, HttpServletResponse response) throws ServletException, IOException {


               logger.info("http method:{}", req.getMethod());
               logger.info("header:{}", req.getHeader("ID"));
               logger.info("servletRequest:{}", IOUtils.toString(req.getReader()));


               response.setStatus(HttpServletResponse.SC_OK);
               response.setContentType("text/plain; charset=UTF-8");
               response.setHeader("ID", "JettyServer");
               response.setCharacterEncoding(StandardCharsets.UTF_8.name());
               if ("GET".equals(req.getMethod())) {

                   response.getWriter().write("GET");
               } else {
                   response.getWriter().write("POST");
               }
               response.getWriter().flush();
           }

       }), "/httpclient");


       server.setHandler(handler);
       server.start();

       server.join();
   }
```

# 1 HttpUrlConnection

如果希望尽可能少的依赖三方包，那么 HttpUrlConnection 是可选项。

```java
   @Test
   public void testHttpUrlConnectionPost() throws Exception {

       URL url = new URL("http://0.0.0.0:8000/httpclient");
       HttpURLConnection connection = (HttpURLConnection) url.openConnection();

       connection.setConnectTimeout(1000);
       connection.setReadTimeout(1000);

       connection.setDoOutput(true);
       connection.setDoInput(true);
       connection.setUseCaches(false);
       connection.setRequestMethod("POST");
       // header
       connection.setRequestProperty("ID", "URLConnection");
       connection.connect();

       try (OutputStream outputStream = connection.getOutputStream()) {
           outputStream.write("body".getBytes(StandardCharsets.UTF_8));
           outputStream.flush();
       }

       int code = connection.getResponseCode();
       logger.info("Code:{}", code);
       if (code == 200) {
           try (InputStream inputStream = connection.getInputStream()) {
               logger.info("{}", IOUtils.toString(inputStream, StandardCharsets.UTF_8));
           }
       } else {
           try (InputStream inputStream = connection.getErrorStream()) {
               logger.info("{}", IOUtils.toString(inputStream, StandardCharsets.UTF_8));
           }

       }

       connection.disconnect();
   }
```

## 1.1 评价

1. 协议支持 - 低
2. API易用性 - 低
3. 性能 - 低
4. 异步支持 - 否
5. 持续更新 - 否

# 2. Apache HttpComponents HttpClient

> Although the java.net package provides basic functionality for accessing resources via HTTP, it doesn't provide the full flexibility or functionality needed by many applications. HttpClient seeks to fill this void by providing an efficient, up-to-date, and feature-rich package implementing the client side of the most recent HTTP standards and recommendations.

基本上是 Java 平台中事实上的标准 HTTP 客户端。支持的特性可见： [https://hc.apache.org/httpcomponents-client-ga/](提供的特性： https://hc.apache.org/httpcomponents-client-ga/)。

## 2.1 同步

```java
   @Test
   public void testHttpComponentClientSync() throws Exception {

       CloseableHttpClient client = HttpClients.createDefault();

       RequestConfig config = RequestConfig.custom()
               .setConnectTimeout(1000)
               .setSocketTimeout(1000)
               .setConnectionRequestTimeout(1000)
               .build();


       HttpPost post = new HttpPost("http://0.0.0.0:8000/httpclient");
       post.setConfig(config);
       post.addHeader("ID", "HttpComponent");

       HttpEntity entity = new StringEntity("body", StandardCharsets.UTF_8);
       post.setEntity(entity);

       client.execute(post, new ResponseHandler<String>() {
           @Override
           public String handleResponse(HttpResponse response) throws ClientProtocolException, IOException {

               logger.info("header:{}", response.getAllHeaders());
               String body = EntityUtils.toString(response.getEntity(),
                       StandardCharsets.UTF_8);
               logger.info("body:{}", body);
               return body;
           }
       });
```

## 2.2 异步

```java
   @Test
   public void testHttpComponentClientASync() throws Exception {

       CloseableHttpAsyncClient asyncClient = HttpAsyncClients.createDefault();
       asyncClient.start();

       RequestConfig config = RequestConfig.custom()
               .setConnectTimeout(1000)
               .setSocketTimeout(1000)
               .setConnectionRequestTimeout(1000)
               .build();

       HttpPost post = new HttpPost("http://0.0.0.0:8000/httpclient");
       post.setConfig(config);
       post.addHeader("ID", "HttpComponent");

       HttpEntity entity = new StringEntity("body", StandardCharsets.UTF_8);
       post.setEntity(entity);

       CompletableFuture<String> bodyFuture = new CompletableFuture();
       asyncClient.execute(post, new FutureCallback<HttpResponse>() {
           @Override
           public void completed(HttpResponse httpResponse) {

               logger.info("[completed] header:{}", httpResponse.getAllHeaders());

               String body = null;
               try {
                   body = EntityUtils.toString(httpResponse.getEntity(),
                           StandardCharsets.UTF_8);
                   bodyFuture.complete(body);
               } catch (Exception e) {

                   bodyFuture.complete(null);
               }

               logger.info("[completed] futureCallBack suc...");
           }

           @Override
           public void failed(Exception e) {

           }

           @Override
           public void cancelled() {

           }
       });

       logger.info("body:{}", bodyFuture.get());

   }
```

其它关于异步的实现可见：[http://hc.apache.org/httpcomponents-asyncclient-dev/index.html](http://hc.apache.org/httpcomponents-asyncclient-dev/index.html)

## 2.3 评价

1. 协议支持 - 高
2. API易用性 - 中
3. 性能 - 高
4. 异步支持 - 是
5. 持续更新 - 是


# 3 OkHTTP

> An HTTP & HTTP/2 client for Android and Java applications.

OkHttp 对自己描述是 `efficient HTTP client`

OkHttp 提供了对最新的 HTTP 协议版本 HTTP/2 和 SPDY 的支持，这使得对同一个主机发出的所有请求都可以共享相同的套接字连接。如果 HTTP/2 和 SPDY 不可用，OkHttp 会使用连接池来复用连接以提高效率。OkHttp 提供了对 GZIP 的默认支持来降低传输内容的大小。OkHttp 也提供了对 HTTP 响应的缓存机制，可以避免不必要的网络请求。当网络出现问题时，OkHttp 会自动重试一个主机的多个 IP 地址。

具体资料可参考：

* https://square.github.io/okhttp/
* https://github.com/square/okhttp/wiki

## 3.1 同步

```java
   @Test
   public void testOKHTTPPostSync() throws Exception {

       OkHttpClient okHttpClient = new OkHttpClient.Builder()
               .connectTimeout(1000, TimeUnit.MILLISECONDS)
               .readTimeout(1000, TimeUnit.MILLISECONDS)
               .build();

       RequestBody body = RequestBody.create(MediaType.get("text/plain; charset=utf-8"), "body");
       Request request = new Request.Builder()
               .url("http://0.0.0.0:8000/httpclient")
               .header("ID", "OKHttp")
               .post(body)
               .build();
       try (Response response = okHttpClient.newCall(request).execute()) {
           logger.info("{}", response.body().string());
       }


   }
```

## 3.2 异步

```java
   /**
    * https://github.com/square/okhttp/wiki/Recipes
    */
   @Test
   public void testOKHTTPPostAsync() throws Exception {

       OkHttpClient okHttpClient = new OkHttpClient.Builder()
               .connectTimeout(1000, TimeUnit.MILLISECONDS)
               .readTimeout(1000, TimeUnit.MILLISECONDS)
               .build();

       RequestBody body = RequestBody.create(MediaType.get("text/plain; charset=utf-8"), "body");
       Request request = new Request.Builder()
               .url("http://0.0.0.0:8000/httpclient")
               .header("ID", "OKHttp")
               .post(body)
               .build();


       CountDownLatch countDownLatch = new CountDownLatch(1);
       okHttpClient.newCall(request).enqueue(new Callback() {
           @Override
           public void onFailure(Call call, IOException e) {
               logger.info("失败！！");
           }

           @Override
           public void onResponse(Call call, Response response) throws IOException {

               try (ResponseBody responseBody = response.body()) {

                   Headers headers = response.headers();
                   logger.info("headers:{}", headers);
                   logger.info("body:{}", responseBody.string());

                   countDownLatch.countDown();
               }
           }
       });


       // wait
       countDownLatch.await();
   }
```

## 3.3 评价

1. 协议支持 - 高
2. API易用性 - 高
3. 性能 - 高
4. 异步支持 - 是
5. 持续更新 - 是

# 4 Spring RestTemplate

Spring 提供的一个简单的模板封装实现。

> Synchronous client to perform HTTP requests, exposing a simple, template method API over underlying HTTP client libraries such as the JDK HttpURLConnection, Apache HttpComponents, and others. The RestTemplate offers templates for common scenarios by HTTP method, in addition to the generalized exchange and execute methods that support of less frequent cases.

[https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/client/RestTemplate.html](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/client/RestTemplate.html)

```java
   @Test
   public void testSpringRestTemplate() throws Exception {

       RestTemplate restTemplate = new RestTemplateBuilder()
               .setConnectTimeout(1000)
               .setReadTimeout(1000)
               .build();

       HttpHeaders header = new HttpHeaders();
       header.add("ID", "SpringRestTemplate");
       header.add(HttpHeaders.ACCEPT_CHARSET, StandardCharsets.UTF_8.name());
       header.add(HttpHeaders.CONTENT_TYPE, "text/plain; charset=utf-8");

       org.springframework.http.HttpEntity<String> entity =
               new org.springframework.http.HttpEntity<String>("body", header);
       ResponseEntity<String> responseEntity = restTemplate.postForEntity("http://0.0.0.0:8000/httpclient",
               entity, String.class);
       logger.info("result:{}", responseEntity.getBody());
   }
```

## 4.1 评价

1. 协议支持 - 高
2. API易用性 - 高
3. 性能 - 中
4. 异步支持 - 否
5. 持续更新 - 否（Spring 已推荐其它实现）

# 5 Unirest

> Lightweight HTTP Request Client Libraries  （API）

Unirest 是基于 HttpClient 的封装(其对HttpClient 的使用代码可做参考借鉴)，意在提供更好的 API。

[http://unirest.io/](http://unirest.io/)

```java
   @Test
   public void testUnirest() throws Exception {

       com.mashape.unirest.http.HttpResponse<String> response =
               Unirest.post("http://0.0.0.0:8000/httpclient")
                       .header("ID", "Unirest")
                       .body("body".getBytes(StandardCharsets.UTF_8))
                       .asString();

       logger.info("result:{}", response.getBody());
   }
```


## 5.1 评价

1. 协议支持 - 高
2. API易用性 - 高
3. 性能 - 高
4. 异步支持 - 是
5. 持续更新 - 否

# 6 Feign & Retrofit

二者思路一致，通过将 HttpClient 和 类 Mthod 结合方式（调用时直接调用实例方法就可以实现 HTTP 调用），提供更好 API，并且 Type-Safe.

## 6.1 Feign

> Feign is a Java to HTTP client binder inspired by Retrofit, JAXRS-2.0, and WebSocket. Feign's first goal was reducing the complexity of binding Denominator uniformly to HTTP APIs regardless of ReSTfulness.

意在：
> Feign makes writing java http clients easier.

[https://github.com/OpenFeign/feign](https://github.com/OpenFeign/feign)

```java
   interface FeignClient {

       @RequestLine("POST /httpclient")
       @feign.Headers({
               "ID: feign",
               "Content-Type: text/plain; charset=UTF-8"
       })
       String httpClient(String body);

   }

   @Test
   public void testFeign() throws Exception {

       FeignClient client = Feign.builder()
               .target(FeignClient.class, "http://0.0.0.0:8000");

       String result = client.httpClient("body");
       logger.info("result:{}", result);

   }
```

## 6.2 Rtrofit

> Type-safe HTTP client for Android and Java by Square, Inc

可见：
* [https://github.com/square/retrofit](https://github.com/square/retrofit)
* [https://square.github.io/retrofit/](https://square.github.io/retrofit/)

```java
   interface RetrofitClient {

       @POST("/httpclient")
       @retrofit2.http.Headers({
               "ID: retrofit",
               "Content-Type: text/plain; charset=UTF-8"
       })
       retrofit2.Call<String> httpClient(@Body String body);
   }

   @Test
   public void testRetrofit() throws Exception {

       Retrofit retrofit =
               new Retrofit.Builder()
                       .baseUrl("http://0.0.0.0:8000")
                       .addConverterFactory(ScalarsConverterFactory.create())
                       .build();

       RetrofitClient client = retrofit.create(RetrofitClient.class);
       retrofit2.Call<String> result = client.httpClient("body");
       logger.info("result:{}", result.execute().body());

   }
```

# 7 结论

选择时可以参考上面的几个标准。当然更高的封装也可能意味着失去了更好的灵活性，以及对底层的了解机会。如果不需要通过代码展现对新事物兴趣与热情，可以选择 HttpClient 与 OkHttp。