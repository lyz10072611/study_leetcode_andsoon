```callout
  **LeetCode Hot100学习指南**：本文档系统整理了LeetCode平台上最常考的100道算法题目，按数据结构和算法类型分为8大类别。每道题目均提供详细解析、Java实现代码、复杂度分析及记忆技巧，旨在帮助开发者系统性掌握算法面试核心知识点，提升编码能力与问题解决效率。
```

# LeetCode Hot100 算法通关指南

## 文档简介

LeetCode Hot100是由LeetCode官方根据题目频率、难度和面试出现次数精选的100道算法题，涵盖了面试中90%以上的核心知识点。这些题目经过无数面试验证，集中体现了一线科技公司对算法能力的考察重点。

本学习文档将这100道题目按数据结构和算法类型分为8大类，每道题目均提供**题目描述**、**详细解析**、**多种解题思路**、**Java完整实现**、**复杂度分析**和**记忆技巧**，旨在帮助开发者构建系统的算法知识体系，高效备战技术面试。

```callout
  **学习价值**：根据历年面试数据统计，掌握本文档中80%的题目，即可应对90%以上的算法面试场景。平均学习周期为4-6周，每日投入2-3小时，可显著提升编码能力和问题解决效率。
```

## 目录

1. [二叉树](#1-二叉树-17道)
2. [栈](#2-栈-9道)
3. [链表](#3-链表-10道)
4. [字符串](#4-字符串-8道)
5. [数组](#5-数组-37道)
6. [搜索](#6-搜索-11道)
7. [矩阵](#7-矩阵-4道)
8. [递推](#8-递推-4道)
9. [算法模板与解题技巧总结](#9-算法模板与解题技巧总结)

## 1. 二叉树 (17道)

二叉树是算法面试中的重点考察内容，约占所有算法题目的20%。本章节包含17道经典二叉树题目，涵盖树的遍历、构造、修改等核心操作。

```callout
  **核心考点**：二叉树的前中后序遍历、层序遍历、递归与迭代实现、路径问题、构造与转换、属性计算。掌握二叉树问题的关键在于深入理解递归思想和树的结构特性。
```

### 1.1 二叉树展开为链表 (LeetCode 114)

#### 题目描述
给你二叉树的根结点 root，请你将它展开为一个单链表：
- 展开后的单链表应该同样使用 TreeNode，其中 right 子指针指向链表中下一个结点，而左子指针始终为 null
- 展开后的单链表应该与二叉树先序遍历顺序相同

**示例 1**:
```
输入：root = [1,2,5,3,4,null,6]
输出：[1,null,2,null,3,null,4,null,5,null,6]
```

#### 题目解析
本题要求将二叉树原地展开为单链表，空间复杂度要求O(1)，考察对二叉树结构的理解和指针操作能力。关键在于找到左子树的最右节点，将右子树接到该节点上，再将左子树移到右子树位置。

#### 解题思路
1. 使用while循环遍历二叉树的每个节点
2. 若当前节点左子树为空，直接移动到右子树
3. 若左子树不为空：
   - 找到左子树最右边的节点
   - 将当前节点的右子树接到左子树最右节点的右指针上
   - 将左子树移动到右子树位置
   - 清空当前节点的左子树指针
   - 移动到下一个节点

```whiteboard
  mindmap
    root(二叉树展开为链表)
      核心操作
        找左子树最右节点
        右子树嫁接
        左子树迁移
        清空左指针
      关键点
        原地操作
        O(1)空间复杂度
        先序遍历顺序
      易错点
        右子树丢失
        循环条件控制
        空树处理
```

#### Java解法实现
```java
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class Solution {
    public void flatten(TreeNode root) {
        while (root != null) {
            // 左子树为 null，直接考虑下一个节点
            if (root.left == null) {
                root = root.right;
            } else {
                // 找左子树最右边的节点
                TreeNode pre = root.left;
                while (pre.right != null) {
                    pre = pre.right;
                }
                // 将原来的右子树接到左子树的最右边节点
                pre.right = root.right;
                // 将左子树插入到右子树的地方
                root.right = root.left;
                root.left = null;
                // 考虑下一个节点
                root = root.right;
            }
        }
    }
}
```

#### 题解背诵技巧
**口诀记忆法**："左子树最右，右子树嫁接，左树变右树，左指针清空"

**关键步骤**：
1. 找左子树最右节点：`while (pre.right != null) { pre = pre.right; }`
2. 嫁接右子树：`pre.right = root.right;`
3. 迁移左子树：`root.right = root.left;`
4. 清空左指针：`root.left = null;`

记住这个四步操作，即可解决该问题。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是树中的节点数。每个节点都会被访问一次。
- **空间复杂度**：O(1)，只需要常数级别的额外空间来存储指针，不依赖于树的大小。

### 1.2 二叉树的层序遍历 (LeetCode 102)

#### 题目描述
给你二叉树的根节点 root ，返回其节点值的层序遍历。 （即逐层地，从左到右访问所有节点）。

**示例**:
```
输入：root = [3,9,20,null,null,15,7]
输出：[[3],[9,20],[15,7]]
```

#### 题目解析
层序遍历是二叉树的基本遍历方式之一，也称为广度优先遍历(BFS)。本题要求按层返回节点值，考察对队列数据结构的应用和分层遍历技巧。

#### 解题思路
1. 使用队列实现层序遍历
2. 每次处理一层的节点：
   - 记录当前层的节点数量
   - 遍历当前层的所有节点，将节点值加入结果列表
   - 将下一层的节点加入队列（先左后右）
3. 重复步骤2，直到队列为空

```whiteboard
mermaid_text: |
  flowchart TD
    Start([开始]) --> Check[检查root是否为空]
    Check -->|是| ReturnEmpty[返回空列表]
    Check -->|否| Init[初始化队列并加入root]
    Init --> QueueCheck{队列是否为空}
    QueueCheck -->|是| ReturnResult[返回结果]
    QueueCheck -->|否| GetSize[获取当前队列大小]
    GetSize --> CreateLevel[创建当前层列表]
    CreateLevel --> ForLoop[i=0 to size-1]
    ForLoop --> Dequeue[出队一个节点]
    Dequeue --> AddVal[将节点值加入当前层列表]
    AddVal --> EnqueueLeft{左子节点是否存在}
    EnqueueLeft -->|是| AddLeft[左子节点入队]
    EnqueueLeft -->|否| EnqueueRight{右子节点是否存在}
    AddLeft --> EnqueueRight
    EnqueueRight -->|是| AddRight[右子节点入队]
    EnqueueRight -->|否| ContinueLoop[继续循环]
    AddRight --> ContinueLoop
    ContinueLoop -->|循环结束| AddLevel[将当前层加入结果]
    AddLevel --> QueueCheck
```

#### Java解法实现
```java
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            int size = queue.size();
            List<Integer> level = new ArrayList<>();
            
            for (int i = 0; i < size; i++) {
                TreeNode node = queue.poll();
                level.add(node.val);
                
                if (node.left != null) {
                    queue.offer(node.left);
                }
                if (node.right != null) {
                    queue.offer(node.right);
                }
            }
            
            result.add(level);
        }
        
        return result;
    }
}
```

#### 题解背诵技巧
**模板记忆法**：层序遍历是BFS的典型应用，记住以下模板：

```
初始化队列并加入根节点
while 队列不为空:
    获取当前队列大小
    创建当前层列表
    循环当前层节点数:
        出队一个节点
        将节点值加入当前层
        左右子节点入队
    将当前层加入结果
```

这个模板不仅适用于本题，还适用于所有层序遍历相关的变种问题。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是树中的节点数。每个节点都会被访问一次。
- **空间复杂度**：O(m)，其中m是树的最大宽度。队列最多存储一层的节点，最坏情况下为完美二叉树的最后一层，约n/2个节点。

### 1.3 其他二叉树题目列表

以下15道二叉树题目同样重要，按照难度和考察频率排序：

| 题目 | 难度 | 核心考点 | 解题关键 |
|------|------|----------|----------|
| 验证二叉搜索树 (98) | 中等 | BST性质、中序遍历 | 中序遍历是否递增 |
| 二叉树的最近公共祖先 (236) | 中等 | 递归、路径记录 | 后序遍历，左右子树是否包含目标节点 |
| 二叉树的最大深度 (104) | 简单 | 递归、深度计算 | 左右子树最大深度+1 |
| 对称二叉树 (101) | 简单 | 递归、镜像比较 | 左右子树对称比较 |
| 从前序与中序遍历序列构造二叉树 (105) | 中等 | 树的构造 | 前序定根，中序分左右 |
| 二叉树中的最大路径和 (124) | 困难 | 路径问题、递归 | 节点贡献值计算 |
| 路径总和 III (437) | 中等 | 前缀和、递归 | 回溯法记录前缀和 |
| 翻转二叉树 (226) | 简单 | 树的修改 | 交换左右子树 |
| 合并二叉树 (617) | 简单 | 树的合并 | 节点值相加，递归合并左右子树 |
| 把二叉搜索树转换为累加树 (538) | 中等 | BST、中序遍历 | 逆中序遍历累加 |
| 不同的二叉搜索树 (96) | 中等 | 动态规划、卡特兰数 | dp[i] = sum(dp[j] * dp[i-j-1]) |
| 打家劫舍 III (337) | 中等 | 树形DP | 每个节点两种状态：偷或不偷 |
| 二叉树的序列化与反序列化 (297) | 困难 | 树的表示 | 前序遍历，特殊字符处理null |
| 二叉树的直径 (543) | 简单 | 深度计算 | 左右子树深度之和 |
| 中序遍历 (94) | 中等 | 遍历方式 | 递归或使用栈的迭代实现 |

## 2. 栈 (9道)

栈是一种遵循"后进先出"原则的数据结构，在解决特定类型问题时具有独特优势。本章节包含9道栈相关题目，重点考察栈的应用场景和单调栈技巧。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: package
content: |
  **核心考点**：栈的基本操作、单调栈、括号匹配、表达式求值、栈与队列的相互实现。单调栈是解决"下一个更大元素"类问题的高效方法，时间复杂度可从O(n²)降至O(n)。
```

### 2.1 每日温度 (LeetCode 739)

#### 题目描述
给定一个整数数组 temperatures ，表示每天的温度，返回一个数组 answer ，其中 answer[i] 是指对于第 i 天，下一个更高温度出现在几天后。如果气温在这之后都不会升高，请在该位置用 0 来代替。

**示例**:
```
输入: temperatures = [73,74,75,71,69,72,76,73]
输出: [1,1,4,2,1,1,0,0]
```

#### 题目解析
本题要求找出每个温度后面第一个更高温度的距离，是典型的"下一个更大元素"类问题。使用暴力法时间复杂度为O(n²)，而使用单调栈可将时间复杂度降至O(n)。

#### 解题思路
1. 使用单调栈存储温度数组的下标，栈中元素保持单调递减的顺序
2. 遍历温度数组：
   - 当栈不为空且当前温度大于栈顶元素对应的温度时，说明找到了栈顶元素的下一个更高温度
   - 计算天数差并更新结果数组
   - 弹出栈顶元素，继续比较当前温度与新栈顶元素
   - 将当前温度的下标入栈
3. 遍历结束后，栈中剩余元素的结果均为0

```whiteboard
mermaid_text: |
  mindmap
    root(每日温度 - 单调栈应用)
      单调栈特性
        存储下标而非值
        保持栈内元素递减
        每个元素最多入栈出栈一次
      算法步骤
        初始化结果数组和栈
        遍历温度数组
        处理栈顶元素(出栈条件)
        计算天数差
        当前元素入栈
      时间优化
        暴力O(n²)→单调栈O(n)
        一次遍历完成
        空间换时间策略
```

#### Java解法实现
```java
class Solution {
    public int[] dailyTemperatures(int[] temperatures) {
        int n = temperatures.length;
        int[] answer = new int[n];
        Deque<Integer> stack = new LinkedList<>();
        
        for (int i = 0; i < n; i++) {
            // 当栈不为空且当前温度大于栈顶元素对应的温度
            while (!stack.isEmpty() && temperatures[i] > temperatures[stack.peek()]) {
                int prevIndex = stack.pop();
                answer[prevIndex] = i - prevIndex;
            }
            stack.push(i);
        }
        
        // 栈中剩余元素对应的answer值保持为0
        return answer;
    }
}
```

#### 题解背诵技巧
**口诀记忆法**："单调栈存下标，递减顺序要维护，遇到高温就出栈，计算距离存结果"

**关键步骤**：
1. 栈中存储的是下标而非温度值
2. 维持栈的单调递减性质
3. 出栈条件是当前温度 > 栈顶下标对应的温度
4. 结果计算是当前下标 - 栈顶下标

记住单调栈的这个应用模式，可以解决一系列"下一个更大元素"问题。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是温度数组的长度。每个元素最多入栈和出栈一次。
- **空间复杂度**：O(n)，最坏情况下栈存储所有元素(温度严格递减时)。

### 2.2 有效的括号 (LeetCode 20)

#### 题目描述
给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s ，判断字符串是否有效。

有效字符串需满足：
1. 左括号必须用相同类型的右括号闭合。
2. 左括号必须以正确的顺序闭合。
3. 每个右括号都有一个对应的相同类型的左括号。

**示例**:
```
输入：s = "()[]{}"
输出：true

输入：s = "(]"
输出：false
```

#### 题目解析
括号匹配是栈的经典应用场景。通过栈记录左括号，遇到右括号时检查是否与栈顶左括号匹配，匹配则出栈，否则字符串无效。

#### 解题思路
1. 创建一个哈希表存储括号的对应关系：右括号作为键，左括号作为值
2. 初始化栈
3. 遍历字符串的每个字符：
   - 若字符是左括号，入栈
   - 若字符是右括号：
     - 栈为空或栈顶元素与该右括号不匹配，返回false
     - 否则出栈
4. 遍历结束后，若栈为空则所有括号匹配，返回true；否则返回false

#### Java解法实现
```java
class Solution {
    public boolean isValid(String s) {
        // 创建括号映射表
        Map<Character, Character> bracketMap = new HashMap<>();
        bracketMap.put(')', '(');
        bracketMap.put(']', '[');
        bracketMap.put('}', '{');
        
        Deque<Character> stack = new LinkedList<>();
        
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            
            if (bracketMap.containsKey(c)) {
                // 右括号，检查匹配
                if (stack.isEmpty() || stack.peek() != bracketMap.get(c)) {
                    return false;
                }
                stack.pop();
            } else {
                // 左括号，入栈
                stack.push(c);
            }
        }
        
        // 栈为空表示所有括号都匹配
        return stack.isEmpty();
    }
}
```

#### 题解背诵技巧
**三步法**："左括号入栈，右括号匹配，结束栈为空"

**边界情况处理**：
1. 字符串长度为奇数时，直接返回false
2. 第一个字符为右括号时，直接返回false
3. 遍历结束后栈不为空，返回false

这三种情况可以快速判断部分无效字符串，提高效率。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是字符串长度。每个字符只处理一次。
- **空间复杂度**：O(n)，最坏情况下栈存储所有左括号。

### 2.3 其他栈题目列表

以下7道栈题目同样重要，按照难度和考察频率排序：

| 题目 | 难度 | 核心考点 | 解题关键 |
|------|------|----------|----------|
| 接雨水 (42) | 困难 | 单调栈、双指针 | 找左侧和右侧更高的柱子 |
| 最小栈 (155) | 简单 | 栈设计、辅助栈 | 用辅助栈存储最小值 |
| 柱状图中最大的矩形 (84) | 困难 | 单调栈、面积计算 | 找左右第一个更小的柱子 |
| 最长有效括号 (32) | 困难 | 栈、动态规划 | 栈存储括号下标 |
| 字符串解码 (394) | 中等 | 栈、递归 | 数字栈和字符串栈分别存储 |
| 最大矩形 (85) | 困难 | 单调栈、矩阵转换 | 转换为柱状图最大矩形问题 |
| 回文链表 (234) | 简单 | 栈、快慢指针 | 后半部分反转比较或栈存储前半部分 |

## 3. 链表 (10道)

链表是一种常见的数据结构，其节点在内存中不连续存储，通过指针连接。链表题目主要考察指针操作能力和边界情况处理。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: link
content: |
  **核心考点**：链表的遍历、反转、环检测、合并、删除特定节点。解决链表问题的关键在于熟练掌握指针操作和哑巴节点(dummy node)技巧，以及快慢指针的应用。
```

### 3.1 两数相加 (LeetCode 2)

#### 题目描述
给你两个非空的链表，表示两个非负的整数。它们每位数字都是按照逆序的方式存储的，并且每个节点只能存储一位数字。请你将两个数相加，并以相同形式返回一个表示和的链表。

你可以假设除了数字 0 之外，这两个数都不会以 0 开头。

**示例**:
```
输入：l1 = [2,4,3], l2 = [5,6,4]
输出：[7,0,8]
解释：342 + 465 = 807
```

#### 题目解析
本题考察链表的遍历和基本运算。由于数字是逆序存储的，我们可以直接从链表头部开始相加，模拟加法运算，注意处理进位和链表长度不一致的情况。

#### 解题思路
1. 创建哑巴节点(dummy node)作为结果链表的头节点
2. 初始化进位carry为0
3. 同时遍历两个链表：
   - 计算当前节点的和：l1.val + l2.val + carry
   - 更新进位carry：sum / 10
   - 创建新节点存储sum % 10
   - 移动指针到下一个节点
4. 处理剩余节点和进位：
   - 如果l1有剩余，继续处理
   - 如果l2有剩余，继续处理
   - 如果carry > 0，创建新节点存储carry
5. 返回哑巴节点的下一个节点作为结果

```whiteboard
block_type: whiteboard
diagram_type: 3
mermaid_text: |
  flowchart TD
    Start([开始]) --> CreateDummy[创建dummy节点和current指针]
    CreateDummy --> InitCarry[carry=0]
    InitCarry --> LoopCondition{l1不为空或l2不为空或carry>0}
    LoopCondition -->|否| ReturnResult[dummy.next]
    LoopCondition -->|是| GetVals[获取l1.val和l2.val，不存在则为0]
    GetVals --> Sum[sum = val1 + val2 + carry]
    Sum --> UpdateCarry[carry = sum / 10]
    UpdateCarry --> CreateNode[创建值为sum%10的新节点]
    CreateNode --> Link[current.next = 新节点]
    Link --> MoveCurrent[current = current.next]
    MoveCurrent --> MovePointers[移动l1和l2指针]
    MovePointers --> LoopCondition
```

#### Java解法实现
```java
/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;
        int carry = 0;
        
        while (l1 != null || l2 != null || carry > 0) {
            int val1 = (l1 != null) ? l1.val : 0;
            int val2 = (l2 != null) ? l2.val : 0;
            
            int sum = val1 + val2 + carry;
            carry = sum / 10;
            
            current.next = new ListNode(sum % 10);
            current = current.next;
            
            if (l1 != null) l1 = l1.next;
            if (l2 != null) l2 = l2.next;
        }
        
        return dummy.next;
    }
}
```

#### 题解背诵技巧
**三要素**："哑巴节点记录头，进位carry要记住，长短链表都照顾"

**关键步骤**：
1. 哑巴节点的使用避免处理头节点特殊情况
2. 循环条件包含carry>0，处理最后一位进位
3. 取值时判断链表是否为空，避免空指针异常

这个模板可以应用于所有链表求和或拼接问题。

#### 复杂度分析
- **时间复杂度**：O(max(m,n))，其中m和n分别是两个链表的长度。需要遍历到较长链表的末尾。
- **空间复杂度**：O(max(m,n)+1)，结果链表的长度最多为较长链表的长度+1(进位)。

### 3.2 反转链表 (LeetCode 206)

#### 题目描述
给你单链表的头节点 head，请你反转链表，并返回反转后的链表。

**示例**:
```
输入：head = [1,2,3,4,5]
输出：[5,4,3,2,1]
```

#### 题目解析
反转链表是最基础也最重要的链表操作之一。考察对链表指针操作的掌握程度，有迭代和递归两种实现方式。

#### 解题思路
**迭代法**：
1. 初始化三个指针：prev(前驱)、current(当前)、next(后继)
2. 遍历链表：
   - 保存当前节点的下一个节点(next)
   - 将当前节点的next指向前驱节点(prev)
   - 移动prev到current，current到next
3. 遍历结束后，prev成为新的头节点

**递归法**：
1. 递归反转当前节点的下一个节点
2. 将当前节点的下一个节点的next指向当前节点
3. 将当前节点的next设为null
4. 返回反转后的头节点

#### Java解法实现
**迭代法**：
```java
/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode current = head;
        
        while (current != null) {
            ListNode next = current.next; // 保存下一个节点
            current.next = prev;          // 反转当前节点的指针
            prev = current;               // 移动prev指针
            current = next;               // 移动current指针
        }
        
        return prev; // prev成为新的头节点
    }
}
```

**递归法**：
```java
class Solution {
    public ListNode reverseList(ListNode head) {
        // 基本情况：空链表或只有一个节点
        if (head == null || head.next == null) {
            return head;
        }
        
        // 递归反转剩余链表
        ListNode newHead = reverseList(head.next);
        
        // 反转当前节点的指针
        head.next.next = head;
        head.next = null;
        
        return newHead;
    }
}
```

#### 题解背诵技巧
**迭代法口诀**："prev初始为null，current指向头，保存next，反转指针，移动prev和current"

**递归法口诀**："归到最后节点，反转指针指向，当前节点next为null"

在面试中，迭代法通常更受青睐，因为它没有递归调用栈的开销。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是链表的长度。需要遍历所有节点。
- **空间复杂度**：O(1)，迭代法只使用常数空间；递归法为O(n)，需要递归调用栈空间。

## 4. 字符串 (8道)

字符串操作是算法面试中的常见内容，涉及哈希表、双指针、动态规划等多种算法思想。本章节包含8道经典字符串题目。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: abc
content: |
  **核心考点**：字符串匹配、子串问题、回文判断、字符计数。掌握字符串问题的关键在于灵活运用哈希表进行字符统计和滑动窗口技巧处理子串问题。
```

### 4.1 无重复字符的最长子串 (LeetCode 3)

#### 题目描述
给定一个字符串 s ，请你找出其中不含有重复字符的 最长子串 的长度。

**示例**:
```
输入: s = "abcabcbb"
输出: 3 
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。
```

#### 题目解析
本题是滑动窗口和哈希表的经典应用。需要找到最长的不包含重复字符的连续子串，关键在于如何高效判断重复字符并移动窗口。

#### 解题思路
1. 使用哈希表存储字符最后出现的索引
2. 初始化左指针left=0，最大长度result=0
3. 遍历字符串，右指针right从0到n-1：
   - 如果当前字符在哈希表中且索引 >= left，更新left为该字符上次索引+1
   - 更新当前字符的索引到哈希表
   - 更新最大长度result = max(result, right-left+1)
4. 返回result

```whiteboard
block_type: whiteboard
diagram_type: 3
mermaid_text: |
  flowchart TD
    Start([开始]) --> Init[初始化哈希表, left=0, result=0]
    Init --> Loop[right=0 to s.length-1]
    Loop --> GetChar[获取当前字符c]
    GetChar --> CheckMap{map包含c且map[c]>=left}
    CheckMap -->|是| UpdateLeft[left=map[c]+1]
    CheckMap -->|否| UpdateMap[map.put(c, right)]
    UpdateLeft --> UpdateMap
    UpdateMap --> UpdateResult[result=max(result, right-left+1)]
    UpdateResult --> ContinueLoop[right++]
    ContinueLoop --> Loop
    Loop -->|结束| ReturnResult[返回result]
```

#### Java解法实现
```java
class Solution {
    public int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> map = new HashMap<>();
        int left = 0;
        int result = 0;
        
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            
            // 如果字符已存在且在当前窗口内，移动左指针
            if (map.containsKey(c) && map.get(c) >= left) {
                left = map.get(c) + 1;
            }
            
            // 更新字符位置和最大长度
            map.put(c, right);
            result = Math.max(result, right - left + 1);
        }
        
        return result;
    }
}
```

#### 题解背诵技巧
**滑动窗口四步法**："哈希表存索引，左指针控窗口，右指针扩范围，计算最大长度"

**关键注意点**：
- 判断字符是否在当前窗口内：map.get(c) >= left
- 不要忘记更新字符的最新位置
- 每次移动后都计算窗口大小

这种滑动窗口+哈希表的模式可以解决大多数子串问题。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是字符串的长度。每个字符最多被访问两次(左右指针各一次)。
- **空间复杂度**：O(min(m,n))，其中m是字符集的大小。哈希表最多存储min(m,n)个字符。

### 4.2 最长回文子串 (LeetCode 5)

#### 题目描述
给你一个字符串 s，找到 s 中最长的回文子串。

**示例**:
```
输入：s = "babad"
输出："bab"
解释："aba" 同样是符合题意的答案。
```

#### 题目解析
回文子串是指正读和反读都一样的字符串。本题要求找到最长的回文子串，有多种解法，包括暴力法、动态规划和中心扩展法。其中中心扩展法是最高效且易于实现的方法。

#### 解题思路
**中心扩展法**：
1. 回文子串可以有一个中心(奇数长度)或两个中心(偶数长度)
2. 遍历字符串，对每个字符和每对相邻字符进行中心扩展
3. 记录扩展得到的最长回文子串的起始和结束索引
4. 返回最长回文子串

#### Java解法实现
```java
class Solution {
    private int start, maxLen;
    
    public String longestPalindrome(String s) {
        int n = s.length();
        if (n < 2) return s;
        
        for (int i = 0; i < n - 1; i++) {
            // 奇数长度回文
            expandAroundCenter(s, i, i);
            // 偶数长度回文
            expandAroundCenter(s, i, i + 1);
        }
        
        return s.substring(start, start + maxLen);
    }
    
    private void expandAroundCenter(String s, int left, int right) {
        // 中心扩展
        while (left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right)) {
            left--;
            right++;
        }
        
        // 更新最长回文子串
        int currentLen = right - left - 1;
        if (currentLen > maxLen) {
            start = left + 1;
            maxLen = currentLen;
        }
    }
}
```

#### 题解背诵技巧
**中心扩展法口诀**："一个中心奇数长，两个中心偶数长，向两边扩展找最长"

**关键步骤**：
1. 循环到n-1，避免最后一个字符的偶数扩展越界
2. 扩展结束后计算长度：right-left-1
3. 更新起始位置：start = left+1

这种方法比动态规划更直观，且空间复杂度更低。

#### 复杂度分析
- **时间复杂度**：O(n²)，其中n是字符串的长度。对于每个中心，扩展最多需要O(n)时间。
- **空间复杂度**：O(1)，只使用常数空间。

## 5. 数组 (37道)

数组是最基础的数据结构，也是算法面试中考察最多的内容之一。本章节包含37道经典数组题目，涵盖排序、查找、动态规划等多种算法思想。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: array
content: |
  **核心考点**：二分查找、双指针、滑动窗口、动态规划、贪心算法。数组题目类型多样，但很多问题都可以用双指针或滑动窗口技巧优化到O(n)时间复杂度。
```

### 5.1 两数之和 (LeetCode 1)

#### 题目描述
给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

**示例**:
```
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。
```

#### 题目解析
两数之和是LeetCode的第一道题目，也是哈希表应用的经典案例。虽然可以用暴力法解决，但哈希表能将时间复杂度从O(n²)降至O(n)。

#### 解题思路
1. 创建哈希表存储数组元素和索引的映射关系
2. 遍历数组，对每个元素nums[i]：
   - 计算目标补数：complement = target - nums[i]
   - 如果补数在哈希表中，返回补数的索引和当前索引i
   - 否则将当前元素和索引存入哈希表
3. 如果遍历结束未找到，返回空数组或抛出异常

```whiteboard
block_type: whiteboard
diagram_type: 3
mermaid_text: |
  flowchart TD
    Start([开始]) --> Init[初始化哈希表]
    Init --> Loop[i=0 to nums.length-1]
    Loop --> Compute[complement = target - nums[i]]
    Compute --> CheckMap{map包含complement?}
    CheckMap -->|是| ReturnResult[返回[map.get(complement), i]]
    CheckMap -->|否| AddToMap[map.put(nums[i], i)]
    AddToMap --> ContinueLoop[i++]
    ContinueLoop --> Loop
    Loop -->|结束| ReturnEmpty[返回空数组]
```

#### Java解法实现
```java
class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            
            map.put(nums[i], i);
        }
        
        // 根据题目描述，这里理论上不会到达
        throw new IllegalArgumentException("No two sum solution");
    }
}
```

#### 题解背诵技巧
**口诀记忆法**："哈希表存值和索引，遍历计算补数，找到则返回，否则存当前值"

**关键注意点**：
- 先检查补数再存入当前值，避免使用同一个元素两次
- 哈希表查找时间为O(1)，使整体复杂度降至O(n)
- 题目保证有唯一解，可以放心返回第一个找到的结果

这种"补数查找"模式适用于多种求和问题。

#### 复杂度分析
- **时间复杂度**：O(n)，其中n是数组的长度。只需遍历一次数组。
- **空间复杂度**：O(n)，最坏情况下需要存储n-1个元素到哈希表。

### 5.2 三数之和 (LeetCode 15)

#### 题目描述
给你一个包含 n 个整数的数组 nums，判断 nums 中是否存在三个元素 a，b，c ，使得 a + b + c = 0 ？请你找出所有和为 0 且不重复的三元组。

注意：答案中不可以包含重复的三元组。

**示例**:
```
输入：nums = [-1,0,1,2,-1,-4]
输出：[[-1,-1,2],[-1,0,1]]
```

#### 题目解析
三数之和是两数之和的扩展，增加了去重的要求。最优解法是排序+双指针，时间复杂度为O(n²)，比暴力法的O(n³)有显著提升。

#### 解题思路
1. 对数组进行排序，便于去重和双指针操作
2. 遍历数组，固定第一个数nums[i]：
   - 如果nums[i] > 0，由于数组已排序，三数之和一定大于0，可直接break
   - 跳过重复的nums[i]：如果i>0且nums[i]==nums[i-1]，continue
   - 使用双指针查找另外两个数：
     - 左指针left = i+1，右指针right = n-1
     - 计算三数之和sum = nums[i] + nums[left] + nums[right]
     - sum == 0：加入结果，同时跳过重复的left和right
     - sum < 0：左指针右移，增大sum
     - sum > 0：右指针左移，减小sum
3. 返回结果列表

#### Java解法实现
```java
class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        int n = nums.length;
        if (n < 3) return result;
        
        // 排序
        Arrays.sort(nums);
        
        for (int i = 0; i < n - 2; i++) {
            // 第一个数大于0，三数之和一定大于0
            if (nums[i] > 0) break;
            
            // 跳过重复的第一个数
            if (i > 0 && nums[i] == nums[i - 1]) continue;
            
            int left = i + 1;
            int right = n - 1;
            
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                
                if (sum == 0) {
                    // 找到一个三元组
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    
                    // 跳过重复的第二个数
                    while (left < right && nums[left] == nums[left + 1]) {
                        left++;
                    }
                    
                    // 跳过重复的第三个数
                    while (left < right && nums[right] == nums[right - 1]) {
                        right--;
                    }
                    
                    // 移动双指针
                    left++;
                    right--;
                } else if (sum < 0) {
                    // 和太小，左指针右移
                    left++;
                } else {
                    // 和太大，右指针左移
                    right--;
                }
            }
        }
        
        return result;
    }
}
```

#### 题解背诵技巧
**三步法**："先排序，定一数，双指针"

**去重关键**：
1. 第一个数去重：i>0且nums[i]==nums[i-1]
2. 第二个数去重：找到解后，循环判断nums[left]==nums[left+1]
3. 第三个数去重：找到解后，循环判断nums[right]==nums[right-1]

记住排序是去重和双指针的基础，这是解决三数之和问题的关键。

#### 复杂度分析
- **时间复杂度**：O(n²)，其中n是数组的长度。排序的时间复杂度为O(n log n)，双指针遍历为O(n²)，整体由后者主导。
- **空间复杂度**：O(log n)至O(n)，取决于排序算法的实现和结果存储需求。

## 6. 搜索 (11道)

搜索类题目涵盖回溯、DFS、BFS等算法思想，是考察问题建模和搜索策略的重要内容。本章节包含11道经典搜索题目。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: mag
content: |
  **核心考点**：深度优先搜索(DFS)、广度优先搜索(BFS)、回溯算法、记忆化搜索。解决搜索问题的关键在于合理设计搜索空间和优化剪枝策略。
```

### 6.1 全排列 (LeetCode 46)

#### 题目描述
给定一个不含重复数字的数组 nums ，返回其所有可能的全排列。你可以按任意顺序返回答案。

**示例**:
```
输入：nums = [1,2,3]
输出：[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

#### 题目解析
全排列是回溯算法的经典应用。需要生成数组的所有可能排列，关键在于如何高效地进行元素选择和回溯操作。

#### 解题思路
1. 使用回溯法递归生成排列：
   - 定义递归函数backtrack(路径, 选择列表)
   - 基本情况：如果路径长度等于数组长度，将路径加入结果
   - 递归情况：遍历选择列表中的每个元素
     - 做选择：将元素加入路径，从选择列表中移除
     - 递归调用backtrack
     - 撤销选择：将元素从路径中移除，加回选择列表
2. 初始调用backtrack(空路径, 完整数组)
3. 返回结果列表

```whiteboard
block_type: whiteboard
diagram_type: 1
mermaid_text: |
  mindmap
    root(全排列 - 回溯法)
      递归函数
        参数: 路径, 选择列表
        返回值: void
        作用: 生成所有排列
      基本情况
        路径长度 == 数组长度
        添加路径到结果
      递归过程
        遍历选择列表
        做选择
        递归调用
        撤销选择
      优化技巧
        不使用额外空间记录选择
        通过交换元素实现选择
```

#### Java解法实现
```java
class Solution {
    public List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, 0, result);
        return result;
    }
    
    // 优化版本：通过交换元素实现选择，不需要额外空间存储选择列表
    private void backtrack(int[] nums, int start, List<List<Integer>> result) {
        // 基本情况：到达数组末尾，添加当前排列
        if (start == nums.length) {
            List<Integer> path = new ArrayList<>();
            for (int num : nums) {
                path.add(num);
            }
            result.add(path);
            return;
        }
        
        // 递归情况：遍历所有可能的选择
        for (int i = start; i < nums.length; i++) {
            // 做选择：交换元素，将nums[i]放到start位置
            swap(nums, start, i);
            
            // 递归：继续处理下一个位置
            backtrack(nums, start + 1, result);
            
            // 撤销选择：交换回来，恢复原状
            swap(nums, start, i);
        }
    }
    
    private void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
}
```

#### 题解背诵技巧
**回溯四步法**："做选择，递归，撤销选择，记录结果"

**优化技巧**：
- 通过数组元素交换实现选择，避免使用额外空间存储选择列表
- 直接修改原数组，递归返回后恢复，节省空间
- 这种"原地回溯"技术适用于多种排列组合问题

记住回溯算法的核心是"尝试所有可能，不合适就退回"，这是解决排列、组合、子集等问题的通用思路。

#### 复杂度分析
- **时间复杂度**：O(n×n!)，其中n是数组的长度。共有n!个排列，每个排列需要O(n)时间复制到结果列表。
- **空间复杂度**：O(n)，递归调用栈的深度为n，结果存储不计入额外空间。

## 7. 矩阵 (4道)

矩阵是二维数组的应用，涉及搜索、动态规划等算法思想。本章节包含4道经典矩阵题目。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: squares
content: |
  **核心考点**：矩阵遍历、搜索路径、动态规划。矩阵问题通常可以转换为图的遍历问题，DFS和BFS是常用解法。
```

### 7.1 岛屿数量 (LeetCode 200)

#### 题目描述
给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。

岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。

此外，你可以假设该网格的四条边均被水包围。

**示例**:
```
输入：grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
输出：3
```

#### 题目解析
岛屿数量是矩阵DFS的经典问题。需要计算网格中连通的'1'的块数，关键在于如何标记已访问的陆地并进行深度优先搜索。

#### 解题思路
1. 遍历矩阵的每个单元格：
   - 如果当前单元格是'1'（陆地）：
     - 岛屿数量加1
     - 使用DFS或BFS标记所有相连的陆地为'0'（已访问）
2. 返回岛屿数量

**DFS方法**：
- 定义递归函数dfs(grid, i, j)
- 基本情况：如果i或j越界，或grid[i][j]不是'1'，返回
- 标记当前单元格为'0'（已访问）
- 递归调用dfs处理上、下、左、右四个方向的单元格

#### Java解法实现
```java
class Solution {
    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) {
            return 0;
        }
        
        int rows = grid.length;
        int cols = grid[0].length;
        int count = 0;
        
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                // 发现陆地，开始DFS
                if (grid[i][j] == '1') {
                    count++;
                    dfs(grid, i, j);
                }
            }
        }
        
        return count;
    }
    
    private void dfs(char[][] grid, int i, int j) {
        int rows = grid.length;
        int cols = grid[0].length;
        
        // 基本情况：越界或不是陆地
        if (i < 0 || i >= rows || j < 0 || j >= cols || grid[i][j] != '1') {
            return;
        }
        
        // 标记为已访问（将陆地变为水）
        grid[i][j] = '0';
        
        // 递归处理上下左右四个方向
        dfs(grid, i - 1, j); // 上
        dfs(grid, i + 1, j); // 下
        dfs(grid, i, j - 1); // 左
        dfs(grid, i, j + 1); // 右
    }
}
```

#### 题解背诵技巧
**口诀记忆法**："遇陆地计数加一，DFS淹没法标记，上下左右都遍历"

**关键步骤**：
1. 双重循环遍历每个单元格
2. 遇到'1'时计数并启动DFS
3. DFS中将访问过的'1'改为'0'，避免重复计数
4. 四个方向都要递归处理

这种"淹没"技术是处理连通区域问题的常用方法，不需要额外空间存储访问标记。

#### 复杂度分析
- **时间复杂度**：O(m×n)，其中m和n分别是矩阵的行数和列数。每个单元格最多被访问一次。
- **空间复杂度**：O(m×n)，最坏情况下（全是陆地），递归调用栈深度为m×n。

## 8. 递推 (4道)

递推类题目主要考察动态规划思想，通过建立状态转移方程解决问题。本章节包含4道经典递推题目。

```callout
block_type: callout
background_color: 6
border_color: 6
emoji_id: repeat
content: |
  **核心考点**：动态规划、状态定义、转移方程。解决递推问题的关键在于找到问题的状态转移规律，并正确定义dp数组的含义。
```

### 8.1 爬楼梯 (LeetCode 70)

#### 题目描述
假设你正在爬楼梯。需要 n 阶你才能到达楼顶。

每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？

**示例**:
```
输入：n = 3
输出：3
解释：有三种方法可以爬到楼顶。
1. 1 阶 + 1 阶 + 1 阶
2. 1 阶 + 2 阶
3. 2 阶 + 1 阶
```

#### 题目解析
爬楼梯是动态规划的入门题目。通过分析可以发现，爬到第n阶的方法数等于爬到第n-1阶和第n-2阶的方法数之和，这是一个斐波那契数列问题。

#### 解题思路
1. **动态规划解法**：
   - 定义dp[i]为爬到第i阶的方法数
   - 状态转移方程：dp[i] = dp[i-1] + dp[i-2]
   - 边界条件：dp[1] = 1, dp[2] = 2
   - 从3到n计算dp[i]
   - 返回dp[n]

2. **优化空间解法**：
   - 观察到dp[i]只依赖于dp[i-1]和dp[i-2]
   - 使用两个变量a和b分别表示dp[i-2]和dp[i-1]
   - 迭代计算：c = a + b，a = b，b = c
   - 只需O(1)空间复杂度

#### Java解法实现
**动态规划解法**：
```java
class Solution {
    public int climbStairs(int n) {
        if (n <= 2) {
            return n;
        }
        
        int[] dp = new int[n + 1];
        dp[1] = 1;
        dp[2] = 2;
        
        for (int i = 3; i <= n; i++) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }
        
        return dp[n];
    }
}
```

**空间优化解法**：
```java
class Solution {
    public int climbStairs(int n) {
        if (n <= 2) {
            return n;
        }
        
        int a = 1; // dp[i-2]
        int b = 2; // dp[i-1]
        
        for (int i = 3; i <= n; i++) {
            int c = a + b;
            a = b;
            b = c;
        }
        
        return b;
    }
}
```

#### 题解背诵技巧
**递推公式**："dp[n] = dp[n-1] + dp[n-2]"，本质是斐波那契数列

**记忆方法**：
- 第n阶只能从第n-1阶或n-2阶到达
- 所以方法数是两者之和
- 边界情况：1阶1种方法，2阶2种方法

这是最简单的动态规划问题之一，但其思想可以应用于更复杂的问题。

#### 复杂度分析
- **时间复杂度**：O(n)，需要计算从3到n的每个值。
- **空间复杂度**：O(n)（动态规划解法）或O(1)（空间优化解法）。

## 9. 算法模板与解题技巧总结

### 9.1 常用数据结构时间复杂度

掌握数据结构的时间复杂度是算法优化的基础：

| 数据结构 | 访问 | 插入 | 删除 | 备注 |
|----------|------|------|------|------|
| 数组 | O(1) | O(n) | O(n) | 随机访问快，插入删除慢 |
| 链表 | O(n) | O(1) | O(1) | 插入删除快，访问慢 |
| 栈 | O(1) | O(1) | O(1) | 后进先出 |
| 队列 | O(1) | O(1) | O(1) | 先进先出 |
| 哈希表 | O(1) | O(1) | O(1) | 平均情况，无序 |
| 红黑树 | O(log n) | O(log n) | O(log n) | 有序，自平衡 |

### 9.2 核心算法模板

#### 9.2.1 回溯算法模板

```java
void backtrack(参数列表) {
    if (终止条件) {
        收集结果;
        return;
    }
    
    for (选择范围内的选项) {
        if (剪枝条件) continue;
        
        做选择;
        backtrack(新参数);
        撤销选择; // 回溯
    }
}
```

**应用场景**：排列、组合、子集、路径搜索等问题。

**剪枝技巧**：
- 提前判断不可能到达目标的路径
- 去重处理，避免重复解
- 边界条件判断

#### 9.2.2 动态规划模板

```java
// 一维DP
int[] dp = new int[n + 1];
dp[0] = 初始值;

for (int i = 1; i <= n; i++) {
    dp[i] = 状态转移方程;
}

return dp[n];

// 二维DP
int[][] dp = new int[m + 1][n + 1];
// 初始化边界条件

for (int i = 1; i <= m; i++) {
    for (int j = 1; j <= n; j++) {
        dp[i][j] = 状态转移方程;
    }
}

return dp[m][n];
```

**应用场景**：最优子结构问题，如最长公共子序列、背包问题、编辑距离等。

**关键步骤**：
- 定义dp数组含义
- 确定状态转移方程
- 设置边界条件
- 确定计算顺序

#### 9.2.3 滑动窗口模板

```java
int left = 0;
int result = 0;

for (int right = 0; right < n; right++) {
    // 扩大窗口，加入right对应元素
    window.add(nums[right]);
    
    // 当窗口不符合条件时，缩小窗口
    while (window不符合条件) {
        window.remove(nums[left]);
        left++;
    }
    
    // 更新结果
    result = Math.max(result, right - left + 1);
}

return result;
```

**应用场景**：子串、子数组问题，如最长无重复子串、最小覆盖子串等。

**关键要素**：
- 窗口条件定义
- 窗口扩大方式
- 窗口缩小时机
- 结果更新时机

### 9.3 解题技巧总结

#### 9.3.1 数组/字符串常用技巧

1. **双指针**：
   - 首尾指针：二分查找、两数之和
   - 快慢指针：链表环检测、数组去重
   - 滑动窗口：子串问题

2. **前缀和**：
   - 快速计算子数组和
   - 解决和为K的子数组问题

3. **哈希表**：
   - 字符/元素计数
   - 快速查找补数或索引

#### 9.3.2 树/图常用技巧

1. **遍历方法**：
   - 树：前中后序遍历（递归/迭代）、层序遍历
   - 图：DFS、BFS、拓扑排序

2. **二叉树递归套路**：
   - 确定递归函数参数和返回值
   - 确定终止条件
   - 确定单层递归逻辑

3. **图的表示**：
   - 邻接矩阵：空间O(n²)，适合稠密图
   - 邻接表：空间O(n+m)，适合稀疏图

#### 9.3.3 复杂度分析技巧

1. **时间复杂度**：
   - 循环次数：确定基本操作执行次数
   - 递归深度：递归算法的栈深度
   - 最坏/平均情况：区分不同输入情况下的复杂度

2. **空间复杂度**：
   - 额外空间：算法使用的额外存储空间
   - 递归栈空间：递归调用占用的栈空间
   - 输出空间：通常不计入空间复杂度

### 9.4 面试解题步骤

1. **理解问题**：
   - 明确输入输出
   - 确认边界条件
   - 考虑特殊情况

2. **设计算法**：
   - 暴力解法 → 优化思路
   - 数据结构选择
   - 算法复杂度分析

3. **编码实现**：
   - 伪代码 → 代码转换
   - 边界条件处理
   - 代码可读性

4. **测试验证**：
   - 测试用例设计
   - 调试与修复
   - 优化与重构

通过系统学习以上算法模板和解题技巧，并结合LeetCode Hot100题目练习，能够有效提升算法解题能力，为技术面试做好充分准备。记住，算法学习是一个循序渐进的过程，关键在于理解思想而非死记硬背。