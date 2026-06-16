#!/usr/bin/env python3
"""
merge.py - 合并多个 .ics 文件为一个标准 VCALENDAR
用法: python3 merge.py file1.ics file2.ics ... > all.ics
"""

import sys
import re

def parse_ics(content):
    """提取 ics 文件中所有 VEVENT 块"""
    events = []
    # 处理行续接（RFC 5545: 以空格或Tab开头的行是上一行的续接）
    content = re.sub(r'\r?\n[ \t]', '', content)
    in_event = False
    current = []
    for line in content.splitlines():
        if line.strip() == 'BEGIN:VEVENT':
            in_event = True
            current = [line]
        elif line.strip() == 'END:VEVENT':
            current.append(line)
            events.append('\r\n'.join(current))
            in_event = False
            current = []
        elif in_event:
            current.append(line)
    return events

def main():
    if len(sys.argv) < 2:
        print("Usage: merge.py file1.ics [file2.ics ...] > all.ics", file=sys.stderr)
        sys.exit(1)

    all_events = []
    seen_uids = set()

    for path in sys.argv[1:]:
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            events = parse_ics(content)
            for ev in events:
                # 提取 UID 去重
                uid_match = re.search(r'^UID:(.+)$', ev, re.MULTILINE)
                uid = uid_match.group(1).strip() if uid_match else None
                if uid and uid in seen_uids:
                    continue
                if uid:
                    seen_uids.add(uid)
                all_events.append(ev)
        except Exception as e:
            print(f"Warning: failed to read {path}: {e}", file=sys.stderr)

    # 输出合并后的 VCALENDAR
    output = []
    output.append("BEGIN:VCALENDAR")
    output.append("VERSION:2.0")
    output.append("PRODID:-//tencent-calendar-sync//merge.py//EN")
    output.append("CALSCALE:GREGORIAN")
    output.append("METHOD:PUBLISH")
    for ev in all_events:
        output.append(ev)
    output.append("END:VCALENDAR")

    print('\r\n'.join(output))
    print(f"Merged {len(all_events)} events from {len(sys.argv)-1} files.", file=sys.stderr)

if __name__ == '__main__':
    main()
