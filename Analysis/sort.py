#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sys import stdin
l = []

for line in stdin:
    try:
        r = line.strip().split()
        w = r[0]
        c = int(r[1])
        l.append((w, c))
    except Exception as e:
        print(line, e)
l.sort(key=lambda x: x[1], reverse=True)
print(*l, sep='\n')
