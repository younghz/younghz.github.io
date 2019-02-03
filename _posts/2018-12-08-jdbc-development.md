---
layout: post
title: "Java data access tools development"
---

* 目录
{:toc}

与缓存不同，数据库存储的数据通常是 schema 化的，这就意味着 DB Object 需要 Maping 为 Java 应用中 Object 才能使用，在获取 Object 之前，Java 查询方法也需要 mapping 为数据库查询语言 SQL。ORM 框架的功能就是将上面两步操作自动化、简便化。

Java 应用数据获取工具从最原始的 JDBC 到 ORM 框架，在到建立在二者之上的读写分离、分库分表中间件发展路径，当前成熟的方案通常是如下链路的封装。

<p style="text-align:center">
<img src="../resource/jdbc_development/data_acess.jpg"  width="270"/>
</p>


每一个节点都在解决不同的问题，如数据连接管理、冗余模板代码、数据映射、多数据库节点的读写分离等问题。下面就从浅入深谈谈不同阶段的问题与解决方案。



# 1. JDBC(Java Database Connectivity)

```java
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>x.x.x</version>
</dependency>
```

概念点：

* Connection。与DB之间的连接对象。
* Statement。执行查询等操作的对象。

```java
public class MySQLDemo {
 
    // JDBC 驱动名及数据库 URL
    static final String JDBC_DRIVER = "com.mysql.jdbc.Driver";  
    static final String DB_URL = "jdbc:mysql://localhost:3306/RUNOOB";
 
    // 数据库的用户名与密码，需要根据自己的设置
    static final String USER = "root";
    static final String PASS = "123456";
 
    public static void main(String[] args) {
        Connection conn = null;
        Statement stmt = null;
        try{
            // 注册 JDBC 驱动
            Class.forName("com.mysql.jdbc.Driver");
        
            // 打开链接
            System.out.println("连接数据库...");
            conn = DriverManager.getConnection(DB_URL,USER,PASS);
        
            // 执行查询
            System.out.println(" 实例化Statement对象...");
            stmt = conn.createStatement();
            String sql;
            sql = "SELECT id, name, url FROM websites";
            ResultSet rs = stmt.executeQuery(sql);
        
            // 展开结果集数据库
            while(rs.next()){
                // 通过字段检索
                int id  = rs.getInt("id");
                String name = rs.getString("name");
                String url = rs.getString("url");
    
                // 输出数据
                System.out.print("ID: " + id);
                System.out.print(", 站点名称: " + name);
                System.out.print(", 站点 URL: " + url);
                System.out.print("\n");
            }
            // 完成后关闭
            rs.close();
            stmt.close();
            conn.close();
        }catch(SQLException se){
            // 处理 JDBC 错误
            se.printStackTrace();
        }catch(Exception e){
            // 处理 Class.forName 错误
            e.printStackTrace();
        }finally{
            // 关闭资源
            try{
                if(stmt!=null) stmt.close();
            }catch(SQLException se2){
            }// 什么都不做
            try{
                if(conn!=null) conn.close();
            }catch(SQLException se){
                se.printStackTrace();
            }
        }
        System.out.println("Goodbye!");
    }
}
```

问题：

1. 连接的问题。忘了关闭连接，并发过大，数据库服务端支持的连接数有限等等。
2. 模板代码的问题。过多模板代码，每个操作都要写重复代码。
3. 数据映射问题。需要每个字段遍历获取。

# 2. 连接池

解决连接的问题。思路：连接池化。

池化的思路是为了解决和数据库建立、销毁连接的性能损耗，数据库本身的连接数限制等等问题。

# 3. Spring JdbcTemplate

解决模板代码的问题。思路：Template 化。

JdbcTemplate包含：

* DataSource 

```
String sql="select count(*) from table";
int count= jdbcTemplate.queryForObject(sql, Integer.class);
```

# 4. Mybatis

ORM 框架。

解决模板代码、数据映射的问题，提供更简便的 sql 操作 API。

```
<dependency>
  <groupId>org.mybatis</groupId>
  <artifactId>mybatis</artifactId>
  <version>x.x.x</version>
</dependency>
```

核心概念：

* SqlSession。Mybatis 对外暴露的执行 sql 的接口，与 Spring JdbcTemplate 一样，SqlSession 同样封装了大量模板代码。不需要使用者关心连接等问题。
* SqlSessionFactory。SqlSession 工厂。

在配置 SqlSessionFactory 时需指定 xml 映射文件，在使用时可以获取对应 Mapper class 来操作。此时数据库操作变为如下步骤。

```java
SqlSession session = sqlSessionFactory.openSession();
try {
  BlogMapper mapper = session.getMapper(BlogMapper.class);
  Blog blog = mapper.selectBlog(101);
} finally {
  session.close();
}
```

问题：

1. 需要自己写一层 DAO 来封装 Mapper 操作。
2. 需要在 DAO 中手动获取 Session，并且 close session 等模板操作。

# 5. Mybatis Spring

解决上述 MyBatis 问题，更方便在 Spring 中使用。

```xml
<dependency>
  <groupId>org.mybatis</groupId>
  <artifactId>mybatis-spring</artifactId>
  <version>x.x.x</version>
</dependency>
```

在 Spring 中更方便使用 MyBatis。实现了：

* 隐藏 Session使用与注入，可以直接通过 Spring Bean 方式注入 mapper 并直接使用其执行映射操作。
* 统一为 Spring 事务管理器。
* 异常统一为 Spring 封装异常。

配置基本与 MyBatis 配置一样：

1. 使用 xml 和 datasource 配置 SqlSessionFactory。
2. 使用 mapper class 路径配置 MapperScannerConfigurer，将 mapper class 实例为包含 sqlSessionFactory 的 mapper bean.
3. 使用 datasource 配置 transactionManager。

此时，可以直接注入 mapper 操作数据库。

```java
@Service
public class FooServiceImpl implements FooService {

  @Autowire
  private UserMapper userMapper;

  public void setUserMapper(UserMapper userMapper) {
    this.userMapper = userMapper;
  }

  public User doSomeBusinessStuff(String userId) {
    return this.userMapper.getUser(userId);
  }
}
```

# 6. 更上层的支持 读写分离、分库分表的组件

如当当的 sharding-jdbc，点评的 zebra 等。这里不详细对比。

__总结__

每个工具都在用自己的概念但是通用的思路解决不同的问题。了解概念才能更好的使用工具，熟悉思路与实现可以帮助扩展甚至编写自己的工具。