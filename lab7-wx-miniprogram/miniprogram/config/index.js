/**
 * 全局配置文件
 * 部署时需替换的 ID 都集中在这里，便于一处修改、全项目生效。
 * 详细申请步骤见 docs/部署指南.md
 */

// 云开发环境 ID —— 在微信开发者工具「云开发控制台」获取
const CLOUD_ENV = 'dorm-8svqc';

// 小程序 AppID —— 在微信公众平台 mp.weixin.qq.com 获取
const APP_ID = 'wx7273f8f3dff4386d';

// 订阅消息模板 ID —— 在小程序管理后台「功能 → 订阅消息」中申请
// applyNotice: 报修申请通知（发给管理员）；handleNotice: 报修处理通知（发给报修人）
const SUBSCRIBE_TEMPLATE = {
  applyNotice: '4Lnbo47VBu7woS0m0O8UjZ-7TBozETC4Mr5tdkwJ4v4',
  handleNotice: 'xdcaBq1COut3fsO_YvmrvQKYrgDrKmMaR-EwbmvH-VU'
};

// 广告单元 ID（可选，不需要广告可保留空字符串）
const AD_UNIT = {
  interstitial: '',   // 插屏广告
  banner: ''          // banner 广告
};

// 云函数名
const CLOUD_FUNCTION = {
  login: 'login',
  applyNotice: 'applyNotice',
  handleNotice: 'handleNotice'
};

// 数据集合名
const COLLECTION = {
  apply: 'c_apply',   // 报修记录
  role: 'c_role',     // 角色权限
  share: 'c_share'    // 分享配置
};

// 业务常量
const BIZ = {
  // 报修位置分类
  locations: ['宿舍', '教室', '办公室', '公共区域', '其他'],
  // 故障类型分类
  faultTypes: ['水电', '网络', '门窗', '家具', '电器', '其他'],
  // 维修级别
  levels: ['普通维修', '紧急维修']
};

export {
  CLOUD_ENV,
  APP_ID,
  SUBSCRIBE_TEMPLATE,
  AD_UNIT,
  CLOUD_FUNCTION,
  COLLECTION,
  BIZ
};
