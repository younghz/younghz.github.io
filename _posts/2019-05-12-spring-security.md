---
layout: post
title: "Web 安全之 Spring Security"
---

* 目录
{:toc}

# 1 spring security architecture

## 1.1 安全分类

Spring Security 将应用安全性分为：

* Authentication. 认证。
* Access Control. 访问控制。

两部分。

### 1.1.1 认证

认证核心接口是 ProviderManager(AuthenticationManager的实现)，其持有一系列的 AuthenticationProvider，
AuthenticationProvider 包含如下两个方法：

```
public interface AuthenticationProvider {

    // 具体认证操作
	Authentication authenticate(Authentication authentication)
			throws AuthenticationException;

    // 是否可以处理当前的认证
	boolean supports(Class<?> authentication);

}
```

具体的认证策略是：

1. 如果输入的 Authentication 认证成功，则返回Authentication（通常带有authenticated=true）。
2. 如果认证失败，则抛出 AuthenticationException。
3. 如果不能确定，则返回 null。


认证形式可以是：
* Form 表单登陆认证；Spring Security 还提供了如 OAuth/LDAP/OpenId 等新式的实现。
* Http Basic / Http Digest 认证；

配置形式如：

```
// ba 认证形式
//.httpBasic();
// login 形式
.formLogin()
```

### 1.1.2 访问控制

认证通过后，就需要看是否具有资源的访问权限。

访问控制和认证的组件类似，AccessDecisionManager 持有一系列的 AccessDecisionVoter，AccessDecisionVoter 负责认证。AccessDecisionVoter
包含：

```
boolean supports(ConfigAttribute attribute);

boolean supports(Class<?> clazz);

/**
 * authentication 代表 the caller making the invocation；
 * object 代表需要访问的资源；
 * attributes 代表角色集，如ROLE_ADMIN或ROLE_AUDIT；
 * 返回 ACCESS_GRANTED、ACCESS_ABSTAIN、ACCESS_DENIED
 */
int vote(Authentication authentication, S object,
        Collection<ConfigAttribute> attributes);
```

## 1.2 应用

受保护的资源可以是 web 资源，也可以是应用中的方法。

### 1.2.1 Web 安全

Spring security 在 web 层的实现是基于 Servlet 的 Filter，其实现是 `FilterChainProxy`，其架构如：

//todo 这里是个图 https://spring.io/guides/topicals/spring-security-architecture 图2 图3

可以通过 EnableWebSecurity 注解配置 Spring security, 这个注解通过配置 WebSecurityConfiguration 这个 configuration，
通过你自定义（无自定义，使用默认）的 WebSecurityConfigurerAdapter 实现构造 FilterChainProxy。

在 web 中使用 Spring Security 的步骤为：

1. 引入 EnableWebSecurity 注解。
2. 自定义配置 WebSecurityConfigurerAdapter。

当前应用 FilterChain 中包含的 Filter 可以在启动日志中找到，如：

> [           main] o.s.s.web.DefaultSecurityFilterChain     : Creating filter chain: org.springframework.security.web.util.matcher.AnyRequestMatcher@1,
 [org.springframework.security.web.context.request.async.WebAsyncManagerIntegrationFilter@7caf1e5,
 org.springframework.security.web.context.SecurityContextPersistenceFilter@2450256f,
 org.springframework.security.web.header.HeaderWriterFilter@63917fe1,
 org.springframework.security.web.csrf.CsrfFilter@25f0c5e7,
 org.springframework.security.web.authentication.logout.LogoutFilter@5ac044ef,
 org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter@63f9ddf9,
 org.springframework.security.web.authentication.ui.DefaultLoginPageGeneratingFilter@760f1081,
 org.springframework.security.web.savedrequest.RequestCacheAwareFilter@2b7facc7,
 org.springframework.security.web.servletapi.SecurityContextHolderAwareRequestFilter@4a1dda83,
 org.springframework.security.web.authentication.AnonymousAuthenticationFilter@5c234920,
 org.springframework.security.web.session.SessionManagementFilter@677349fb,
 org.springframework.security.web.access.ExceptionTranslationFilter@5e99e2cb,
 org.springframework.security.web.access.intercept.FilterSecurityInterceptor@1a88c4f5]

其中：

* SecurityContextPersistenceFilter 负责保存 SecurityContext，并与当前回话（session）绑定。如果当次请求没有 session id,那么新创建 SecurityContext
并保存，如果存在，直接获取当前的会话的 SecurityContext（包含当前用户信息）。
* LogoutFilter 负责登出操作，如清理 SecurityContext，清理 cookie 等。
* UsernamePasswordAuthenticationFilter 认证。上面 1.1.1 的实现。
* FilterSecurityInterceptor 访问控制。上面 1.1.2 的实现。
* DefaultLoginPageGeneratingFilter。生成 login 页面。
* ExceptionTranslationFilter。处理异常，如 访问控制失败，抛出 AccessDeniedException，此 filter 在获取到此异常后将请求重定向到 /login 页面。

### 1.2.2 方法安全

方法安全基于 spring aop 实现，具体处理逻辑可见 MethodSecurityInterceptor。
其从 SecurityContextHolder 获取当前上下文的 SecurityContext（由 SecurityContextPersistenceFilter 在请求到来时写入）。

在调用 Secured 注解声明方法前根据 SecurityContext 与 Secured 声明的 ROLE 信息尽心访问控制验证。

# 2 spring security in action

## 2.1 web 认证 & 访问控制

认证即登陆，将请求中的用户信息与服务端保存的用户信息比较。在 Spring Security 中，默认支持 In-Memory Authentication、JDBC Authentication
以及其它形式的用户信息存储位置。如下，是一个将用户信息存储在内存中的例子：

认证用户以及权限配置：
```
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.inMemoryAuthentication().passwordEncoder(NoOpPasswordEncoder.getInstance())
                .withUser(User.builder().username("h").password("h").roles("Father").build())
                .withUser(User.builder().username("y").password("y").roles("Son").build());
    }
```


认证路径与权限配置：
```
    @Override
    protected void configure(HttpSecurity http) throws Exception {

        http
                // 认证路径与匹配角色配置
                .authorizeRequests()
                .antMatchers("/my/**").permitAll()
                .antMatchers("/money/save").hasRole("Father")
                .antMatchers("/money/make").hasRole("Father")
                .antMatchers("/money/spend").hasRole("Son")
                .anyRequest().permitAll()

                .and()

                // login 配置
                .formLogin()
                .permitAll()

                // logout 配置
                .and()
                .logout()
                .logoutRequestMatcher(new AntPathRequestMatcher("/my/logout"))
                .logoutSuccessUrl("/login")
                .deleteCookies()
                .invalidateHttpSession(true)
                .permitAll();

    }
```

### 2.1.1 处理时序流

以访问 /money/save 为例：

1. 访问 /money/save。
2. FilterSecurityInterceptor 处理 /money/save 访问控制失败，抛出 AccessDeniedException。
3. ExceptionTranslationFilter 识别异常，将请求重定向到 /login。
4. UsernamePasswordAuthenticationFilter 处理 /login，使用用户名、密码信息认证。
5. FilterSecurityInterceptor 走 /login 访问控制逻辑，根据配置认证信息验证。
6. 验证成功，走到 /money/save controller。

### 2.1.2 设计思路与技术点

* Ability Manager + Ordered Abilities
* 密码 Encoder，默认包含了实现:
    * BCryptPasswordEncoder
    * Pbkdf2PasswordEncoder
    * SCryptPasswordEncoder



## 2.2 方法安全

配置：

```
@EnableGlobalMethodSecurity(securedEnabled = true)
public class MethodSecurityConfig {
// ...
}


public interface BankService {

@Secured("IS_AUTHENTICATED_ANONYMOUSLY")
public Account readAccount(Long id);

@Secured("IS_AUTHENTICATED_ANONYMOUSLY")
public Account[] findAccounts();

@Secured("ROLE_TELLER")
public Account post(Account account, double amount);
}
```

### 2.1.1 设计思路与技术点

* 基于代码的 AOP 实现。
* 跨线程传递信息实现。DelegatingSecurityContextTaskExecutor。

## 2.3 CSRF

Web 安全配置中默认集合了 CsrfFilter，用于对 POST/PUT 等请求进行 CsrfToken 验证。默认支持 Token 通过 Header 和
Cookie 进行传递。

## 2.4 CORS

对跨域的支持可以通过如下配置实现：

```
  @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            // by default uses a Bean by the name of corsConfigurationSource
            .cors().configurationSource()
            ...
    }

```

其实现在 CorsFilter 中。

# 3 总结

在 Spring 体系下，Spring Security 无疑是最合适的安全方案。当然，Web 安全还不止是这些。

Spring Securty 作为 Spring 核心组件之一，可供借鉴的除了其安全策略实现，还包含设计思路，实现模式，以及 Spring 体系下的一套开发模型。
