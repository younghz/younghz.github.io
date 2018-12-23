---
layout: post
title: "【T】SpringApplication核心流程与扩展"
---

<p style="text-align:center">
<img src="../resource/springapplication_core_process/wj.jpg"  width="700"/>
</p>

* 目录
{:toc}

`SpringApplication` 启动类

```
public ConfigurableApplicationContext run(String... args) {
	StopWatch stopWatch = new StopWatch();
	stopWatch.start();
	ConfigurableApplicationContext context = null;
	Collection<SpringBootExceptionReporter> exceptionReporters = new ArrayList<>();
	configureHeadlessProperty();
	
	// 0：SpringBoot 启动生命周期 listener
	SpringApplicationRunListeners listeners = getRunListeners(args);
	listeners.starting();
	try {
		ApplicationArguments applicationArguments = new DefaultApplicationArguments(
				args);
				
		// Step 1: prepareEnvironment
		ConfigurableEnvironment environment = prepareEnvironment(listeners,
				applicationArguments);
		configureIgnoreBeanInfo(environment);
		Banner printedBanner = printBanner(environment);
		
		// Step 2：prepareApplicationContext
		context = createApplicationContext();
		exceptionReporters = getSpringFactoriesInstances(
				SpringBootExceptionReporter.class,
				new Class[] { ConfigurableApplicationContext.class }, context);
				
	    // Step 3: loadContext 
		prepareContext(context, environment, listeners, applicationArguments,
				printedBanner);
				
		// Step 4：refreshApplicationContext
		refreshContext(context);
		afterRefresh(context, applicationArguments);
		stopWatch.stop();
		if (this.logStartupInfo) {
			new StartupInfoLogger(this.mainApplicationClass)
					.logStarted(getApplicationLog(), stopWatch);
		}
		listeners.started(context);
		callRunners(context, applicationArguments);
	}
	catch (Throwable ex) {
		handleRunFailure(context, ex, exceptionReporters, listeners);
		throw new IllegalStateException(ex);
	}

	try {
		listeners.running(context);
	}
	catch (Throwable ex) {
		handleRunFailure(context, ex, exceptionReporters, null);
		throw new IllegalStateException(ex);
	}
	return context;
}
```

# 0：SpringBoot 启动生命周期 listener

SpringApplicationRunListener 为 SpringApplication 启动监听 listener，其实现配置在 spring.factories 文件中，通过`SpringFactoriesLoader`
加载，核心生命周期包含：environmentPrepared、contextPrepared、contextLoaded、started 四个阶段。这四个阶段对应如上 SpringApplication
启动代码核心四个步骤：prepareEnvironment -> prepareApplicationContext -> loadContext -> refreshApplicationContext。

* environmentPrepared：创建了 Environment, 但是 ApplicationContext 还没有创建。
* contextPrepared：创建了 ApplicationContext，但是还没有 Load bean into ApplicationContext。
* contextLoaded：ApplicationContext 已经被 Loaded（装载），但是还没有 refresh。
* started：ApplicationContext refresh 完毕。


可以通过实例 SpringApplicationRunListener 实现启动监听并执行相应动作，如希望修改 ApplicationContext 的 classLoader，那么
可以实现 SpringApplicationRunListener  contextPrepared 方法，获取 ApplicationContext 并修改其 classLoader。

# Step 1: prepareEnvironment


核心代码：
```
private ConfigurableEnvironment getOrCreateEnvironment() {
	if (this.environment != null) {
		return this.environment;
	}
	switch (this.webApplicationType) {
	case SERVLET:
		return new StandardServletEnvironment();
	case REACTIVE:
		return new StandardReactiveWebEnvironment();
	default:
		return new StandardEnvironment();
	
}
```

Environment 的核心点是 properties 和 profiles。Environment 通过持有「有序的」PropertySource 对象 `List<PropertySource<?>> propertySourceList`
来表示其包含的属性块。以 StandardEnvironment 实现为例，其默认会添加两个属性块 SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME 和
SYSTEM_ENVIRONMENT_PROPERTY_SOURCE_NAME。

```
@Override
protected void customizePropertySources(MutablePropertySources propertySources) {
	propertySources.addLast(new MapPropertySource(SYSTEM_PROPERTIES_PROPERTY_SOURCE_NAME, getSystemProperties()));
	propertySources.addLast(new SystemEnvironmentPropertySource(SYSTEM_ENVIRONMENT_PROPERTY_SOURCE_NAME, getSystemEnvironment()));
}
```

当需要从 Environment 获取属性(property)时，会通过循环 `List<PropertySource<?>> propertySourceList` 属性块列表的方式查找属性，也就是说
List 中属性块的顺序决定了属性查找的优先级。这也是 Spring 控制资源优先级的方式。

# Step 2：prepareApplicationContext

和 Environment 一样，会根据应用类型实例不同的 ApplicationContext。

```
protected ConfigurableApplicationContext createApplicationContext() {
	Class<?> contextClass = this.applicationContextClass;
	if (contextClass == null) {
		try {
			switch (this.webApplicationType) {
			case SERVLET:
				contextClass = Class.forName(DEFAULT_SERVLET_WEB_CONTEXT_CLASS);
				break;
			case REACTIVE:
				contextClass = Class.forName(DEFAULT_REACTIVE_WEB_CONTEXT_CLASS);
				break;
			default:
				contextClass = Class.forName(DEFAULT_CONTEXT_CLASS);
			}
		}
		catch (ClassNotFoundException ex) {
			throw new IllegalStateException(
					"Unable create a default ApplicationContext, "
							+ "please specify an ApplicationContextClass",
					ex);
		}
	}
	return (ConfigurableApplicationContext) BeanUtils.instantiateClass(contextClass);
}
```

ApplicationContext 和 BeanFactory 的体系可以在IDE通过右键 `Diagrams` -> `show Diagram...` 查看。

# Step 3: loadContext 

```
private void prepareContext(ConfigurableApplicationContext context,
		ConfigurableEnvironment environment, SpringApplicationRunListeners listeners,
		ApplicationArguments applicationArguments, Banner printedBanner) {
	context.setEnvironment(environment);
	postProcessApplicationContext(context);
	applyInitializers(context);
	listeners.contextPrepared(context);
	if (this.logStartupInfo) {
		logStartupInfo(context.getParent() == null);
		logStartupProfileInfo(context);
	}
	// Add boot specific singleton beans
	ConfigurableListableBeanFactory beanFactory = context.getBeanFactory();
	beanFactory.registerSingleton("springApplicationArguments", applicationArguments);
	if (printedBanner != null) {
		beanFactory.registerSingleton("springBootBanner", printedBanner);
	}
	if (beanFactory instanceof DefaultListableBeanFactory) {
		((DefaultListableBeanFactory) beanFactory)
				.setAllowBeanDefinitionOverriding(this.allowBeanDefinitionOverriding);
	}
	// Load the sources
	Set<Object> sources = getAllSources();
	Assert.notEmpty(sources, "Sources must not be empty");
	load(context, sources.toArray(new Object[0]));
	listeners.contextLoaded(context);
}
```

核心 Load 代码如下：

```
protected void load(ApplicationContext context, Object[] sources) {
	if (logger.isDebugEnabled()) {
		logger.debug(
				"Loading source " + StringUtils.arrayToCommaDelimitedString(sources));
	}
	
	// 创建 loader
	BeanDefinitionLoader loader = createBeanDefinitionLoader(
			getBeanDefinitionRegistry(context), sources);
	if (this.beanNameGenerator != null) {
		loader.setBeanNameGenerator(this.beanNameGenerator);
	}
	if (this.resourceLoader != null) {
		loader.setResourceLoader(this.resourceLoader);
	}
	if (this.environment != null) {
		loader.setEnvironment(this.environment);
	}
	
	// 实际 load 
	loader.load();
}
```

此时 load 只通过BeanDefinitionLoader  AnnotatedBeanDefinitionReader 的 register 注册了启动方法，其它Spring Bean Class 是
通过 ConfigurationClassPostProcessor 中的 ConfigurationClassParser 扫描出，并在 ConfigurationClassPostProcessor 注册的。


# Step 4：refreshApplicationContext

核心的 SpringApplicationContext 的 refresh 流程是固定的、标准的，其核心代码在 AbstractApplicationContext 中，如下：

```
@Override
public void refresh() throws BeansException, IllegalStateException {
	synchronized (this.startupShutdownMonitor) {
		// Prepare this context for refreshing.
		prepareRefresh();

		// Tell the subclass to refresh the internal bean factory.
		ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();

		// Prepare the bean factory for use in this context.
		prepareBeanFactory(beanFactory);

		try {
			// Allows post-processing of the bean factory in context subclasses.
			postProcessBeanFactory(beanFactory);

			// Invoke factory processors registered as beans in the context.
			invokeBeanFactoryPostProcessors(beanFactory);

			// Register bean processors that intercept bean creation.
			registerBeanPostProcessors(beanFactory);

			// Initialize message source for this context.
			initMessageSource();

			// Initialize event multicaster for this context.
			initApplicationEventMulticaster();

			// Initialize other special beans in specific context subclasses.
			onRefresh();

			// Check for listener beans and register them.
			registerListeners();

			// Instantiate all remaining (non-lazy-init) singletons.
			finishBeanFactoryInitialization(beanFactory);

			// Last step: publish corresponding event.
			finishRefresh();
		}

		catch (BeansException ex) {
			if (logger.isWarnEnabled()) {
				logger.warn("Exception encountered during context initialization - " +
						"cancelling refresh attempt: " + ex);
			}

			// Destroy already created singletons to avoid dangling resources.
			destroyBeans();

			// Reset 'active' flag.
			cancelRefresh(ex);

			// Propagate exception to caller.
			throw ex;
		}

		finally {
			// Reset common introspection caches in Spring's core, since we
			// might not ever need metadata for singleton beans anymore...
			resetCommonCaches();
		}
	}
}
```
如上流程也说明了 Spring 全部种类 Bean 的加载顺序与生命周期。
其中如下两步为核心步骤，也是 spring 的核心两个扩展点，即 `BeanFactoryPostProcessor` 和 `BeanPostProcessor`。

```
	// Invoke factory processors registered as beans in the context.
	invokeBeanFactoryPostProcessors(beanFactory);

	// Register bean processors that intercept bean creation.
	registerBeanPostProcessors(beanFactory);
```

## 4.1 BeanDefinition、配置 扫描注册

#### 1. 执行顺序说明

PostProcessorRegistrationDelegate.invokeBeanFactoryPostProcessors 定义了所有 BeanFactoryPostProcessor 的调用顺序，基本
顺序是：

首先执行 BeanDefinitionRegistryPostProcessors 实现，顺序为：
* First, invoke the BeanDefinitionRegistryPostProcessors that implement PriorityOrdered.
* Next, invoke the BeanDefinitionRegistryPostProcessors that implement Ordered.
* Finally, invoke all other BeanDefinitionRegistryPostProcessors until no further ones appear.

其次执行 BeanFactoryPostProcessors 实现，顺序为：
* First, invoke the BeanFactoryPostProcessors that implement PriorityOrdered.
* Next, invoke the BeanFactoryPostProcessors that implement Ordered
* Finally, invoke all other BeanFactoryPostProcessors.

#### 2. Bean、配置 扫描注册

BeanDefinition 扫描注册依赖于处理器 ConfigurationClassPostProcessor，其实现了 BeanDefinitionRegistryPostProcessor 接口，并且
实现了 PriorityOrdered，且其优先级定义为最高，所以第一个被执行。

__a. ConfigurationClassPostProcessor 什么时候被注册？__

AnnotatedBeanDefinitionReader 在构造方法中存在如下调用：

```
AnnotationConfigUtils.registerAnnotationConfigProcessors(this.registry);
```
其中注册了 ConfigurationClassPostProcessor、CommonAnnotationBeanPostProcessor 等 PostProcessor 的 BeanDefinition。此时
ConfigurationClassPostProcessor 注册到 ApplicationContext 中。

__b. 怎么扫描注册的 BeanDefinition?__

ConfigurationClassPostProcessor 通过 ConfigurationClassParser 扫描所有 @Configuration 类，核心代码如下：

```
    // Step1: 新建 parser
	ConfigurationClassParser parser = new ConfigurationClassParser(
			this.metadataReaderFactory, this.problemReporter, this.environment,
			this.resourceLoader, this.componentScanBeanNameGenerator, registry);

	Set<BeanDefinitionHolder> candidates = new LinkedHashSet<>(configCandidates);
	Set<ConfigurationClass> alreadyParsed = new HashSet<>(configCandidates.size());
	do {

	    // Step2:扫描 Configuration(Spring Bean Class) class
		parser.parse(candidates);
		parser.validate();

		Set<ConfigurationClass> configClasses = new LinkedHashSet<>(parser.getConfigurationClasses());
		configClasses.removeAll(alreadyParsed);

		// Read the model and create bean definitions based on its content
		if (this.reader == null) {
			this.reader = new ConfigurationClassBeanDefinitionReader(
					registry, this.sourceExtractor, this.resourceLoader, this.environment,
					this.importBeanNameGenerator, parser.getImportRegistry());
		}

		// Step3: load BeanDefinition
		this.reader.loadBeanDefinitions(configClasses);
		alreadyParsed.addAll(configClasses);
```

ConfigurationClassParser 通过扫描读取类注解、成员方法等方式收集所有的 Spring 配置类，包含：

* @Component 注解类，并将其增加到 ToBeLoadClasses 中。
* @PropertySources 注解类，并将其增加到 Environment 中，其利用类 `ResourceLoader` 的 getResource 来加载资源。
* @ComponentScans 注解，并按照注解中的扫描路径、排除路径等内容扫描（由ComponentScanAnnotationParser扫描），并将扫描到的类增加到 ToBeLoadClasses 中。
* @Import 注解导入的类，实现 ImportSelector 的类，增加到 ToBeLoadClasses 中。
* @ImportResource 导入的类。
* @Bean 标记的。

核心内容有三：1. 类扫描，增加到待 load 列表中。2. 资源加载到 Environment 中。3. ResourceLoader。

__c. 配置的资源如 .properties 文件怎样、什么时候加载到 Environment ？__

见上方 PropertySources 代码分析。


## 4.2 BeanPostProcessor

4.1 以 ConfigurationClassPostProcessor 为例展示了所有 BeanFactoryPostProcessor 的加载、执行。 以及 ConfigurationClassPostProcessor 
作为 Spring 配置类处理器所做的 Spring Bean load 过程。

在 ApplicationContext refresh 中 BeanFactoryPostProcessor 处理后，就是 BeanPostProcessor 的处理，处理流程基本类似。

# 5. Spring 扩展点整理

扩展点：
* BeanFactoryPostProcessor：注册 Bean定义或者 custom modification of an application context's bean definitions。
* BeanDefinitionRegistryPostProcessor：registration of further bean definitions before regular BeanFactoryPostProcessor。
* BeanPostProcessor：对 Bean 实例进行修改，如 `checking for marker interfaces or wrapping them with proxies`。
* ImportBeanDefinitionRegistrar：用于注册额外的 Bean，由 ConfigurationClassParser 处理。
* 各种 Aware。

