from typing import List


class Solution:
    def meg(nums1: int, nums2: int):
        res=[]
        n=len(nums1)-1
        m=len(nums2)-1
        p=m+n-1
        while n>=0 and m>=0:
            if nums1[n]>nums2[m]:
                nums1[p]=nums1[n]
                n-=1
            else:
                nums1[p]=nums2[m]
                m-=1
            p-=1
        while m>0:
            nums1[p]=nums2[m]
            p-=1
            m-=1
        return nums1


