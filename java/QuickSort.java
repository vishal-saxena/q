package com.ds.algo.sort;

import java.util.Arrays;

public class QuickSort {
  public static void main(String[] args) {
    String[] a = new String[]{"Q", "U", "I", "C", "K", "S", "O", "R", "T", "E", "X", "A", "M", "P",
        "L", "E"};
    sort(a);
  }

  private static void sort(String[] a) {
    sort(a, 0, a.length -1);
  }

  private static void sort(String[] a, int lo, int hi) {
    int p = pivot(a, lo, hi);
    sort(a,0,p);
    sort(a,p,a.length -1);
  }

  private static int pivot(String[] a, int lo, int hi) {
    int p = lo;
    int left = lo+1;
    int right = hi;
    while(true){

      while (a[left].compareTo(a[p]) <=0){
        left++;
        if(left ==right)
          break; //markers equal
      }

      while(a[right].compareTo(a[p])>0){
        right--;
        if(right==left)
          break; //markers equal
      }

      //swap marker elements
      String swap = a[left];
      a[left]=a[right];
      a[right]=swap;
      //left was greater than pivot and hence was swapped, no need to check again
      left++;
      //right was less than pivot and hence was swapped, no need to check again
      right--;

      if(left==right) {
        break; //markers equal, this is the in place position of a[p]
      }
    }

    System.out.println(String.format("%s: \n %s", lo, Arrays.toString(a)));
    return lo;
  }
}
