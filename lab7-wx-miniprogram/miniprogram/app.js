import { CLOUD_ENV } from './config/index';

App({
  onLaunch: function () {
    // 实验七完善：云能力初始化失败时不阻断应用，
    // 后续 api 层会自动回退到本地兜底数据，保证无云环境也能演示。
    if (!wx.cloud) {
      console.warn('[app] 当前基础库不支持云能力，将使用本地兜底数据演示');
    } else {
      try {
        wx.cloud.init({
          env: CLOUD_ENV,
          traceUser: true
        });
        console.log('[app] 云开发初始化成功，env:', CLOUD_ENV);
      } catch (e) {
        console.warn('[app] 云开发初始化失败，使用本地兜底:', e.message);
      }
    }
  },
})
