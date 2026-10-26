import * as api from '../../utils/api';

/** 审核状态 → 标签颜色 */
const STATUS_COLOR = {
  '未处理': '#ff976a',
  '已确认': '#1989fa',
  '不受理': '#ee0a24',
  '已处理': '#07c160'
};

Page({

  onLoad: function (options) {
    const { id, admin } = options;
    // URL 参数为字符串，需显式判定，避免 'false' 被当作真值
    this.setData({ admin: admin === 'true' || admin === true || admin === '1' });
    this.getApplyDataItem(id);
  },

  /* 申报详情 */
  getApplyDataItem(id) {
    api.getApplyById(id).then(res => {
      const item = (res.data || [])[0];
      if (!item) {
        wx.showToast({ title: '记录不存在或已删除', icon: 'none' });
        return;
      }
      this.setData({ data: item, statusColor: STATUS_COLOR[item.status] || '#999999' });
    }).catch(err => {
      console.warn('[detail.getApplyDataItem] 失败:', err);
      wx.showToast({ title: '加载详情失败', icon: 'none' });
    });
  },

  /* 一键联系 */
  callApplyPhone(e) {
    wx.makePhoneCall({
      phoneNumber: e.currentTarget.dataset.phone
    });
  },

  /* 一键复制 */
  copyApplyPhone(e) {
    wx.setClipboardData({
      data: e.currentTarget.dataset.phone,
    });
  },

  /* 预览图片 */
  previewImage(e) {
    const { url, urls } = e.currentTarget.dataset;
    wx.previewImage({ current: url, urls: urls });
  }

})
