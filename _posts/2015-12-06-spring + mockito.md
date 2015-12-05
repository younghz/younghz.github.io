--- 
layout: post 
title: "spring + mockito" 
tagline: "注入bean的mock" 
description: "" 
category: java 
tags: [java] 
--- 
{% include JB/setup %}


```java

import static org.mockito.Mockito.*;

public class ServiceTest extends AbstractJunitTest{


    @Autowired
        private InvokeService invokeService;

    @Autowired
        private ToBeMockService toBeMockService;     // 1.注入正常，并且要注入要mock的bean

    @Before
        public void mockBefore() throws Exception {
            toBeMockService = mock(ToBeMockService.class);    //2.mock bean

            MockResult mockResult = new MockResult();
            mockResult.setxxx();

            // 3. when - then 
            when(toBeMockService.invoke(any(Param.class))).thenReturn(mockResult);  

            // 4. 替换注入的bean
            Object object = AopTargetUtils.getTarget(invokeService);
            FieldUtils.writeField(object, “toBeMockService”,toBeMockService, true);
        }

    @After
        public void after() throws Exception {
        }


    @Test
        public void testInvoke() throws Exception {

            // 调用，在这个方法中会调用mock的bean
            invokeService.invoke(orderModel);
        }


}

````
