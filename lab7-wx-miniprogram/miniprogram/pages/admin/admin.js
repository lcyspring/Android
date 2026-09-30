import { floor } from '../../config/config.default';
import * as api from '../../utils/api';
import { SUBSCRIBE_TEMPLATE } from '../../config/index';

const limit = 20;
let tabsIndex = 0;
let floorIndex = 0;

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
    applyData: []
  },

  onLoad: function () {
    this.getApplyData();
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
      this.setData({
        applyData: [...this.data.applyData, ...(res.data || [])],
        isEndOfList: (res.data || []).length < limit
      });
    } catch (err) {
      console.warn('[admin.getApplyData] 失败:', err);
      wx.showToast({ title: '加载失败，请重试', icon: 'none' });
    }
    wx.hideLoading();
  },

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
      console.warn('[admin.getApplyDataItem] 失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
    wx.hideLoading();
  },

  /* 更新申请状态 */
  updateApplyStatus(e) {
    const { id, index } = e.currentTarget.dataset;
    wx.showModal({
      title: '温馨提示',
      content: '确认此申报数据？',
      success: async (res) => {
        if (res.confirm) {
          // 请求订阅消息权限（给报修人发处理通知）
          wx.requestSubscribeMessage({
            tmplIds: [SUBSCRIBE_TEMPLATE.handleNotice],
            fail: () => {}
          });
          this.setData({ applyDataItem: this.data.applyData[index] });
          wx.showLoading({ title: '处理中...', mask: true });
          try {
            await api.updateApplyStatus(id, '已处理');
            this.setData({ applyData: [] });
            this.getApplyData();
            wx.hideLoading();
            wx.showToast({ title: '处理成功', duration: 500 });
            this.sendHandleNotice();
          } catch (err) {
            wx.hideLoading();
            console.warn('[admin.updateApplyStatus] 失败:', err);
            wx.showToast({ title: '处理失败，请重试', icon: 'error' });
          }
        }
      }
    });
  },

  /* 删除申报数据 */
  deleteApplyData(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '温馨提示',
      content: '确认删除此申报数据？',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...', mask: true });
          try {
            await api.removeApply(id);
            this.setData({ applyData: [] });
            this.getApplyData();
            wx.hideLoading();
            wx.showToast({ title: '删除成功', duration: 500 });
          } catch (err) {
            wx.hideLoading();
            console.warn('[admin.deleteApplyData] 失败:', err);
            wx.showToast({ title: '删除失败，请重试', icon: 'error' });
          }
        }
      }
    });
  },

  /* 发送处理通知 */
  sendHandleNotice() {
    const admin = wx.getStorageSync('admin');
    api.sendHandleNotice({
      name: admin.name,
      dorm: this.data.applyDataItem.location + ' ' + this.data.applyDataItem.floor + '栋' + this.data.applyDataItem.dorm,
      phone: admin.phone,
      status: '已处理',
      remarks: '祝您生活愉快!',
      openid: this.data.applyDataItem._openid,
      templateId: SUBSCRIBE_TEMPLATE.handleNotice
    }).then(res => console.log(res));
  },

  /* 查看申报表 */
  navDetail(e) {
    const { id, admin } = e.currentTarget.dataset;
    wx.navigateTo({ url: '../detail/detail?id=' + id + '&admin=' + admin });
  },

})
