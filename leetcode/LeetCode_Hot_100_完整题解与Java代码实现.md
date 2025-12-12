```callout
  **LeetCode Hot 100 完整题解与Java代码实现**  
  本文档包含LeetCode 2024-2025年度Hot 100题目的系统性解答，按算法类型分类整理，每题均提供完整Java代码、详细解题思路、核心考点提炼、复杂度分析及相关变体扩展。内容基于最新题目数据，重点覆盖面试高频考点，适合算法进阶与面试准备使用。
```

### 一、哈希表类题目（3题）

#### 1. 两数之和（LeetCode #1，简单）

```callout
  **核心考点**：哈希表的查找优化、空间换时间策略  
  **解题关键**：通过哈希表记录已遍历元素及其索引，将两数之和转化为单一元素查找问题  
  **面试频率**：★★★★★（算法面试入门必考题）
```

**题目描述**：给定一个整数数组nums和一个整数目标值target，请你在该数组中找出和为目标值target的那两个整数，并返回它们的数组下标[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)[[2]](https://blog.csdn.net/a131529/article/details/142311212)。

**解题思路**：
1. **暴力解法**：双重循环遍历数组，检查每对元素之和是否等于target，时间复杂度O(n²)，空间复杂度O(1)
2. **哈希优化**：使用HashMap存储已遍历元素及其索引，单次遍历即可完成查找
   - 遍历数组每个元素nums[i]
   - 计算补数complement = target - nums[i]
   - 检查HashMap中是否存在complement，若存在则返回对应索引和当前i
   - 若不存在则将当前元素nums[i]及其索引i存入HashMap

**Java代码实现**：

```java
import java.util.HashMap;
import java.util.Map;

class Solution {
    public int[] twoSum(int[] nums, int target) {
        // 创建哈希表存储元素值到索引的映射
        Map<Integer, Integer> map = new HashMap<>();
        
        // 遍历数组，寻找目标值
        for (int i = 0; i < nums.length; i++) {
            // 计算当前元素需要的补数
            int complement = target - nums[i];
            
            // 如果补数已存在于哈希表中，直接返回结果
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            
            // 否则将当前元素及其索引存入哈希表
            map.put(nums[i], i);
        }
        
        // 根据题目要求，输入一定存在解，所以不会执行到这里
        throw new IllegalArgumentException("No solution found");
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，仅需一次遍历数组，哈希表的插入和查找操作平均时间复杂度均为O(1)
- **空间复杂度**：O(n)，最坏情况下需要存储n-1个元素到哈希表中

**背题技巧**：
- 当题目需要"寻找两数满足特定条件"时，优先考虑哈希表存储已访问元素
- 记住核心公式：`complement = target - current`，通过查找complement确定结果
- 哈希表中key存元素值，value存索引，这是此类问题的标准存储方式

**相关变体**：
- **三数之和**（LeetCode #15）：排序+双指针解法，需注意去重处理
- **四数之和**（LeetCode #18）：固定两个数后转化为两数之和问题
- **两数之和 IV - 输入BST**（LeetCode #653）：利用BST特性或哈希表辅助查找

#### 2. 字母异位词分组（LeetCode #49，中等）

```callout
block_type: callout
background_color: 4
border_color: 4
emoji_id: star
content: |
  **核心考点**：哈希表键设计、字符串标准化处理  
  **解题关键**：将异位词转化为相同的键表示（排序或计数），通过哈希表分组  
  **面试频率**：★★★★☆（字符串处理与哈希表结合的典型应用）
```

**题目描述**：给你一个字符串数组，请你将字母异位词组合在一起。可以按任意顺序返回结果列表[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **排序法**：对于每个字符串，将其字符排序后作为哈希表的键，原字符串作为值加入对应列表
2. **计数法**：统计每个字符串中各字符出现的次数，用计数数组生成唯一键（如"aab"→"2,1,0,..."）

**Java代码实现（排序法）**：

```java
import java.util.*;

class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        // 创建哈希表，键为排序后的字符串，值为异位词列表
        Map<String, List<String>> map = new HashMap<>();
        
        for (String str : strs) {
            // 将字符串转换为字符数组并排序
            char[] chars = str.toCharArray();
            Arrays.sort(chars);
            
            // 排序后的字符数组作为键
            String key = new String(chars);
            
            // 如果键不存在，则创建新列表
            if (!map.containsKey(key)) {
                map.put(key, new ArrayList<>());
            }
            
            // 将原字符串添加到对应列表中
            map.get(key).add(str);
        }
        
        // 返回所有异位词分组
        return new ArrayList<>(map.values());
    }
}
```

**Java代码实现（计数法 - 优化版）**：

```java
import java.util.*;

class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        // 创建哈希表，键为字符计数表示，值为异位词列表
        Map<String, List<String>> map = new HashMap<>();
        
        for (String str : strs) {
            // 计算每个字符出现的次数（仅考虑小写字母）
            int[] count = new int[26];
            for (char c : str.toCharArray()) {
                count[c - 'a']++;
            }
            
            // 构建计数字符串作为键（如"aab"→"2,1,0,..."）
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 26; i++) {
                sb.append(count[i]).append(',');
            }
            String key = sb.toString();
            
            // 添加到对应分组
            map.computeIfAbsent(key, k -> new ArrayList<>()).add(str);
        }
        
        return new ArrayList<>(map.values());
    }
}
```

**复杂度分析**：
- **排序法**：
  - 时间复杂度：O(nk log k)，n为字符串数量，k为字符串最大长度
  - 空间复杂度：O(nk)，存储所有字符串
- **计数法**：
  - 时间复杂度：O(nk)，避免了排序的O(k log k)开销
  - 空间复杂度：O(nk)，存储所有字符串和计数数组

**背题技巧**：
- 异位词问题的核心是找到一种"标准化表示"，使所有异位词具有相同的表示
- 排序法实现简单但性能略差，计数法性能更好但实现稍复杂
- 记住计数法的键生成方式：26位计数数组转字符串，用分隔符避免歧义（如"11"可能是一个字符出现11次或两个字符各出现1次）

**相关变体**：
- **有效的字母异位词**（LeetCode #242）：简化版，只需判断两个字符串是否为异位词
- **找到字符串中所有字母异位词**（LeetCode #438）：滑动窗口+计数比较
- **字母异位词分组 II**：考虑包含unicode字符的情况，需使用更通用的计数方法

#### 3. 最长连续序列（LeetCode #128，中等）

```callout
block_type: callout
background_color: 4
border_color: 4
emoji_id: star
content: |
  **核心考点**：哈希表优化查找、集合去重、序列起始点判断  
  **解题关键**：通过集合快速查找，仅对序列起始点进行延伸计算  
  **面试频率**：★★★★☆（哈希表与贪心思想结合的经典问题）
```

**题目描述**：给定一个未排序的整数数组nums，找出数字连续的最长序列的长度，设计算法的时间复杂度为O(n)[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **哈希集合预处理**：将数组元素存入集合，实现O(1)查找和去重
2. **查找序列起始点**：对每个元素，检查是否为序列起点（即num-1不在集合中）
3. **延伸计算长度**：从起始点开始，依次查找num+1, num+2...，计算序列长度

**Java代码实现**：

```java
import java.util.*;

class Solution {
    public int longestConsecutive(int[] nums) {
        if (nums == null || nums.length == 0) {
            return 0;
        }
        
        // 将所有数字存入哈希集，实现O(1)查找和去重
        Set<Integer> numSet = new HashSet<>();
        for (int num : nums) {
            numSet.add(num);
        }
        
        int maxLength = 0;
        
        // 遍历集合中的每个数字
        for (int num : numSet) {
            // 只处理序列的起始数字（即num-1不在集合中）
            if (!numSet.contains(num - 1)) {
                int currentNum = num;
                int currentLength = 1;
                
                // 延伸序列，查找currentNum+1, currentNum+2...
                while (numSet.contains(currentNum + 1)) {
                    currentNum++;
                    currentLength++;
                }
                
                // 更新最大长度
                maxLength = Math.max(maxLength, currentLength);
            }
        }
        
        return maxLength;
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，每个元素最多被访问两次（一次检查是否为起点，一次在延伸序列时）
- **空间复杂度**：O(n)，存储所有元素到集合中

**背题技巧**：
- 记住关键判断条件：`!numSet.contains(num - 1)`，确保只对序列起始点进行延伸
- 该算法利用了"每个序列只有一个起点"的特性，避免了重复计算
- 对于"最长/最短连续序列"类问题，先考虑是否可以通过集合或哈希表优化查找

**相关变体**：
- **最长连续递增序列**（LeetCode #674）：数组有序版，简单遍历即可
- **最长递增子序列**（LeetCode #300）：经典动态规划问题，O(n²)或O(n log n)解法
- **连续数组**（LeetCode #525）：前缀和+哈希表寻找最长0和1相等的子数组

### 二、双指针类题目（4题）

#### 4. 移动零（LeetCode #283，简单）

```callout
block_type: callout
background_color: 4
border_color: 4
emoji_id: star
content: |
  **核心考点**：双指针技巧、原地数组操作  
  **解题关键**：快慢指针分离非零元素和零元素，最后填充零  
  **面试频率**：★★★★☆（数组操作与双指针结合的基础题）
```

**题目描述**：给定一个数组nums，编写一个函数将所有0移动到数组的末尾，同时保持非零元素的相对顺序[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)[[2]](https://blog.csdn.net/a131529/article/details/142311212)。

**解题思路**：
1. **双指针法**：
   - 慢指针（slow）：指向当前应该放置非零元素的位置
   - 快指针（fast）：遍历数组，寻找非零元素
   - 遍历结束后，将慢指针之后的位置全部填充为0

**Java代码实现**：

```java
class Solution {
    public void moveZeroes(int[] nums) {
        if (nums == null || nums.length == 0) {
            return;
        }
        
        // 慢指针：记录下一个非零元素应该放置的位置
        int slow = 0;
        
        // 快指针：遍历数组寻找非零元素
        for (int fast = 0; fast < nums.length; fast++) {
            // 如果找到非零元素，放到slow位置，并移动slow指针
            if (nums[fast] != 0) {
                nums[slow] = nums[fast];
                slow++;
            }
        }
        
        // 将slow指针之后的所有位置填充为0
        while (slow < nums.length) {
            nums[slow] = 0;
            slow++;
        }
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，只需两次遍历数组（一次移动非零元素，一次填充零）
- **空间复杂度**：O(1)，仅使用常数额外空间，实现原地操作

**背题技巧**：
- 双指针模板：`slow`指针跟踪"有效"位置，`fast`指针遍历整个数组
- 记住"先处理非零元素，再填充零"的两步操作流程
- 该技巧可推广到"将特定元素移到一端"的所有类似问题

**相关变体**：
- **移除元素**（LeetCode #27）：将等于val的元素移到末尾或直接删除
- **颜色分类**（LeetCode #75）：三指针法，将0、1、2排序
- **分隔数组**（LeetCode #912）：将数组分成两部分，左侧小于pivot，右侧大于等于

#### 5. 盛最多水的容器（LeetCode #11，中等）

```callout
block_type: callout
background_color: 4
border_color: 4
emoji_id: star
content: |
  **核心考点**：双指针贪心策略、面积计算  
  **解题关键**：左右指针向中间移动，优先移动高度较小的指针  
  **面试频率**：★★★★★（贪心算法与双指针结合的经典面试题）
```

**题目描述**：给定一个长度为n的整数数组height，有n条垂线，第i条线的两个端点是(i, 0)和(i, height[i])。找出其中的两条线，使得它们与x轴共同构成的容器可以容纳最多的水[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **暴力法**：枚举所有可能的两条线组合，计算面积并取最大值，O(n²)时间复杂度
2. **双指针法**：
   - 左右指针分别位于数组两端
   - 计算当前面积并更新最大值
   - 移动高度较小的指针（因为移动较高指针不可能增加面积，而移动较低指针可能获得更高高度）

**Java代码实现（双指针法）**：

```java
class Solution {
    public int maxArea(int[] height) {
        int maxArea = 0;
        // 左右双指针初始化为数组两端
        int left = 0, right = height.length - 1;
        
        while (left < right) {
            // 计算当前容器的宽度
            int width = right - left;
            // 容器高度由较短的线段决定
            int currentHeight = Math.min(height[left], height[right]);
            // 计算面积并更新最大面积
            int currentArea = width * currentHeight;
            maxArea = Math.max(maxArea, currentArea);
            
            // 移动高度较小的指针，寻找可能的更大面积
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxArea;
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，左右指针共移动n-1次
- **空间复杂度**：O(1)，仅使用常数额外空间

**背题技巧**：
- 记住核心公式：`面积 = 宽度 × 最小高度`
- 移动规则：`谁小移谁`（高度较小的指针），相等时移任意一个
- 该问题的贪心策略正确性证明：移动较高指针不可能获得更大面积，因此只能移动较低指针

**相关变体**：
- **接雨水**（LeetCode #42）：更复杂的雨水收集问题，双指针或单调栈解法
- **最大矩形**（LeetCode #85）：在矩阵中寻找最大矩形面积
- **直方图最大矩形面积**（LeetCode #84）：单调栈经典应用

#### 6. 三数之和（LeetCode #15，中等）

```callout
block_type: callout
background_color: 4
border_color: 4
emoji_id: star
content: |
  **核心考点**：排序+双指针、去重处理  
  **解题关键**：固定一个数后转化为两数之和问题，注意三重去重  
  **面试频率**：★★★★★（数组处理与双指针结合的高频面试题）
```

**题目描述**：给你一个包含n个整数的数组nums，判断nums中是否存在三个元素a，b，c，使得a + b + c = 0。请你找出所有和为0且不重复的三元组[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **排序预处理**：对数组排序，便于双指针操作和去重
2. **固定第一个数**：遍历数组，固定nums[i]作为三元组的第一个数
3. **双指针找两数**：左指针i+1，右指针n-1，寻找nums[left]+nums[right] = -nums[i]
4. **三重去重**：对i、left、right分别进行去重处理，避免重复三元组

**Java代码实现**：

```java
import java.util.*;

class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        if (nums == null || nums.length < 3) {
            return result;
        }
        
        // 对数组排序，便于双指针操作和去重
        Arrays.sort(nums);
        
        // 遍历数组，固定第一个数
        for (int i = 0; i < nums.length - 2; i++) {
            // 去重：如果当前数和前一个数相同，跳过
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            
            // 如果第一个数已经大于0，后面不可能有三数之和为0
            if (nums[i] > 0) {
                break;
            }
            
            // 左右双指针
            int left = i + 1;
            int right = nums.length - 1;
            
            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];
                
                if (sum == 0) {
                    // 找到符合条件的三元组
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    
                    // 去重：移动左指针到下一个不同的数
                    while (left < right && nums[left] == nums[left + 1]) {
                        left++;
                    }
                    
                    // 去重：移动右指针到上一个不同的数
                    while (left < right && nums[right] == nums[right - 1]) {
                        right--;
                    }
                    
                    // 更新指针，继续寻找
                    left++;
                    right--;
                } else if (sum < 0) {
                    // 和太小，移动左指针增大sum
                    left++;
                } else {
                    // 和太大，移动右指针减小sum
                    right--;
                }
            }
        }
        
        return result;
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n²)，排序O(n log n)，遍历+双指针O(n²)
- **空间复杂度**：O(log n) ~ O(n)，排序所需空间，取决于具体实现

**背题技巧**：
- 记住三数之和的标准流程：排序→固定一数→双指针找另外两数
- 三重去重是关键：i去重、left去重、right去重
- 边界条件：`nums[i] > 0`时直接break，因为排序后后面的数都更大

**相关变体**：
- **四数之和**（LeetCode #18）：固定两个数后用双指针
- **三数之和的多种可能**：如和为target而非0，或绝对值最小的三数之和
- **最接近的三数之和**（LeetCode #16）：类似思路，记录最接近target的和

#### 7. 接雨水（LeetCode #42，困难）

```callout
  **核心考点**：双指针动态规划、单调栈  
  **解题关键**：计算每个位置左右最大高度，取较小值减去当前高度  
  **面试频率**：★★★★★（高级双指针/单调栈技巧的代表性面试题）
```

**题目描述**：给定n个非负整数表示每个宽度为1的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **双指针法**：
   - 维护左右两个指针和左右最大高度
   - 比较左右最大高度，优先处理高度较小的一侧
   - 累加每个位置能接的雨水量：`min(leftMax, rightMax) - height[i]`

**Java代码实现（双指针法）**：

```java
class Solution {
    public int trap(int[] height) {
        if (height == null || height.length <= 2) {
            return 0;
        }
        
        int left = 0, right = height.length - 1;
        int leftMax = 0, rightMax = 0;
        int water = 0;
        
        while (left < right) {
            // 左侧高度较小，处理左侧
            if (height[left] < height[right]) {
                // 更新左侧最大高度
                if (height[left] >= leftMax) {
                    leftMax = height[left];
                } else {
                    // 当前位置能接的雨水
                    water += leftMax - height[left];
                }
                left++;
            } else {
                // 右侧高度较小或相等，处理右侧
                if (height[right] >= rightMax) {
                    rightMax = height[right];
                } else {
                    // 当前位置能接的雨水
                    water += rightMax - height[right];
                }
                right--;
            }
        }
        
        return water;
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，仅需一次遍历数组
- **空间复杂度**：O(1)，使用常数额外空间

**背题技巧**：
- 记住核心公式：`当前位置雨水 = min(左侧最大高度, 右侧最大高度) - 当前高度`
- 双指针法通过"谁小移谁"的策略，确保了`min(leftMax, rightMax)`的正确性
- 该问题还有动态规划解法（O(n)空间）和单调栈解法，可根据面试要求灵活选择

**相关变体**：
- **接雨水 II**（LeetCode #407）：二维矩阵接雨水，优先队列解法
- **直方图最大矩形面积**（LeetCode #84）：单调栈经典应用
- **最大矩形**（LeetCode #85）：在0-1矩阵中寻找最大矩形

### 三、滑动窗口类题目（2题）

#### 8. 无重复字符的最长子串（LeetCode #3，中等）

```callout
  **核心考点**：滑动窗口、哈希表优化  
  **解题关键**：维护窗口左右边界，用哈希表记录字符最近位置  
  **面试频率**：★★★★★（字符串处理与滑动窗口结合的必考题）
```

**题目描述**：给定一个字符串s，请你找出其中不含有重复字符的最长子串的长度[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **滑动窗口+哈希表**：
   - 右指针不断向右移动，将字符加入窗口
   - 当遇到重复字符时，左指针移动到重复字符的下一个位置（取max避免左指针左移）
   - 哈希表记录每个字符最后出现的位置

**Java代码实现**：

```java
import java.util.*;

class Solution {
    public int lengthOfLongestSubstring(String s) {
        if (s == null || s.length() == 0) {
            return 0;
        }
        
        Map<Character, Integer> charMap = new HashMap<>();
        int maxLength = 0;
        int left = 0;  // 窗口左边界
        
        for (int right = 0; right < s.length(); right++) {
            char currentChar = s.charAt(right);
            
            // 如果字符已存在且位置在当前窗口内，移动左指针到重复字符的下一位
            if (charMap.containsKey(currentChar) && charMap.get(currentChar) >= left) {
                left = charMap.get(currentChar) + 1;
            }
            
            // 更新字符最新位置
            charMap.put(currentChar, right);
            
            // 更新最大长度
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        return maxLength;
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，每个字符最多被访问两次（左右指针各一次）
- **空间复杂度**：O(min(m, n))，m为字符集大小，n为字符串长度

**背题技巧**：
- 记住关键判断条件：`charMap.containsKey(currentChar) && charMap.get(currentChar) >= left`
- 左指针更新公式：`left = max(left, charMap.get(currentChar) + 1)`
- 该技巧适用于所有"寻找最长/最短无重复子串"类问题

**相关变体**：
- **至多包含两个不同字符的最长子串**（LeetCode #159）：扩展为允许两个重复字符
- **至多包含K个不同字符的最长子串**（LeetCode #340）：通用化滑动窗口问题
- **长度最小的子数组**（LeetCode #209）：滑动窗口寻找和大于等于target的最小长度

#### 9. 找到字符串中所有字母异位词（LeetCode #438，中等）

```callout
block_type: callout
background_color: 4
border_color: 4
emoji_id: star
content: |
  **核心考点**：固定窗口滑动、字符计数比较  
  **解题关键**：用计数数组记录窗口内字符频率，与目标比较  
  **面试频率**：★★★☆☆（滑动窗口与字符匹配结合的典型问题）
```

**题目描述**：给定两个字符串s和p，找到s中所有p的异位词的子串，返回这些子串的起始索引[[1]](https://blog.csdn.net/xiaofeng10330111/article/details/141401712)。

**解题思路**：
1. **计数数组法**：
   - 统计p中各字符的频率，作为目标计数
   - 在s上滑动固定大小的窗口（p的长度），维护窗口内字符计数
   - 比较窗口计数与目标计数，相等则记录起始索引

**Java代码实现**：

```java
import java.util.*;

class Solution {
    public List<Integer> findAnagrams(String s, String p) {
        List<Integer> result = new ArrayList<>();
        if (s == null || p == null || s.length() < p.length()) {
            return result;
        }
        
        int sLen = s.length();
        int pLen = p.length();
        
        // 创建计数数组，记录26个字母的频率
        int[] targetCount = new int[26];
        int[] windowCount = new int[26];
        
        // 初始化p的计数和s初始窗口的计数
        for (int i = 0; i < pLen; i++) {
            targetCount[p.charAt(i) - 'a']++;
            windowCount[s.charAt(i) - 'a']++;
        }
        
        // 检查初始窗口是否匹配
        if (matches(targetCount, windowCount)) {
            result.add(0);
        }
        
        // 滑动窗口遍历s
        for (int i = pLen; i < sLen; i++) {
            // 窗口右移：移除左侧字符，添加右侧字符
            windowCount[s.charAt(i - pLen) - 'a']--;
            windowCount[s.charAt(i) - 'a']++;
            
            // 检查当前窗口是否匹配
            if (matches(targetCount, windowCount)) {
                result.add(i - pLen + 1);
            }
        }
        
        return result;
    }
    
    // 比较两个计数数组是否相等
    private boolean matches(int[] arr1, int[] arr2) {
        for (int i = 0; i < 26; i++) {
            if (arr1[i] != arr2[i]) {
                return false;
            }
        }
        return true;
    }
}
```

**复杂度分析**：
- **时间复杂度**：O(n)，n为s的长度，每个字符处理一次，比较计数数组O(26)为常数
- **空间复杂度**：O(1)，使用固定大小的计数数组（26个元素）

**背题技巧**：
- 固定窗口大小的滑动窗口问题，窗口大小等于p的长度
- 计数数组比较是异位词判断的高效方法，比排序法O(k log k)更优
- 窗口移动时只需更新边界字符的计数，避免重复计算

**相关变体**：
- **最小覆盖子串**（LeetCode #76）：不定长滑动窗口，寻找包含所有字符的最小窗口
- **字符串的排列**（LeetCode #567）：判断s2是否包含s1的排列，与本题几乎相同
- **子串的变体**：如允许一个字符替换的最长重复子串等

```callout
  **文档说明**：本文档已完成哈希表类（3题）、双指针类（4题）和滑动窗口类（2题）共9道题目的详解。后续章节将继续覆盖链表类（14题）、二叉树类（17题）、动态规划类（10题）及其他类型题目。代码实现均经过验证，解题思路注重原理与技巧结合，适合算法学习与面试准备使用。
```