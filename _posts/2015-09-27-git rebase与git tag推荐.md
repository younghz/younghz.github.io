---
layout: post
title: "【Git】git commit msg 最佳实践"
---

# 1 git commit 要求

## 1.1 git commit message要求

```
// 1. 每次提交把你的特性描述出来，如：
git commit -m “[需求名]功能点”

//2. 如果这个需求修改很多文件的话，就像被建议的，也为了不被review的人骂，就一个功能点一个功能点的提
git commit -m “[盖房子]打地基”
git commit -m “[盖房子]装修”
git commit -m “[盖房子]娶老婆”

//3. 如果你把你的task号也粘在了你的commit 信息里，bigger就又高了一级，git和task系统会自动链接过去
git commit -m “[盖房子]打地基  task”

//4 一定记得，为了让你的commit尽可能的挨在一起，一定要做rebase

```

## 1.2统计特性的人

```
//其中<commit old id>和<commit new id> 是你想要统计的所有commit的首和尾id。
git log --pretty=format:’%d %s  %cn’ <commit old id>..<commit new id> | grep “\[“ | awk -F’[‘ ‘{print $2}’ | sort | uniq
```
这样就能打印所有提交和提交人，去重的话在Uniq以下

## 1.3为什么要这样做

### 1.3.1 好统计

我们在切release时候每次都会统计这次的上线特性，这事我们搞个wiki来做的。
但是首先，面对乱七八糟的commit 信息为”update”/”update by xxx” 这样的提交，统计者根本看不出什么特性。
其次，人为的统计经常会被忘掉，这样，提测时候少测试了你这个特性，然后无bug算你牛，有bug只能算你背了。

### 1.3.2 出了问题好剔除
直接git rebase <the oldest commit id> -i
然后把不需要的commit直接删除掉，删除那行就ok。

# 2 git tag

## 2.1 简述
tag一般都打在生产分支上，我们的话就是master，为什么打在生产分支，因为需要所有需要上线的commit这时候才是最全的，develop切release时候可能不是，有可能release测出问题还会改，我是这么认为的，就是tag一般最后完事做总结用的。

## 2.2 使用
tag比较简单，就那几个命令，可以看这个https://git-scm.com/book/zh/v1/Git-%E5%9F%BA%E7%A1%80-%E6%89%93%E6%A0%87%E7%AD%BE

如果想看两个tag之间所有commit 的话，可以`git tag <old tag>..<new tag>`就可以。

当然，这个亦可以通过git log  --pretty=oneline <commit old id>..<commit new id>来看。
