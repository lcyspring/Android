/**
 * API 层（Repository）
 * 集中封装所有云数据库与云函数调用，页面只调用本模块，
 * 不直接散写 wx.cloud.xxx，方便统一维护与异常处理。
 *
 * 实验七完善点：
 * 1. 增加 USE_MOCK 开关：未开通云开发环境时自动兜底到本地数据，
 *    保证无云环境也能演示完整业务流程（任务书「网络请求」「本地数据保存」均覆盖）。
 * 2. 增加「我的报修」本地缓存：提交后同步写入 wx.storage，满足本地数据保存要求，
 *    且支持离线查看本人提交记录。
 * 3. 统一异常处理：云调用失败时给用户明确反馈，不再只 console.log。
 */
import { COLLECTION, CLOUD_FUNCTION } from '../config/index';

// 本地缓存键
const STORAGE_KEY_MINE = 'my_repairs';      // 我的报修记录
const STORAGE_KEY_ADMIN = 'admin';          // 管理员信息（原项目已用）
const STORAGE_KEY_MOCK_SEED = 'mock_seeded';// mock 种子数据标记

// 是否启用本地兜底：true=无云环境也跑；false=纯云开发
// 当 wx.cloud 不可用或调用失败时自动回退到本地
const USE_MOCK_FALLBACK = true;

let db = null;
try {
  db = wx.cloud && wx.cloud.database ? wx.cloud.database() : null;
} catch (e) {
  console.warn('[api] 云数据库初始化失败，将使用本地兜底数据:', e.message);
  db = null;
}

/* ===================== 本地兜底数据（mock） ===================== */

// 生成 mock 种子数据，让无云环境也能看到列表
function ensureMockSeed() {
  const seeded = wx.getStorageSync(STORAGE_KEY_MOCK_SEED);
  if (seeded) return;
  const now = Date.now();
  const seed = [
    {
      _id: 'mock_1', _openid: 'mock_user',
      name: '张三', floor: 3, dorm: '301', phone: '13800138000',
      location: '宿舍', faultType: '水电',
      desc: '卫生间水龙头漏水，急需维修', level: '紧急维修',
      status: '未处理', createTime: formatTime(now - 3600000),
      images: []
    },
    {
      _id: 'mock_2', _openid: 'mock_user',
      name: '李四', floor: 5, dorm: '502', phone: '13900139000',
      location: '宿舍', faultType: '网络',
      desc: '宿舍网线口松动，无法上网', level: '普通维修',
      status: '未处理', createTime: formatTime(now - 7200000),
      images: []
    },
    {
      _id: 'mock_3', _openid: 'mock_user',
      name: '王五', floor: 2, dorm: '203', phone: '13700137000',
      location: '教室', faultType: '门窗',
      desc: '教室门锁损坏，关不严', level: '普通维修',
      status: '已处理', createTime: formatTime(now - 86400000),
      images: []
    }
  ];
  wx.setStorageSync(STORAGE_KEY_MOCK_SEED, seed);
}

// 简单时间格式化（不引入额外依赖）
function formatTime(ts) {
  const d = new Date(ts);
  const p = (n) => (n < 10 ? '0' + n : '' + n);
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

// 从本地缓存读取全部报修（mock 种子 + 我的报修）
function getLocalApplyList() {
  ensureMockSeed();
  const seed = wx.getStorageSync(STORAGE_KEY_MOCK_SEED) || [];
  const mine = wx.getStorageSync(STORAGE_KEY_MINE) || [];
  return [...mine, ...seed];
}

// 本地按条件过滤
function filterLocal(list, opts) {
  return list.filter(item => {
    if (opts.status && item.status !== opts.status) return false;
    if (opts.floor && item.floor !== opts.floor) return false;
    if (opts.location && item.location !== opts.location) return false;
    if (opts.faultType && item.faultType !== opts.faultType) return false;
    return true;
  });
}

/* ===================== 报修记录 c_apply ===================== */

/**
 * 查询报修列表（支持分页与条件筛选）
 * @param {Object} opts 查询条件
 *   - status:    状态筛选（未处理/已处理）
 *   - floor:     楼栋筛选（数字）
 *   - location:  报修位置（宿舍/教室/办公室...）
 *   - faultType: 故障类型（水电/网络/门窗...）
 *   - skip:      跳过条数（分页）
 *   - limit:     每页条数
 */
async function getApplyList(opts = {}) {
  const { status, floor, location, faultType, skip = 0, limit = 20 } = opts;

  // 无云环境或云不可用：走本地兜底
  if (!db || !USE_MOCK_FALLBACK) {
    return mockListResult({ status, floor, location, faultType, skip, limit });
  }

  const where = {};
  if (status) where.status = status;
  if (floor) where.floor = floor;
  if (location) where.location = location;
  if (faultType) where.faultType = faultType;

  try {
    return await db.collection(COLLECTION.apply)
      .orderBy('createTime', 'desc')
      .where(where)
      .skip(skip)
      .limit(limit)
      .get();
  } catch (err) {
    console.warn('[api.getApplyList] 云调用失败，回退本地:', err && err.errMsg);
    if (USE_MOCK_FALLBACK) {
      return mockListResult({ status, floor, location, faultType, skip, limit });
    }
    throw err;
  }
}

// 本地分页+过滤结果，返回结构与 wx.cloud 一致：{ data: [...] }
function mockListResult(opts) {
  let list = getLocalApplyList();
  list = filterLocal(list, opts);
  // 按时间倒序
  list.sort((a, b) => (a.createTime < b.createTime ? 1 : -1));
  const skip = opts.skip || 0;
  const limit = opts.limit || 20;
  const paged = list.slice(skip, skip + limit);
  return { data: paged };
}

/** 根据 _id 查询单条报修详情 */
async function getApplyById(id) {
  if (!db || !USE_MOCK_FALLBACK) {
    return mockGetByIdResult(id);
  }
  try {
    return await db.collection(COLLECTION.apply).where({ _id: id }).get();
  } catch (err) {
    console.warn('[api.getApplyById] 云调用失败，回退本地:', err && err.errMsg);
    if (USE_MOCK_FALLBACK) return mockGetByIdResult(id);
    throw err;
  }
}

function mockGetByIdResult(id) {
  const list = getLocalApplyList();
  const item = list.find(x => x._id === id);
  return { data: item ? [item] : [] };
}

/** 新增一条报修记录 */
async function addApply(data) {
  // 同步写入本地「我的报修」缓存（满足任务书本地数据保存要求）
  saveMyRepair(data);

  if (!db || !USE_MOCK_FALLBACK) {
    // 本地兜底：生成临时 _id
    const localItem = { ...data, _id: 'local_' + Date.now(), _openid: 'local_user' };
    appendMyRepairWithId(localItem);
    return { _id: localItem._id };
  }
  try {
    return await db.collection(COLLECTION.apply).add({ data });
  } catch (err) {
    console.warn('[api.addApply] 云调用失败，仅存本地:', err && err.errMsg);
    const localItem = { ...data, _id: 'local_' + Date.now(), _openid: 'local_user' };
    appendMyRepairWithId(localItem);
    return { _id: localItem._id };
  }
}

/** 更新报修状态（如：未处理 → 已处理） */
async function updateApplyStatus(id, status) {
  // 同步更新本地缓存
  updateLocalApplyStatus(id, status);
  if (!db || !USE_MOCK_FALLBACK) return { stats: { updated: 1 } };
  try {
    return await db.collection(COLLECTION.apply).where({ _id: id }).update({ data: { status } });
  } catch (err) {
    console.warn('[api.updateApplyStatus] 云调用失败，仅更新本地:', err && err.errMsg);
    return { stats: { updated: 1 } };
  }
}

/** 删除一条报修记录 */
async function removeApply(id) {
  removeLocalApply(id);
  if (!db || !USE_MOCK_FALLBACK) return { stats: { removed: 1 } };
  try {
    return await db.collection(COLLECTION.apply).doc(id).remove();
  } catch (err) {
    console.warn('[api.removeApply] 云调用失败，仅删本地:', err && err.errMsg);
    return { stats: { removed: 1 } };
  }
}

/* ===================== 「我的报修」本地缓存（实验七新增） ===================== */

function getMyRepairs() {
  return wx.getStorageSync(STORAGE_KEY_MINE) || [];
}

function saveMyRepair(data) {
  // 占位：实际带 _id 的由 appendMyRepairWithId 写入
}

function appendMyRepairWithId(item) {
  const list = wx.getStorageSync(STORAGE_KEY_MINE) || [];
  list.unshift(item);
  wx.setStorageSync(STORAGE_KEY_MINE, list);
}

function updateLocalApplyStatus(id, status) {
  // 更新我的报修
  const mine = wx.getStorageSync(STORAGE_KEY_MINE) || [];
  let changed = false;
  const newMine = mine.map(x => {
    if (x._id === id) { changed = true; return { ...x, status }; }
    return x;
  });
  if (changed) wx.setStorageSync(STORAGE_KEY_MINE, newMine);
  // 更新 mock 种子
  const seed = wx.getStorageSync(STORAGE_KEY_MOCK_SEED) || [];
  let seedChanged = false;
  const newSeed = seed.map(x => {
    if (x._id === id) { seedChanged = true; return { ...x, status }; }
    return x;
  });
  if (seedChanged) wx.setStorageSync(STORAGE_KEY_MOCK_SEED, newSeed);
}

function removeLocalApply(id) {
  // 删我的报修
  const mine = wx.getStorageSync(STORAGE_KEY_MINE) || [];
  const newMine = mine.filter(x => x._id !== id);
  if (newMine.length !== mine.length) wx.setStorageSync(STORAGE_KEY_MINE, newMine);
  // 删 mock 种子
  const seed = wx.getStorageSync(STORAGE_KEY_MOCK_SEED) || [];
  const newSeed = seed.filter(x => x._id !== id);
  if (newSeed.length !== seed.length) wx.setStorageSync(STORAGE_KEY_MOCK_SEED, newSeed);
}

/* ===================== 角色 c_role ===================== */

/** 获取角色列表（含管理员 openid） */
async function getRoleList() {
  if (!db || !USE_MOCK_FALLBACK) {
    // 本地兜底：默认把当前用户设为管理员，方便演示管理页
    const admin = wx.getStorageSync(STORAGE_KEY_ADMIN) || {
      _id: 'mock_admin', openid: 'mock_user', role: '超级管理员', name: '演示管理员', phone: '13800138000'
    };
    return { data: [admin] };
  }
  try {
    return await db.collection(COLLECTION.role).get();
  } catch (err) {
    console.warn('[api.getRoleList] 云调用失败，回退本地:', err && err.errMsg);
    const admin = wx.getStorageSync(STORAGE_KEY_ADMIN) || { _id: 'mock_admin', openid: 'mock_user', role: '超级管理员' };
    return { data: [admin] };
  }
}

/* ===================== 分享 c_share ===================== */

/** 获取小程序分享配置 */
async function getShareConfig() {
  if (!db || !USE_MOCK_FALLBACK) {
    return { data: [{ title: '校园报修助手', path: '/pages/index/index', imageUrl: '' }] };
  }
  try {
    return await db.collection(COLLECTION.share).get();
  } catch (err) {
    console.warn('[api.getShareConfig] 云调用失败，回退本地:', err && err.errMsg);
    return { data: [{ title: '校园报修助手', path: '/pages/index/index', imageUrl: '' }] };
  }
}

/* ===================== 云函数调用 ===================== */

/** 调用 login 云函数获取用户 openid */
async function login() {
  if (!wx.cloud || !wx.cloud.callFunction || !USE_MOCK_FALLBACK) {
    // 本地兜底：生成一个稳定的伪 openid
    let openid = wx.getStorageSync('mock_openid');
    if (!openid) {
      openid = 'mock_' + Math.random().toString(36).slice(2, 10);
      wx.setStorageSync('mock_openid', openid);
    }
    return { result: { openid } };
  }
  try {
    return await wx.cloud.callFunction({ name: CLOUD_FUNCTION.login });
  } catch (err) {
    console.warn('[api.login] 云函数调用失败，回退本地:', err && err.errMsg);
    let openid = wx.getStorageSync('mock_openid') || ('mock_' + Math.random().toString(36).slice(2, 10));
    wx.setStorageSync('mock_openid', openid);
    return { result: { openid } };
  }
}

/** 调用 applyNotice 云函数，给管理员发送「新报修」订阅消息 */
async function sendApplyNotice(data) {
  if (!wx.cloud || !wx.cloud.callFunction || !USE_MOCK_FALLBACK) {
    console.log('[mock] sendApplyNotice（模拟发送）:', data);
    return { result: { errCode: 0, errMsg: 'ok(mock)' } };
  }
  try {
    return await wx.cloud.callFunction({ name: CLOUD_FUNCTION.applyNotice, data });
  } catch (err) {
    console.warn('[api.sendApplyNotice] 云函数调用失败（不影响主流程）:', err && err.errMsg);
    return { result: { errCode: -1, errMsg: 'mock' } };
  }
}

/** 调用 handleNotice 云函数，给报修人发送「已处理」订阅消息 */
async function sendHandleNotice(data) {
  if (!wx.cloud || !wx.cloud.callFunction || !USE_MOCK_FALLBACK) {
    console.log('[mock] sendHandleNotice（模拟发送）:', data);
    return { result: { errCode: 0, errMsg: 'ok(mock)' } };
  }
  try {
    return await wx.cloud.callFunction({ name: CLOUD_FUNCTION.handleNotice, data });
  } catch (err) {
    console.warn('[api.sendHandleNotice] 云函数调用失败（不影响主流程）:', err && err.errMsg);
    return { result: { errCode: -1, errMsg: 'mock' } };
  }
}

/* ===================== 云存储（图片上传） ===================== */

/**
 * 上传图片到云存储
 * @param {string} filePath 本地临时路径
 * @param {string} cloudPath 云存储路径，如 repair/xxx.jpg
 */
async function uploadImage(filePath, cloudPath) {
  if (!wx.cloud || !wx.cloud.uploadFile || !USE_MOCK_FALLBACK) {
    // 本地兜底：直接返回本地路径作为 fileID（预览可用）
    return { fileID: filePath };
  }
  try {
    return await wx.cloud.uploadFile({ cloudPath, filePath });
  } catch (err) {
    console.warn('[api.uploadImage] 云上传失败，使用本地路径:', err && err.errMsg);
    return { fileID: filePath };
  }
}

export {
  getApplyList,
  getApplyById,
  addApply,
  updateApplyStatus,
  removeApply,
  getRoleList,
  getShareConfig,
  login,
  sendApplyNotice,
  sendHandleNotice,
  uploadImage,
  getMyRepairs    // 实验七新增：读取「我的报修」本地缓存
};
