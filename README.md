## 任你购 homeassistant 集成

This is a hass integration for [Rennigou(Anybuy)](https://rennigou.jp).

### 功能

- 本日汇率
- 获取订单信息

### 安装

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

打开HACS设置并添加本repo (https://github.com/Cerallin/hass-rennigou) 为一个自定义集成（分类要选**Integration**）

你也可以点击下方按钮一键安装：
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&repository=hass-rennigou&owner=Cerallin)

## 配置

> [⚙️ 配置](https://my.home-assistant.io/redirect/config) > 设备与服务 > [🧩 集成](https://my.home-assistant.io/redirect/integrations) > [➕ 添加集成](https://my.home-assistant.io/redirect/config_flow_start?domain=rennigou) > 🔍 搜索 [`rennigou`](https://my.home-assistant.io/redirect/config_flow_start?domain=rennigou)


之后填写**用户名**和**密码**即可。

**注** 不知为何不显示提示词，也就是“用户名/密码”。但总之上边是用户名下面是密码。

## 例子

例如你可以定义一个[list-card](https://github.com/iantrich/list-card)卡片如下：
```yaml
type: custom:list-card
title: 待收货
entity: sensor.ren_ni_gou_awaiting_delivery
feed_attribute: orders
columns:
  - title: ''
    type: image
    field: image_link
    width: auto
    height: 150
    style:
      - text-align: center
  - title: 名称
    field: title
    style:
      - text-align: left
  - title: 状态
    field: status
    style:
      - text-align: center
  - title: 源站
    field: source_site
    style:
      - text-align: center
  - title: 更新时间
    field: updated_at
    style:
      - text-align: center
  - title: 类型
    field: type
    style:
      - text-align: center
```

## TODO

- [ ] 修复用户名密码不显示的问题
- [ ] 获取待收货包裹物流号
- [ ] 提供选项：自动注册待收货包裹为实体
- [x] 根据包裹状态自动分类
- [x] 在homeassistant的brand repo注册任你购的Logo
- [ ] 发布到HACS