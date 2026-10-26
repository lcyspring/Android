import { floor } from '../../config/config.default';
import * as api from '../../utils/api';
import { AD_UNIT } from '../../config/index';

const limit = 20;
let tabsIndex = 0;
let floorIndex = 0;
let interstitialAd = null;

/** 各角色的标签页（不同角色只关心各自的状态） */
const TAB_LIST = {
  '超级管理员': [
    { name: '待审核', status: '未处理' },
    { name: '已确认', status: '已确认' },
    { name: '不受理', status: '不受理' },
    { name: '已完成', status: '已处理' }
  ],
  '维修人员': [
    { name: '待维修', status: '已确认' },
    { name: '已完成', status: '已处理' }
  ],
  '普通用户': [
    { name: '我的列表', status: '' },
    { name: '已完成', status: '已处理' }
  ]
};

/** 审核状态 → 标签颜色 */
const STATUS_COLOR = {
  '未处理': '#ff976a',
  '已确认': '#1989fa',
  '不受理': '#ee0a24',
  '已处理': '#07c160'
};

Page({

  data: {
    tabList: TAB_LIST['普通用户'],
    floorList: floor,
    applyData: [],
    userInfo: null,
    isAdmin: false,
    isWorker: false
  },

  onLoad: function (options) {
    // 登录态校验：未登录先跳转登录页
    const session = api.getSession();
    if (!session) {
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    const role = session.role || '普通用户';
    tabsIndex = 0;
    floorIndex = 0;
    this.setData({
      userInfo: session,
      isAdmin: role === '超级管理员',
      isWorker: role === '维修人员',
      tabList: TAB_LIST[role] || TAB_LIST['普通用户']
    });
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

  /* 从「上传维修情况」页返回后刷新列表 */
  onShow() {
    if (this._needRefresh) {
      this._needRefresh = false;
      this.setData({ applyData: [] });
      this.getApplyData();
    }
  },

  onShareAppMessage: function () {
    const shareData = this.data.shareData || {};
    return {
      title: shareData.title || '校园报修助手，随手提交、即时跟进',
      path: shareData.path || 'pages/index/index',
      imageUrl: shareData.imageUrl || '',
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

  /* 选择栋数（仅管理员显示筛选器） */
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

  /* 数据可见范围：管理员看全部；维修人员看指派给自己的；普通用户只看自己宿舍 */
  buildScope() {
    const { isAdmin, isWorker, userInfo } = this.data;
    if (isAdmin) {
      return { floor: floorIndex === 0 ? null : floorIndex, dorm: null, workerName: null };
    }
    if (isWorker) {
      return { floor: null, dorm: null, workerName: (userInfo && userInfo.name) || '__none__' };
    }
    return {
      floor: (userInfo && userInfo.floor) || null,
      // 未配置宿舍时用不存在的值兜底，保证普通用户不会看到全量数据
      dorm: (userInfo && userInfo.dorm) || '__none__',
      workerName: null
    };
  },

  /* 给列表项补充状态颜色，供 WXML 直接绑定 */
  decorateApply(list) {
    return (list || []).map(item => ({
      ...item,
      statusColor: STATUS_COLOR[item.status] || '#999999'
    }));
  },

  /* 获取申报数据 */
  async getApplyData() {
    wx.showLoading({ title: '加载中...', mask: true });
    const scope = this.buildScope();
    try {
      const res = await api.getApplyList({
        status: this.data.tabList[tabsIndex].status,
        floor: scope.floor,
        dorm: scope.dorm,
        workerName: scope.workerName,
        skip: this.data.applyData.length,
        limit
      });
      const merged = this.decorateApply([...this.data.applyData, ...(res.data || [])]);
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
      this.setData({ applyData: this.decorateApply(res.data) });
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

  /* 维修人员：上传维修情况 */
  toRepair(e) {
    const { id } = e.currentTarget.dataset;
    this._needRefresh = true;
    wx.navigateTo({ url: '../repair/repair?id=' + id });
  },

  /* 退出登录 */
  logout() {
    wx.showModal({
      title: '温馨提示',
      content: '确认退出当前账号？',
      success: (res) => {
        if (res.confirm) {
          api.clearSession();
          wx.reLaunch({ url: '/pages/login/login' });
        }
      }
    });
  },

  /* 切换账号 */
  toLogin() {
    wx.reLaunch({ url: '/pages/login/login' });
  },

  /* 查看申报表 */
  navDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: '../detail/detail?id=' + id + '&admin=' + this.data.isAdmin });
  },

  /* 获取分享数据 */
  onShareMessage() {
    api.getShareConfig().then(res => {
      this.setData({ shareData: res.data[0] });
    });
  },

})
