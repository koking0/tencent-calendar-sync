# tencent-calendar-sync

自动将腾讯会议日程同步到 GitHub，生成 `all.ics` 供 Google 日历订阅。

## 工作原理

GitHub Actions 每 30 分钟运行一次，通过 vdirsyncer 从腾讯会议 CalDAV 拉取日程，合并为 `all.ics` 提交到仓库。

## 配置

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 值 |
|--------|-----|
| `CALDAV_USER` | `Cal_ywihek8d2f@cal.meeting.tencent.com` |
| `CALDAV_PASS` | 腾讯会议 CalDAV 密码 |

## 订阅地址

`all.ics` 生成后，可通过 raw 链接在 Google 日历中订阅：

```
https://raw.githubusercontent.com/koking0/tencent-calendar-sync/main/all.ics
```

> 注意：私有仓库的 raw 链接需要带 token 才能访问，Google 日历订阅建议改用 GitHub Pages 或 Actions 推送到公开端点。
