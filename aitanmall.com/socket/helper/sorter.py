def merge(array, left, midpoint, right):
    n1 = midpoint - left + 1
    n2 = right - midpoint
 
    # create temp arrays
    left_temp = [0] * (n1)
    right_temp = [0] * (n2)
 
    # Copy data to temp arrays L[] and R[]
    for i in range(0, n1):
        left_temp[i] = array[left + i]
 
    for j in range(0, n2):
        right_temp[j] = array[midpoint + 1 + j]
 
    # Merge the temp arrays back into arr[l..r]
    i = 0     # Initial index of first subarray
    j = 0     # Initial index of second subarray
    k = left     # Initial index of merged subarray
 
    while i < n1 and j < n2:
        if left_temp[i] <= right_temp[j]:
            array[k] = left_temp[i]
            i += 1
        else:
            array[k] = right_temp[j]
            j += 1
        k += 1
 
    # Copy the remaining elements of L[], if there
    # are any
    while i < n1:
        array[k] = left_temp[i]
        i += 1
        k += 1
 
    # Copy the remaining elements of R[], if there
    # are any
    while j < n2:
        array[k] = right_temp[j]
        j += 1
        k += 1
 
# l is for left index and r is right index of the
# sub-array of arr to be sorted
 
 
def mergeSort(arr, l, r):
    if l < r:
 
        # Same as (l+r)//2, but avoids overflow for
        # large l and h
        m = l+(r-l)//2
 
        # Sort first and second halves
        mergeSort(arr, l, m)
        mergeSort(arr, m+1, r)
        merge(arr, l, m, r)