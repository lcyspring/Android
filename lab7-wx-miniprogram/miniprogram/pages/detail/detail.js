import * as api from '../../utils/api';

Page({

  onLoad: function (options) {
    const { id, admin } = options;
    this.getApplyDataItem(id);
    if (admin) {
      this.setData({ admin });
    }
  },

  /* 申报详情 */
  getApplyDataItem(id) {
    api.getApplyById(id).then(res => {
      const item = (res.data || [])[0];
      if (!item) {
        wx.showToast({ title: '记录不存在或已删除', icon: 'none' });
        return;
      }
      this.setData({ data: item });
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
