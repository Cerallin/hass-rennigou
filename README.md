## 任你购 homeassistant 集成

This is a hass integration for [Rennigou(Anybuy)](https://rennigou.jp).

### 功能

- 本日汇率
- 获取订单信息

### 安装

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

打开HACS设置并添加本repo (https://github.com/Cerallin/hass-rennigou) 为一个自定义集成（分类要选**Integration**）

## 配置

设备与服务 -> 集成 -> 添加集成 (按钮) -> 搜索 rennigou

之后填写用户名和密码即可。

**注** 不知为何不显示提示词，也就是“用户名/密码”。但总之上边是用户名下面是密码。

## 例子

例如你可以定义一个Markdown卡片如下：
```yaml
type: markdown
title: 任你购Go
content: |-
  {% set packages = states.sensor.YOUR_SENSOR_NAME.attributes.orders %}

  {% for package in packages %}
    <img src="{{ package.image_link }}" width="100px">

    {{ package.title }}

    {{ package.updated_at | as_local }}
  {% endfor %}
```

## TODO

- [ ] 修复用户名密码不显示的问题
- [ ] 获取待收货包裹物流号
- [ ] 提供选项：自动注册待收货包裹为实体
- [x] 根据包裹状态自动分类
- [ ] 在homeassistant的brand repo注册任你购的Logo
- [ ] 发布到HACS