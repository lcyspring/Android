import * as api from '../../utils/api';

Page({

  data: {
    id: '',
    data: {},
    content: '',
    imageList: [],
    maxImageCount: 6,
    submitting: false
  },

  onLoad(options) {
    // 权限守卫：仅维修人员可上传维修情况
    const session = api.getSession();
    if (!session || session.role !== '维修人员') {
      wx.showToast({ title: '请以维修人员账号登录', icon: 'none' });
      setTimeout(() => wx.reLaunch({ url: '/pages/login/login' }), 900);
      return;
    }
    this.setData({ id: (options && options.id) || '' });
    this.loadDetail();
  },

  /* 读取报修详情 */
  loadDetail() {
    api.getApplyById(this.data.id).then(res => {
      const item = (res.data || [])[0];
      if (!item) {
        wx.showToast({ title: '记录不存在或已删除', icon: 'none' });
        return;
      }
      this.setData({ data: item });
    }).catch(err => {
      console.warn('[repair.loadDetail] 失败:', err);
      wx.showToast({ title: '加载详情失败', icon: 'none' });
    });
  },

  /* 维修说明 */
  setContent(e) {
    this.setData({ content: e.detail.value });
  },

  /* 选择维修现场图片 */
  chooseImage() {
    const remaining = this.data.maxImageCount - this.data.imageList.length;
    if (remaining <= 0) {
      wx.showToast({ title: '最多上传' + this.data.maxImageCount + '张', icon: 'none' });
      return;
    }
    wx.chooseMedia({
      count: remaining,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed'],
      success: (res) => {
        const newPaths = res.tempFiles.map(f => f.tempFilePath);
        this.setData({ imageList: [...this.data.imageList, ...newPaths] });
      }
    });
  },

  /* 删除已选图片 */
  deleteImage(e) {
    const { index } = e.currentTarget.dataset;
    this.setData({ imageList: this.data.imageList.filter((_, i) => i !== index) });
  },

  /* 预览图片 */
  previewImage(e) {
    const { url } = e.currentTarget.dataset;
    wx.previewImage({ current: url, urls: this.data.imageList });
  },

  /* 仅保存维修记录（状态保持「已确认」） */
  saveOnly() {
    this.submit(false);
  },

  /* 提交维修记录并标记「已处理」 */
  submitAndComplete() {
    this.submit(true);
  },

  /* 上传图片 + 提交维修记录 */
  async submit(complete) {
    if (this.data.submitting) return;
    if (!this.data.content.trim() && !this.data.imageList.length) {
      wx.showToast({ title: '请填写维修情况或上传图片', icon: 'none' });
      return;
    }
    this.setData({ submitting: true });
    wx.showLoading({ title: '提交中...', mask: true });
    try {
      const images = [];
      for (let i = 0; i < this.data.imageList.length; i++) {
        const filePath = this.data.imageList[i];
        const ext = filePath.split('.').pop();
        const uploadRes = await api.uploadImage(filePath, `repair/${Date.now()}_${i}.${ext}`);
        images.push(uploadRes.fileID);
      }
      await api.submitRepair(this.data.id, { content: this.data.content.trim(), images }, complete);
      wx.hideLoading();
      wx.showToast({ title: complete ? '已完成维修' : '记录已保存', duration: 800 });
      setTimeout(() => wx.navigateBack(), 800);
    } catch (err) {
      wx.hideLoading();
      console.warn('[repair.submit] 失败:', err);
      wx.showToast({ title: '提交失败，请重试', icon: 'error' });
    }
    this.setData({ submitting: false });
  }

})
