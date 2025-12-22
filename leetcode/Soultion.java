class Soultion{
    public int maxsub(int nums[]){
        int n=nums.length;
        if(n==0)return 0;
        int maxSum=nums[0];
        int currentMax=nums[0];
        for(int i=1;i<n;i++){
           currentMax=Math.max(nums[i],currentMax+nums[i]);
           maxSum=Math.max(currentMax,maxSum);
        }
        return maxSum;
    }

    public int rob(int nums[]){
        int prev

    }


}