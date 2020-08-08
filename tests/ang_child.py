#!/bin/python3

import math
import os
import random
import re
import sys

# Complete the angryChildren function below.
def angryChildren(kchild, packets):
    # packets = sorted(packets)
    # print("packets", packets)
    # min_l = None
    # min_diff = float("inf")
    # for i, v in enumerate(packets):
    #     last = i+k - 1
    #     if last > len(packets) - 1:
    #         continue
    #     v2 = packets[last]
    #     diff = v2 - v
    #     print(packets)
    #     sub = packets[i:i+k]
    #     print(sub)
    #     print(i, v, v2, diff)
    #     if diff < min_diff:
    #         min_diff = diff
    #         min_l = sub
    # print(min_l)

    # abs_diff = 0
    # for i, x in enumerate(min_l):
    #     for j in range(i + 1, len(min_l)):
    #         y = min_l[j]
    #         abs_diff = abs_diff + abs(y-x)

    
    # previous_first_sum = 0
    # previous_sum = 0
    # previous_sums = {}
    # for i, x in enumerate(packets):
    #     previous_sums[i] = 0
    #     curr_first_sum = 0
    #     if i + kchild >= len(packets) - 1:
    #         break
    #     sub_last_idx = i + kchild - 1
    #     sub = packets[i:sub_last_idx + 1]
    #     print("sub", sub, i, sub_last_idx)
    #     print("previous first sum", previous_first_sum)
    #     current_sum = 0
    #     if i == 0:
    #         print("i == 0")
    #         for j, y in enumerate(sub):
    #             print("j", j)
    #             for z in sub[j+1:]:
    #                 print("y, z", y, z)
    #                 diff = abs(y-z)
    #                 if j == 0:
    #                     curr_first_sum = curr_first_sum + diff
    #                 current_sum = current_sum + diff
    #     else:
    #         current_sum = previous_sum - previous_first_sum
    #         print("current sum start", current_sum, previous_sum, previous_first_sum)
    #         for j, v in enumerate(sub):
    #             if j == len(sub) - 1:
    #                 break
    #             v2 = sub[-1]
    #             print("v, v2", v, v2)
    #             diff = abs(v - v2)
    #             if j == 0:
    #                 curr_first_sum = curr_first_sum + diff
    #             current_sum = current_sum + diff
    #     print("current first sum", curr_first_sum)
    #     previous_first_sum = curr_first_sum
    #     print(sub, current_sum)
    #     if min_diff > current_sum:
    #         min_diff = current_sum
    #     previous_sum = current_sum
    packets = sorted(packets)
    # print(packets)
    diffs_sum = {}
    min_diff = float("inf")
    prev_sum = 0
    for i, x in enumerate(packets[:len(packets) - kchild + 1]):
        sub = packets[i:i+kchild]
        # print(sub)

        # print("prev sum", prev_sum, diffs_sum[i-1] if i != 0 else "-1")
        curr_sum = 0 if i == 0 else prev_sum - diffs_sum[i-1]
        # print("new curr sum", curr_sum)

        for j, y in enumerate(sub):
            if i+j not in diffs_sum:
                diffs_sum[i+j] = 0
            if i == 0:
                for k, z in enumerate(sub[j+1:]):
                    # print("y, z", y, z, i, j, k)
                    diff = abs(y-z)
                    diffs_sum[i+j] = diffs_sum[i+j] + diff
                    # print(diffs_sum)
                    curr_sum = curr_sum + diff
            else:
                if j == len(sub) - 1:
                    continue
                # print("y, end", y, sub[-1])
                diff = abs(y-sub[-1])
                diffs_sum[i+j] = diffs_sum[i+j] + diff
                curr_sum = curr_sum + diff
        prev_sum = curr_sum
        # print("curr sum", prev_sum)
        # print("diffs_sum", diffs_sum)
        min_diff = min(min_diff, curr_sum)
    return min_diff

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input())

    k = int(input())

    packets = []

    for _ in range(n):
        packets_item = int(input())
        packets.append(packets_item)

    result = angryChildren(k, packets)

    fptr.write(str(result) + '\n')

    fptr.close()

# Complete the angryChildren function below.
def angryChildren(k, packets):
    packets.sort()
    min_diff = 0
    first = packets[:k]
    for i, v in enumerate(first):
        for j, w in enumerate(first[i+1:]):
            min_diff = min_diff + abs(v - w)
    print(packets)
    for i in range(1, len(packets) - k + 1):
        curr = 2 * sum(packets[i:i+k-1]) + (k-1) * (packets[i+k-1] - packets[i-1])
        # print(i, packets[i:i+k], curr, k, len(packets)-k-1)
        print(i, packets[i:i+k-1])
        min_diff = min(curr, min_diff)
    return min_diff