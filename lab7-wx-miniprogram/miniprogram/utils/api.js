/**
 * API 层（Repository 层）
 * 集中封装所有云数据库与云函数调用，页面只调用本模块，
 * 不直接散写 wx.cloud.xxx，方便统一维护与异常处理。
 *
 * 架构对应任务书要求：「UI - ViewModel - Repository」中的 Repository 层。
 *
 * 实验七完善：双模 Repository —— 云开发优先，本地兜底（USE_MOCK_FALLBACK=true）
 * 当 wx.cloud 不可用、云环境未开通或调用失败时，自动回退到 wx.storage 本地数据，
 * 保证无云环境也能演示完整业务流程（提交→列表→详情→管理→处理）。
 */
import { COLLECTION, CLOUD_FUNCTION, USE_MOCK_FALLBACK } from '../config/index';

let db = null;
try {
  if (wx.cloud) db = wx.cloud.database();
} catch (e) {
  console.warn('[api] wx.cloud.database 初始化失败，启用本地兜底:', e.message);
}

/* ===================== 本地兜底：mock 种子与 wx.storage 工具 ===================== */

const STORAGE_KEYS = {
  apply: 'local_apply',          // 本地报修记录池（模拟 c_apply 集合）
  myRepairs: 'my_repairs',      // 当前用户提交的报修（含本地生成的）
  admin: 'admin',               // 管理员信息缓存
  role: 'local_role',            // 本地角色列表（模拟 c_role 集合）
  share: 'local_share',          // 本地分享配置（模拟 c_share 集合）
  mockSeeded: 'mock_seeded_v2'  // 是否已注入种子数据（v2：含审核流与维修人员）
};

/**
 * 报修种子数据（覆盖 4 种状态，便于按角色演示）
 * - 未处理：待管理员审核
 * - 已确认：管理员审核通过并指派维修人员
 * - 不受理：管理员驳回，含 rejectReason
 * - 已处理：维修人员完成，含 workerName / repairRecords
 */
const SEED_DATA = [
  {
    _id: 'mock_seed_1',
    dorm: '305', floor: 1, level: '紧急维修',
    levelIcon: 'https://646f-dorm-8svqc-1259164383.tcb.qcloud.la/%E7%94%B5%E8%AF%9D.png',
    phone: '13800138001', _openid: 'mock_openid_admin',
    createTime: '2026-10-12 09:30:00',
    desc: '宿舍厕所堵塞，请安排维修', name: '李春雨',
    status: '未处理', location: '宿舍', faultType: '水电', images: [],
    rejectReason: '', workerName: '', workerPhone: '', repairRecords: []
  },
  {
    _id: 'mock_seed_2', dorm: '104', floor: 2, level: '普通维修',
    levelIcon: 'https://646f-dorm-8svqc-1259164383.tcb.qcloud.la/%E7%81%AF%E6%B3%A1.png',
    phone: '13800138002', _openid: 'mock_openid_user',
    createTime: '2026-10-12 10:15:00',
    desc: '灯管坏了，需要更换', name: '李文鑫',
    status: '未处理', location: '宿舍', faultType: '电器', images: [],
    rejectReason: '', workerName: '', workerPhone: '', repairRecords: []
  },
  {
    _id: 'mock_seed_3', dorm: '108', floor: 3, level: '普通维修',
    levelIcon: 'https://646f-dorm-8svqc-1259164383.tcb.qcloud.la/%E7%81%AF%E6%B3%A1.png',
    phone: '13800138003', _openid: 'mock_openid_user2',
    createTime: '2026-10-11 14:20:00',
    desc: '空调不制冷，运行噪音大', name: '裴杨坤',
    status: '已确认', location: '宿舍', faultType: '电器', images: [],
    rejectReason: '', workerName: '罗钢', workerPhone: '17726131718',
    confirmTime: '2026-10-11 15:00:00', repairRecords: []
  },
  {
    _id: 'mock_seed_4', dorm: '104', floor: 2, level: '普通维修',
    levelIcon: 'https://646f-dorm-8svqc-1259164383.tcb.qcloud.la/%E7%81%AF%E6%B3%A1.png',
    phone: '13800138002', _openid: 'mock_openid_user',
    createTime: '2026-10-10 08:40:00',
    desc: '想在宿舍加装一个插座', name: '李文鑫',
    status: '不受理', location: '宿舍', faultType: '水电', images: [],
    rejectReason: '私自加装插座属于违规改造，请通过后勤处正式渠道申请',
    confirmTime: '2026-10-10 09:10:00', workerName: '', workerPhone: '', repairRecords: []
  },
  {
    _id: 'mock_seed_5', dorm: '108', floor: 3, level: '普通维修',
    levelIcon: 'https://646f-dorm-8svqc-1259164383.tcb.qcloud.la/%E7%81%AF%E6%B3%A1.png',
    phone: '13800138003', _openid: 'mock_openid_user2',
    createTime: '2026-10-09 16:05:00',
    desc: '门锁松动，已修复', name: '裴杨坤',
    status: '已处理', location: '宿舍', faultType: '门窗', images: [],
    rejectReason: '', workerName: '罗钢', workerPhone: '17726131718',
    confirmTime: '2026-10-09 16:40:00', handleTime: '2026-10-09 18:20:00',
    repairRecords: [
      { content: '已更换门锁锁芯并加固螺丝，反复测试开合正常。', images: [], createTime: '2026-10-09 18:20:00', operator: '罗钢' }
    ]
  }
];

/**
 * 角色种子（含账号密码，供账号登录演示）
 * 与 c_role 云集合字段保持一致：account / password / role / name / phone / floor / dorm / openid
 * 演示账号：
 *   admin/123456   超级管理员（审核报修、指派维修人员）
 *   luogang/123456 维修人员（接单、上传维修情况）
 *   heshifu/123456 维修人员
 *   wlx/123456     普通用户（只看自己宿舍）
 *   pyk/123456     普通用户
 */
const SEED_ROLE = [
  { openid: 'mock_openid_admin', account: 'admin', password: '123456', role: '超级管理员', name: '李春雨', phone: '13800138001', floor: 1, dorm: '305' },
  { openid: 'mock_openid_worker1', account: 'luogang', password: '123456', role: '维修人员', name: '罗钢', phone: '17726131718', floor: null, dorm: '' },
  { openid: 'mock_openid_worker2', account: 'heshifu', password: '123456', role: '维修人员', name: '贺强', phone: '13327228777', floor: null, dorm: '' },
  { openid: 'mock_openid_user', account: 'wlx', password: '123456', role: '普通用户', name: '李文鑫', phone: '13800138002', floor: 2, dorm: '104' },
  { openid: 'mock_openid_user2', account: 'pyk', password: '123456', role: '普通用户', name: '裴杨坤', phone: '13800138003', floor: 3, dorm: '108' }
];
const SEED_SHARE = [{ title: '校园报修助手，随手提交、即时跟进', path: 'pages/index/index', imageUrl: '' }];

/** 首次启动注入 mock 种子数据 */
function ensureSeed() {
  const seeded = wx.getStorageSync(STORAGE_KEYS.mockSeeded);
  if (!seeded) {
    wx.setStorageSync(STORAGE_KEYS.apply, SEED_DATA);
    wx.setStorageSync(STORAGE_KEYS.role, SEED_ROLE);
    wx.setStorageSync(STORAGE_KEYS.share, SEED_SHARE);
    wx.setStorageSync(STORAGE_KEYS.mockSeeded, true);
    console.log('[api] mock 种子数据已注入（5 条报修 + 5 个账号 + 1 分享配置）');
    return;
  }
  // 迁移：旧版本缓存的角色缺少账号/宿舍/维修人员，补写最新种子（保留报修数据不重置）
  const roles = wx.getStorageSync(STORAGE_KEYS.role) || [];
  const needUpgrade = !roles.length || !roles[0].account || !roles[0].dorm
    || !roles.some(r => r.role === '维修人员');
  if (needUpgrade) {
    wx.setStorageSync(STORAGE_KEYS.role, SEED_ROLE);
    console.log('[api] 角色种子已升级为含账号、宿舍归属与维修人员的版本');
  }
}

/** 读取本地报修记录池 */
function localGetAllApply() {
  ensureSeed();
  return wx.getStorageSync(STORAGE_KEYS.apply) || [];
}

/** 写回本地报修记录池 */
function localSaveAllApply(list) {
  wx.setStorageSync(STORAGE_KEYS.apply, list);
}

/** 生成模拟 _id */
function genLocalId() {
  return 'local_' + Date.now() + '_' + Math.floor(Math.random() * 10000);
}

/** 当前时间文本（YYYY-MM-DD HH:mm:ss） */
function nowText() {
  const d = new Date();
  const p = n => (n < 10 ? '0' + n : '' + n);
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate())
    + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
}

/** 生成本地 mock openid（首次随机，之后复用） */
function getMockOpenid() {
  let oid = wx.getStorageSync('mock_openid');
  if (!oid) {
    oid = 'mock_openid_' + Math.floor(Math.random() * 1e8);
    wx.setStorageSync('mock_openid', oid);
  }
  return oid;
}

/* ===================== 报修记录 c_apply ===================== */

/**
 * 查询报修列表（支持分页与条件筛选）
 * 云优先：走云数据库；失败则回退到 wx.storage 本地池。
 *
 * @param {Object} opts 查询条件
 *   - status:    状态筛选（未处理/已处理）
 *   - floor:     楼栋筛选（数字）
 *   - dorm:      宿舍号筛选（普通用户只查自己宿舍）
 *   - workerName: 维修人员筛选（维修人员只看指派给自己的）
 *   - location:  报修位置（宿舍/教室/办公室...）
 *   - faultType: 故障类型（水电/网络/门窗...）
 *   - skip:      跳过条数（分页）
 *   - limit:     每页条数
 */
async function getApplyList(opts = {}) {
  const { status, floor, dorm, workerName, location, faultType, skip = 0, limit = 20 } = opts;
  // 云优先
  if (db) {
    try {
      const where = {};
      if (status) where.status = status;
      if (floor) where.floor = floor;
      if (dorm) where.dorm = dorm;
      if (workerName) where.workerName = workerName;
      if (location) where.location = location;
      if (faultType) where.faultType = faultType;
      const res = await db.collection(COLLECTION.apply)
        .orderBy('createTime', 'desc')
        .where(where)
        .skip(skip)
        .limit(limit)
        .get();
      return res;
    } catch (e) {
      console.warn('[api.getApplyList] 云查询失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  // 本地兜底
  let list = localGetAllApply();
  if (status) list = list.filter(x => x.status === status);
  if (floor) list = list.filter(x => x.floor === floor);
  if (dorm) list = list.filter(x => x.dorm === dorm);
  if (workerName) list = list.filter(x => x.workerName === workerName);
  if (location) list = list.filter(x => x.location === location);
  if (faultType) list = list.filter(x => x.faultType === faultType);
  list.sort((a, b) => (a.createTime < b.createTime ? 1 : -1));
  const page = list.slice(skip, skip + limit);
  return { data: page };
}

/** 根据 _id 查询单条报修详情 */
async function getApplyById(id) {
  if (db) {
    try {
      return await db.collection(COLLECTION.apply).where({ _id: id }).get();
    } catch (e) {
      console.warn('[api.getApplyById] 云查询失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  const list = localGetAllApply();
  return { data: list.filter(x => x._id === id) };
}

/**
 * 新增一条报修记录
 * 同步写入本地 my_repairs 缓存，便于「我的报修」离线查看
 */
async function addApply(data) {
  if (db) {
    try {
      return await db.collection(COLLECTION.apply).add({ data });
    } catch (e) {
      console.warn('[api.addApply] 云写入失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  // 本地兜底：构造完整记录并写回池 + my_repairs
  const oid = getMockOpenid();
  const record = {
    _id: genLocalId(),
    _openid: oid,
    images: data.images || [],
    ...data
  };
  const list = localGetAllApply();
  list.unshift(record);
  localSaveAllApply(list);
  // my_repairs 缓存由 publish.js 提交成功后统一写入，避免重复
  return { _id: record._id };
}

/**
 * 通用更新报修记录（审核结果、维修记录等都走这里）
 * 云优先：按 _id 更新；失败回退本地池合并。
 *
 * @param {string} id    报修记录 _id
 * @param {Object} patch 待更新字段
 */
async function updateApply(id, patch) {
  if (db) {
    try {
      return await db.collection(COLLECTION.apply).doc(id).update({ data: patch });
    } catch (e) {
      console.warn('[api.updateApply] 云更新失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  const list = localGetAllApply();
  const idx = list.findIndex(x => x._id === id);
  if (idx >= 0) {
    list[idx] = { ...list[idx], ...patch };
    localSaveAllApply(list);
  }
  return { stats: { updated: idx >= 0 ? 1 : 0 } };
}

/**
 * 管理员审核通过：状态置为「已确认」并指派维修人员
 *
 * @param {string} id     报修记录 _id
 * @param {Object} worker 维修人员 { name, phone }
 */
async function confirmApply(id, worker) {
  return updateApply(id, {
    status: '已确认',
    workerName: (worker && worker.name) || '',
    workerPhone: (worker && worker.phone) || '',
    confirmTime: nowText()
  });
}

/**
 * 管理员驳回：状态置为「不受理」并记录原因
 *
 * @param {string} id     报修记录 _id
 * @param {string} reason 不受理原因
 */
async function rejectApply(id, reason) {
  return updateApply(id, {
    status: '不受理',
    rejectReason: reason || '不符合报修条件',
    confirmTime: nowText()
  });
}

/**
 * 维修人员上传维修情况，追加到 repairRecords
 *
 * @param {string}  id        报修记录 _id
 * @param {Object}  record    { content, images }
 * @param {boolean} complete  true 时同时把状态置为「已处理」
 */
async function submitRepair(id, record = {}, complete = false) {
  const res = await getApplyById(id);
  const current = (res.data || [])[0] || {};
  const session = getSession() || {};
  const records = (current.repairRecords || []).concat([{
    content: record.content || '维修完成',
    images: record.images || [],
    createTime: nowText(),
    operator: session.name || '维修人员'
  }]);
  const patch = { repairRecords: records };
  if (complete) {
    patch.status = '已处理';
    patch.handleTime = nowText();
  }
  return updateApply(id, patch);
}

/** 删除一条报修记录 */
async function removeApply(id) {
  if (db) {
    try {
      return await db.collection(COLLECTION.apply).doc(id).remove();
    } catch (e) {
      console.warn('[api.removeApply] 云删除失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  let list = localGetAllApply();
  list = list.filter(x => x._id !== id);
  localSaveAllApply(list);
  return { stats: { removed: 1 } };
}

/* ===================== 角色 c_role ===================== */

/** 获取角色列表（含管理员 openid） */
async function getRoleList() {
  if (db) {
    try {
      return await db.collection(COLLECTION.role).get();
    } catch (e) {
      console.warn('[api.getRoleList] 云查询失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  ensureSeed();
  return { data: wx.getStorageSync(STORAGE_KEYS.role) || [] };
}

/* ===================== 分享 c_share ===================== */

/** 获取小程序分享配置 */
async function getShareConfig() {
  if (db) {
    try {
      return await db.collection(COLLECTION.share).get();
    } catch (e) {
      console.warn('[api.getShareConfig] 云查询失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  ensureSeed();
  return { data: wx.getStorageSync(STORAGE_KEYS.share) || [] };
}

/* ===================== 账号登录 / 会话 ===================== */

/** 会话存储键（登录成功后写入，页面据此判断登录态与角色） */
const SESSION_KEY = 'userInfo';

/**
 * 账号密码登录
 * 云优先：查 c_role 集合 account + password 匹配；失败回退本地角色种子。
 *
 * @param {string} account  账号
 * @param {string} password 密码
 * @returns {Promise<Object|null>} 匹配到的用户（含 role/name/phone/openid），无匹配返回 null
 */
async function loginWithAccount(account, password) {
  const acc = (account || '').trim();
  if (!acc || !password) return null;
  if (db) {
    try {
      const res = await db.collection(COLLECTION.role).where({ account: acc, password }).get();
      return (res.data && res.data[0]) || null;
    } catch (e) {
      console.warn('[api.loginWithAccount] 云查询失败，回退本地:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  ensureSeed();
  const roles = wx.getStorageSync(STORAGE_KEYS.role) || [];
  return roles.find(r => r.account === acc && r.password === password) || null;
}

/** 读取当前登录会话，未登录返回 null */
function getSession() {
  return wx.getStorageSync(SESSION_KEY) || null;
}

/** 写入登录会话 */
function setSession(user) {
  wx.setStorageSync(SESSION_KEY, user);
}

/** 清除登录会话 */
function clearSession() {
  wx.removeStorageSync(SESSION_KEY);
  wx.removeStorageSync(STORAGE_KEYS.admin);
}

/* ===================== 云函数调用 ===================== */

/** 调用 login 云函数获取用户 openid */
async function login() {
  if (wx.cloud) {
    try {
      return await wx.cloud.callFunction({ name: CLOUD_FUNCTION.login });
    } catch (e) {
      console.warn('[api.login] 云函数失败，回退 mock openid:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  // 本地兜底：固定返回种子管理员 openid，与 SEED_ROLE 匹配，
  // 保证无云环境下默认就是管理员，能直接演示管理后台。
  // （此前用随机 mock openid，和角色列表对不上，导致永远"暂无权限"）
  return { result: { openid: 'mock_openid_admin' } };
}

/** 调用 applyNotice 云函数，给管理员发送「新报修」订阅消息（本地兜底走空成功） */
async function sendApplyNotice(data) {
  if (wx.cloud) {
    try {
      return await wx.cloud.callFunction({ name: CLOUD_FUNCTION.applyNotice, data });
    } catch (e) {
      console.warn('[api.sendApplyNotice] 云函数失败，本地兜底（跳过通知）:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  return { errCode: 0, errMsg: 'mock:sendApplyNotice skipped' };
}

/** 调用 handleNotice 云函数，给报修人发送「已处理」订阅消息 */
async function sendHandleNotice(data) {
  if (wx.cloud) {
    try {
      return await wx.cloud.callFunction({ name: CLOUD_FUNCTION.handleNotice, data });
    } catch (e) {
      console.warn('[api.sendHandleNotice] 云函数失败，本地兜底（跳过通知）:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  return { errCode: 0, errMsg: 'mock:sendHandleNotice skipped' };
}

/* ===================== 云存储（图片上传） ===================== */

/**
 * 上传图片到云存储
 * 本地兜底：把本地临时路径原样返回（fileID 即本地路径，预览可正常显示）
 * @param {string} filePath 本地临时路径
 * @param {string} cloudPath 云存储路径，如 repair/xxx.jpg
 */
async function uploadImage(filePath, cloudPath) {
  if (wx.cloud) {
    try {
      return await wx.cloud.uploadFile({ cloudPath, filePath });
    } catch (e) {
      console.warn('[api.uploadImage] 云存储失败，本地兜底（使用本地路径）:', e.message);
      if (!USE_MOCK_FALLBACK) throw e;
    }
  }
  // 本地兜底：fileID 直接用本地路径，wx.previewImage / image 组件都能显示
  return { fileID: filePath, statusCode: 0, errMsg: 'mock:uploadImage local' };
}

export {
  getApplyList,
  getApplyById,
  addApply,
  updateApply,
  confirmApply,
  rejectApply,
  submitRepair,
  removeApply,
  getRoleList,
  getShareConfig,
  login,
  loginWithAccount,
  getSession,
  setSession,
  clearSession,
  sendApplyNotice,
  sendHandleNotice,
  uploadImage
};
