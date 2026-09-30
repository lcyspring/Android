import { icon } from '../../config/config.default';
import { moment } from '../../utils/moment';
import * as api from '../../utils/api';
import { BIZ, SUBSCRIBE_TEMPLATE, AD_UNIT } from '../../config/index';

Page({

  data: {
    name: '',
    floor: '',
    dorm: '',
    phone: '',
    desc: '',
    level: '普通维修',
    levelIcon: icon.ordinary,
    pickerList: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
    // 新增：报修位置、故障分类、图片列表
    locations: BIZ.locations,
    faultTypes: BIZ.faultTypes,
    location: '',
    faultType: '',
    imageList: [],
    maxImageCount: 6
  },

  /* 申报人 */
  setName(e) {
    this.setData({ name: e.detail.value })
  },

  /* 选择栋数 */
  selectFloor(e) {
    this.setData({ floor: this.data.pickerList[Number(e.detail.value)] })
  },

  /* 设置宿舍号 */
  setDormNum(e) {
    this.setData({ dorm: e.detail.value })
  },

  /* 联系电话 */
  setPhone(e) {
    this.setData({ phone: e.detail.value })
  },

  /* 申报描述 */
  setDesc(e) {
    this.setData({ desc: e.detail.value })
  },

  /* 选择报修位置 */
  selectLocation(e) {
    this.setData({ location: this.data.locations[Number(e.detail.value)] })
  },

  /* 选择故障类型 */
  selectFaultType(e) {
    this.setData({ faultType: this.data.faultTypes[Number(e.detail.value)] })
  },

  /* 选择维修级别 */
  selectLevel(e) {
    if (e.detail === '紧急维修') {
      this.setData({ levelIcon: icon.press })
    } else {
      this.setData({ levelIcon: icon.ordinary })
    }
    this.setData({ level: e.detail })
  },

  clickLevel(e) {
    if (e.currentTarget.dataset.level === '紧急维修') {
      this.setData({ levelIcon: icon.press })
    } else {
      this.setData({ levelIcon: icon.ordinary })
    }
    this.setData({ level: e.currentTarget.dataset.level })
  },

  /* 选择图片 */
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
    const imageList = this.data.imageList.filter((_, i) => i !== index);
    this.setData({ imageList });
  },

  /* 预览图片 */
  previewImage(e) {
    const { url } = e.currentTarget.dataset;
    wx.previewImage({ current: url, urls: this.data.imageList });
  },

  /* 提交申报表 */
  async inApplyData() {
    if (!this.validate()) return;

    // 申请订阅消息权限（失败不影响提交）
    wx.requestSubscribeMessage({
      tmplIds: [SUBSCRIBE_TEMPLATE.applyNotice],
      fail: () => {}
    });

    wx.showLoading({ title: '正在提交...', mask: true });

    try {
      // 1. 上传图片到云存储，拿到 fileID 列表
      const fileIds = [];
      for (let i = 0; i < this.data.imageList.length; i++) {
        const filePath = this.data.imageList[i];
        const ext = filePath.split('.').pop();
        const cloudPath = `repair/${Date.now()}_${i}.${ext}`;
        const uploadRes = await api.uploadImage(filePath, cloudPath);
        fileIds.push(uploadRes.fileID);
      }

      // 2. 写入数据库
      await api.addApply({
        name: this.data.name.trim(),
        floor: this.data.floor,
        dorm: this.data.dorm,
        phone: this.data.phone,
        desc: this.data.desc.trim(),
        level: this.data.level,
        levelIcon: this.data.levelIcon,
        location: this.data.location,
        faultType: this.data.faultType,
        images: fileIds,
        status: '未处理',
        createTime: moment('YYYY-MM-DD hh:mm:ss'),
      });

      wx.hideLoading();
      wx.showToast({ title: '提交成功', duration: 1000 });

      // 3. 给管理员发送订阅消息（失败不影响主流程）
      const admin = wx.getStorageSync('admin');
      if (admin && admin.openid) {
        api.sendApplyNotice({
          name: this.data.name,
          dorm: this.data.location + ' ' + this.data.floor + '栋' + this.data.dorm,
          desc: this.data.desc.substr(0, 16) + '...',
          phone: this.data.phone,
          createTime: moment('YYYY-MM-DD hh:mm:ss'),
          templateId: SUBSCRIBE_TEMPLATE.applyNotice,
          openid: admin.openid
        }).catch(err => console.log('sendApplyNotice fail:', err));
      }

      // 4. 返回首页
      wx.reLaunch({ url: '../index/index?id=success' });
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '提交失败', icon: 'error' });
      console.error(err);
    }
  },

  /* 申报表单校验 */
  validate() {
    let phoneReg = /[1][3,4,5,7,8][0-9]{9}$/;
    if (!this.data.name) {
      wx.showToast({ title: '请填写申报人', icon: 'error', duration: 500 });
      return false;
    }
    if (!this.data.location) {
      wx.showToast({ title: '请选择报修位置', icon: 'error', duration: 500 });
      return false;
    }
    if (!this.data.floor) {
      wx.showToast({ title: '请选择栋数', icon: 'error', duration: 500 });
      return false;
    }
    if (!this.data.dorm) {
      wx.showToast({ title: '请填写宿舍/房间号', icon: 'error', duration: 500 });
      return false;
    }
    if (!this.data.faultType) {
      wx.showToast({ title: '请选择故障类型', icon: 'error', duration: 500 });
      return false;
    }
    if (!this.data.phone) {
      wx.showToast({ title: '请填写手机号码', icon: 'error', duration: 500 });
      return false;
    }
    if (!phoneReg.test(this.data.phone)) {
      wx.showToast({ title: '请填写正确手机号', icon: 'error', duration: 500 });
      return false;
    }
    if (!this.data.desc) {
      wx.showToast({ title: '请说明情况', icon: 'error', duration: 500 });
      return false;
    }
    return true;
  }

})
