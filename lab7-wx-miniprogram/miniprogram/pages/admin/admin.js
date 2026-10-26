import { floor } from '../../config/config.default';
import * as api from '../../utils/api';
import { SUBSCRIBE_TEMPLATE } from '../../config/index';

const limit = 20;
let tabsIndex = 0;
let floorIndex = 0;

/** 审核状态 → 标签颜色 */
const STATUS_COLOR = {
  '未处理': '#ff976a',
  '已确认': '#1989fa',
  '不受理': '#ee0a24',
  '已处理': '#07c160'
};

Page({

  data: {
    tabList: [
      { name: '待审核', status: '未处理' },
      { name: '已确认', status: '已确认' },
      { name: '不受理', status: '不受理' },
      { name: '已完成', status: '已处理' }
    ],
    floorList: floor,
    applyData: [],
    userInfo: null
  },

  onLoad: function () {
    // 权限守卫：仅超级管理员可进入，否则回登录页
    const session = api.getSession();
    if (!session || session.role !== '超级管理员') {
      wx.showToast({ title: '请先以管理员账号登录', icon: 'none' });
      setTimeout(() => wx.reLaunch({ url: '/pages/login/login' }), 900);
      return;
    }
    tabsIndex = 0;
    floorIndex = 0;
    this.setData({ userInfo: session });
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

  /* 给列表项补充状态颜色 */
  decorateApply(list) {
    return (list || []).map(item => ({
      ...item,
      statusColor: STATUS_COLOR[item.status] || '#999999'
    }));
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
        applyData: this.decorateApply([...this.data.applyData, ...(res.data || [])]),
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
      this.setData({ applyData: this.decorateApply(res.data) });
    } catch (err) {
      console.warn('[admin.getApplyDataItem] 失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
    wx.hideLoading();
  },

  /* 审核通过：从维修人员中选一位并指派（状态 → 已确认） */
  async confirmApply(e) {
    const { id, index } = e.currentTarget.dataset;
    let workers = [];
    try {
      const res = await api.getRoleList();
      workers = (res.data || []).filter(r => r.role === '维修人员');
    } catch (err) {
      console.warn('[admin.confirmApply] 获取维修人员失败:', err);
    }
    if (!workers.length) {
      wx.showToast({ title: '暂无维修人员账号', icon: 'none' });
      return;
    }
    wx.showActionSheet({
      itemList: workers.map(w => w.name + '（' + w.phone + '）'),
      success: (res) => this.doConfirm(id, index, workers[res.tapIndex])
    });
  },

  async doConfirm(id, index, worker) {
    wx.showLoading({ title: '处理中...', mask: true });
    try {
      await api.confirmApply(id, worker);
      this.setData({ applyDataItem: this.data.applyData[index] });
      this.setData({ applyData: [] });
      this.getApplyData();
      wx.hideLoading();
      wx.showToast({ title: '已确认，已指派 ' + worker.name, icon: 'none' });
      this.requestNotice();
      this.sendNotice('已确认');
    } catch (err) {
      wx.hideLoading();
      console.warn('[admin.doConfirm] 失败:', err);
      wx.showToast({ title: '操作失败，请重试', icon: 'error' });
    }
  },

  /* 不受理：填写原因（状态 → 不受理） */
  rejectApply(e) {
    const { id, index } = e.currentTarget.dataset;
    wx.showModal({
      title: '填写不受理原因',
      editable: true,
      placeholderText: '请输入不受理原因',
      success: async (res) => {
        if (!res.confirm) return;
        const reason = (res.content || '').trim();
        if (!reason) {
          wx.showToast({ title: '请填写不受理原因', icon: 'none' });
          return;
        }
        wx.showLoading({ title: '处理中...', mask: true });
        try {
          await api.rejectApply(id, reason);
          this.setData({ applyDataItem: { ...this.data.applyData[index], rejectReason: reason } });
          this.setData({ applyData: [] });
          this.getApplyData();
          wx.hideLoading();
          wx.showToast({ title: '已标记不受理', icon: 'none' });
          this.requestNotice();
          this.sendNotice('不受理');
        } catch (err) {
          wx.hideLoading();
          console.warn('[admin.rejectApply] 失败:', err);
          wx.showToast({ title: '操作失败，请重试', icon: 'error' });
        }
      }
    });
  },

  /* 删除申报数据（已处理 / 不受理可删） */
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

  /* 申请订阅消息权限（失败不影响主流程） */
  requestNotice() {
    wx.requestSubscribeMessage({
      tmplIds: [SUBSCRIBE_TEMPLATE.handleNotice],
      fail: () => {}
    });
  },

  /* 给报修人发送状态通知（本地兜底会跳过） */
  sendNotice(status) {
    const admin = wx.getStorageSync('admin') || wx.getStorageSync('userInfo') || {};
    const item = this.data.applyDataItem || {};
    api.sendHandleNotice({
      name: admin.name,
      dorm: item.location + ' ' + item.floor + '栋' + item.dorm,
      phone: admin.phone,
      status,
      remarks: item.rejectReason || '祝您生活愉快!',
      openid: item._openid,
      templateId: SUBSCRIBE_TEMPLATE.handleNotice
    }).then(res => console.log(res)).catch(err => console.log(err));
  },

  /* 查看申报表 */
  navDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: '../detail/detail?id=' + id + '&admin=' + true });
  },

})
