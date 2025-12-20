# 十分钟学会正确的github工作流，和开源作者们使用同一套流程

**<font color='blue'>开源项目的背后，都有一套严谨的工作流程！</font>**

你是不是经常看到大佬们在GitHub上优雅地协作？

而你却总是搞不清楚什么时候该pull，什么时候该push？

别担心！今天我用最接地气的方式，教你十分钟学会专业的GitHub工作流！

## 为什么要学习GitHub工作流？

**<font color='red'>因为这是全球开发者的通用语言！</font>**

不管你是想参与开源项目，还是和团队协作开发。

掌握正确的GitHub工作流，就等于拿到了全球开发圈的「通行证」。

没有规范的流程，代码乱得像一锅粥！

有了规范的流程，团队配合默契，效率暴增！

## 基础概念先搞清

**<font color='green'>先理解这几个核心概念，后面就不懵了！</font>**

**仓库(Repository)**：就是你的项目文件夹，包含所有代码和历史记录。

**分支(Branch)**：代码的平行宇宙，可以在不影响主线的情况下开发新功能。

**主分支(main/master)**：最稳定、可发布的代码版本，绝对不能直接在上面改！

**提交(Commit)**：保存当前的代码变更，就像游戏的存档点。

**拉取请求(Pull Request)**：告诉其他人「我改好了，来看看吧」的申请。

**合并(Merge)**：把一个分支的改动融合到另一个分支中。

**冲突(Conflict)**：当两人改了同一处代码，Git不知道该听谁的。

## GitHub Flow：最流行的工作流

**<font color='purple'>这是GitHub官方推荐的工作流，简单实用！</font>**

### 1. 创建分支

**永远不要直接在main分支上开发！**

```bash
# 确保你在最新的main分支上
git checkout main
git pull origin main

# 创建并切换到新分支
git checkout -b feature/awesome-feature
```

**<font color='orange'>分支命名有讲究：</font>** feature/xxx（新功能）、bugfix/xxx（修复bug）、docs/xxx（文档更新）。

### 2. 开发并提交

在你的分支上尽情发挥，完成后提交：

```bash
# 查看改动了哪些文件
git status

# 添加改动的文件
git add .

# 提交改动
git commit -m "feat: 添加了登录功能"
```

**<font color='red'>提交信息也有规范！</font>** 常用前缀：feat（新功能）、fix（修复）、docs（文档）、style（格式）、refactor（重构）、test（测试）、chore（杂项）。

### 3. 推送分支

把你的分支推送到远程仓库：

```bash
git push origin feature/awesome-feature
```

### 4. 创建Pull Request

在GitHub网页上操作：

1. 点击「Compare & pull request」按钮
2. 填写PR标题和描述（说清楚你做了什么）
3. 点击「Create pull request」

**<font color='blue'>好的PR描述应该包含：</font>** 实现了什么功能、解决了什么问题、有什么注意事项。

### 5. 代码审查

等待团队成员审查你的代码，并根据反馈进行修改。

如果需要修改，直接在你的分支上继续提交，PR会自动更新。

### 6. 合并PR

代码审查通过后，点击「Merge pull request」按钮，选择合并方式：

- **Create a merge commit**：保留所有提交历史
- **Squash and merge**：将所有提交压缩成一个（推荐）
- **Rebase and merge**：重放所有提交，保持线性历史

### 7. 删除分支

合并完成后，删除已经没用的分支：

```bash
# 删除本地分支
git checkout main
git branch -d feature/awesome-feature

# 删除远程分支
git push origin --delete feature/awesome-feature
```

## 实用技巧：解决常见问题

### 解决冲突

当出现冲突时，不要慌：

```bash
# 拉取最新的main分支
git checkout main
git pull origin main

# 切回你的分支并合并main
git checkout feature/awesome-feature
git merge main
```

这时会提示冲突，打开冲突文件，你会看到：

```
<<<<<<< HEAD
你的代码
=======
别人的代码
>>>>>>> main
```

修改文件，保留正确的代码，删除冲突标记，然后：

```bash
git add .
git commit -m "fix: 解决冲突"
git push origin feature/awesome-feature
```

### 撤销最近的提交

写错了？没关系：

```bash
# 撤销最近一次提交，但保留更改
git reset --soft HEAD~1

# 彻底丢弃最近一次提交
git reset --hard HEAD~1
```

**<font color='red'>注意：</font>** 使用`--hard`会永久丢失更改，慎用！

### 暂存当前工作

需要临时切换分支，但当前工作还没完成？

```bash
# 暂存当前工作
git stash

# 切换分支，做其他事情
git checkout other-branch

# 切回来，恢复暂存的工作
git checkout feature/awesome-feature
git stash pop
```

## 进阶：Git Flow工作流

**<font color='purple'>适合更复杂的项目，有固定的发布周期。</font>**

这种工作流使用两个长期分支：

- **main/master**：只存放稳定、已发布的代码
- **develop**：开发分支，包含最新的开发代码

还有三种临时分支：

- **feature/**：新功能分支，从develop创建，完成后合并回develop
- **release/**：发布分支，从develop创建，用于准备发布
- **hotfix/**：热修复分支，从main创建，修复生产环境的紧急bug

## 实用命令速查表

**<font color='green'>收藏这个表，日常操作不用愁！</font>**

```bash
# 克隆仓库
git clone https://github.com/username/repo.git

# 创建并切换分支
git checkout -b branch-name

# 查看所有分支
git branch -a

# 拉取最新代码
git pull origin branch-name

# 推送到远程
git push origin branch-name

# 查看提交历史
git log --oneline --graph

# 合并分支
git merge branch-name

# 变基（让提交历史更干净）
git rebase branch-name
```

## 总结

**<font color='blue'>掌握GitHub工作流，你就能：</font>**

高效协作，不再踩队友的脚。

代码历史清晰，随时可以回溯。

轻松参与开源项目，展示你的才华。

提高代码质量，因为每次改动都会被审查。

**记住核心步骤：** 创建分支 → 开发提交 → 推送分支 → 创建PR → 代码审查 → 合并 → 删除分支。

这套流程看似复杂，但一旦熟悉，你会发现它让团队协作变得无比顺畅！

**<font color='red'>赶紧动手试试吧！</font>** 十分钟入门，受益一辈子！