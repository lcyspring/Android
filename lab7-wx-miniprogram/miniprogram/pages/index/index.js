import { floor } from '../../config/config.default';
import * as api from '../../utils/api';
import { AD_UNIT } from '../../config/index';

const limit = 20;
let tabsIndex = 0;
let floorIndex = 0;
let interstitialAd = null;

Page({

  data: {
    tabList: [{
      name: '当前未处理',
      status: '未处理'
    }, {
      name: '当前已处理',
      status: '已处理'
    }],
    floorList: floor,
    applyData: [],
  },

  onLoad: function (options) {
    this.getOpenid();
    this.onShareMessage();
    this.getApplyData();
    // 配置了插屏广告 ID 时才创建
    if (AD_UNIT.interstitial && wx.createInterstitialAd) {
      interstitialAd = wx.createInterstitialAd({ adUnitId: AD_UNIT.interstitial });
      interstitialAd.onLoad(() => {});
      interstitialAd.onError((err) => {});
      interstitialAd.onClose(() => {});
    }
    if (options.id === 'success' && interstitialAd) {
      interstitialAd.show().catch((err) => console.error(err));
    }
  },

  onShareAppMessage: function () {
    return {
      title: this.data.shareData.title,
      path: this.data.shareData.path,
      imageUrl: this.data.shareData.imageUrl,
      success: res => console.log(res),
      fail: err => console.log(err)
    }
  },

  /* 触底刷新 */
  onReachBottom: function () {
    !this.data.isEndOfList && this.getApplyData();
  },

  /* 选择状态 */
  selectStatus(e) {
    const { index } = e.detail;
    tabsIndex = index;
    this.setData({ applyData: [] });
    this.getApplyData();
    if (interstitialAd) {
      interstitialAd.show().catch((err) => console.error(err));
    }
  },

  /* 选择栋数 */
  selectFloor(e) {
    const { index } = e.detail;
    floorIndex = index;
    if (index === 0) {
      this.setData({ applyData: [] });
      this.getApplyData();
    } else {
      this.getApplyDataItem(floorIndex);
    }
  },

  /* 获取申报数据 */
  async getApplyData() {
    wx.showLoading({ title: '加载中...', mask: true });
    try {
      const res = await api.getApplyList({
        status: this.data.tabList[tabsIndex].status,
        floor: floorIndex === 0 ? null : floorIndex,
        skip: this.data.applyData.length,
        limit
      });
      const merged = [...this.data.applyData, ...(res.data || [])];
      this.setData({
        applyData: merged,
        isEndOfList: (res.data || []).length < limit
      });
    } catch (err) {
      console.warn('[index.getApplyData] 失败:', err);
      wx.showToast({ title: '加载失败，请下拉重试', icon: 'none' });
    }
    wx.hideLoading();
  },

  /* 选择栋数获取申报数据 */
  async getApplyDataItem(floor) {
    wx.showLoading({ title: '加载中...', mask: true });
    try {
      const res = await api.getApplyList({
        floor,
        status: this.data.tabList[tabsIndex].status,
        limit: 100
      });
      this.setData({ applyData: res.data || [] });
    } catch (err) {
      console.warn('[index.getApplyDataItem] 失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
    wx.hideLoading();
  },

  /* 跳转申报页 */
  toPublish() {
    wx.navigateTo({ url: '../publish/publish' });
  },

  /* 跳转管理页 */
  toAdmin() {
    if (this.data.isAdmin) {
      wx.navigateTo({ url: '../admin/admin' });
    } else {
      wx.showToast({ title: '暂无权限', icon: 'error', duration: 1000 });
    }
  },

  /* 获取用户的 openid */
  getOpenid() {
    api.login().then(res => {
      console.log("openid:", res.result.openid);
      this.getUserRole(res.result.openid);
      this.setData({ openid: res.result.openid });
    }).catch(err => console.log(err));
  },

  /* 获取角色列表 */
  getUserRole(openid) {
    api.getRoleList().then(res => {
      const openidList = res.data.map((item) => {
        if (item.role === '超级管理员') {
          wx.setStorageSync('admin', item);
        }
        return item.openid;
      });
      this.setData({ isAdmin: openidList.includes(openid) });
    });
  },

  /* 查看申报表 */
  navDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: '../detail/detail?id=' + id });
  },

  /* 获取分享数据 */
  onShareMessage() {
    api.getShareConfig().then(res => {
      this.setData({ shareData: res.data[0] });
    });
  },

})
