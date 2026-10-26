import * as api from '../../utils/api';

Page({

  data: {
    account: '',
    password: '',
    loading: false
  },

  onAccountInput(e) {
    this.setData({ account: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  /* 点击演示账号快速填充 */
  fillAccount(e) {
    const { account } = e.currentTarget.dataset;
    this.setData({ account, password: '123456' });
  },

  /* 账号密码登录 */
  async onLogin() {
    const { account, password } = this.data;
    if (!account.trim()) {
      wx.showToast({ title: '请输入账号', icon: 'none' });
      return;
    }
    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }
    this.setData({ loading: true });
    try {
      const user = await api.loginWithAccount(account, password);
      if (!user) {
        wx.showToast({ title: '账号或密码错误', icon: 'none' });
        return;
      }
      this.saveSession(user);
      wx.showToast({ title: '登录成功', icon: 'success', duration: 800 });
      setTimeout(() => wx.reLaunch({ url: '/pages/index/index' }), 800);
    } catch (err) {
      console.warn('[login.onLogin] 登录失败:', err);
      wx.showToast({ title: '登录失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  /* 微信一键登录：静默获取 openid，按角色表 openid 匹配 */
  async onWechatLogin() {
    wx.showLoading({ title: '登录中...', mask: true });
    try {
      const res = await api.login();
      const openid = res.result.openid;
      console.log('[login] openid:', openid);
      const roleRes = await api.getRoleList();
      const matched = (roleRes.data || []).find(item => item.openid === openid);
      if (!matched) {
        wx.hideLoading();
        wx.showToast({ title: '该微信未分配角色', icon: 'none' });
        return;
      }
      this.saveSession({ ...matched, openid });
      wx.hideLoading();
      wx.showToast({ title: '登录成功', icon: 'success', duration: 800 });
      setTimeout(() => wx.reLaunch({ url: '/pages/index/index' }), 800);
    } catch (err) {
      wx.hideLoading();
      console.warn('[login.onWechatLogin] 登录失败:', err);
      wx.showToast({ title: '登录失败，请重试', icon: 'none' });
    }
  },

  /* 统一写入会话；管理员额外缓存，供订阅消息发送使用 */
  saveSession(user) {
    api.setSession(user);
    if (user.role === '超级管理员') {
      wx.setStorageSync('admin', user);
    }
  },

})
