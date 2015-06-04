public final class Increment1 {
    public static void main (String [] args)
    {
        int i = 0;
        int arr[] = {0,1,2,3,4,5,6,7,8,9};
        System.out.println(arr[i]);
        System.out.println(arr[i++]);
        System.out.println(arr[++i]);
        System.out.println(arr[--i]);
        System.out.println(arr[i--]);
    }
}
