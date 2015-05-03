  ---
  layout: post
  title: "2015-5-3-和而不同，git rebase 和 git merge.md"
  tagline: ""
  description: ""
  category: skill
  tags: [mt]
  ---
  {% include JB/setup %}


> You ask me a question, I tell you a story.    
                                                            — from null
                                                            
这里也讲一下自己的理解。

> 本文所述主分支指Master或者develop分支，新分支指feature-*或者bugfix-*分支。
 
# 原理

+ 注意rebase这个词，git上将其翻译为“定基”。这就是git rebase的作用，原来我checkout出来的基（base）是commit1，但是在我合并时我可以将我的base定到更新的commit上，反应到log上就是不会使主分支出现过多的分岔。
+ 当你使用merge合并分支时，实际是又在 上做了一个commit。但是使用rebase就不会出现额外的commit。而这点你可以看log graph。
+ Fast-Forward。使用rebase处理新分支在合并到主分支上是Fast-Forward的，但是直接合并是non Fast-Forward。
 
## 二者的同
**相同点显而易见，都是用作分支的合并。**    

## 二者的不同
下面是操作的步骤，从最后的结果可以看出不同点。

### 1，首先进行一些基本操作
> //新建文件夹并git初始化    
mkdir test    
cd test    
git init    

### 2，在分支master上新建分支nb1和nb2，并且每个分支上做了两个commit。

> 此时二者是同时从master分支上checkout出来的，所以二者的base是一致的。

![prepare job.png](https://github.com/younghz/ResourceForBlog/blob/master/git_rebase_and_git_merge/prepare%20job.png)

**这时nb1和nb2的log graph形状都是这样的：**

 
> 接下来我是要把分支nb1和nb2的改动都合并到master分支上。

###3，首先我把nb1先合并到master分支上.使用git merge.
**合并完成后的log graph:**    
![nb1 log](https://github.com/younghz/ResourceForBlog/blob/master/git_rebase_and_git_merge/nb1%20lg.png)
 

>下面的操作就可以看出不同了。

###4，使用rebase的效果。
首先，我先rebase master，这也是我们酒店代码提交所要求的。

>//在nb2分支上做的操作    
git rebase master
 
> //切换到master分支合并    
git checkout master    
git merge nb2    

**这时得到的log graph 是这样的：**    
![master log](https://github.com/younghz/ResourceForBlog/blob/master/git_rebase_and_git_merge/master%20nb2%20rebase.png)
 
###5, 使用merge
这里，在nb2分支上不rebase，直接切换到master分支上合并。

>git checkout master
git merge nb2

**效果图是这样的：**    
![rebase](https://github.com/younghz/ResourceForBlog/blob/master/git_rebase_and_git_merge/merge(non-fastfoward).png)
 
### 6，不同点清自行对比上两幅图

# 其他
**有人说为什么不在主分支做rebase?而且所有合并代码的工具默认使用的都是merge操作？**
 
大部分情况下在主分支上做合并操作的和新分支开发的根本就不是一个人，所以合并操作的人根本不熟悉你的分支，那么他根本就不应该重新定义你所做的改动的base。他若改了，你定会心里说上无数遍：     
**不熟悉老子代码还要乱改老子commit的base，你你你你。。。。**