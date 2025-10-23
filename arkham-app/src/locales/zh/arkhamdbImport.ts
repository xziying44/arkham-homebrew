export default {
  title: 'ArkhamDB导入',
  description: '从ArkhamDB JSON内容包导入卡牌到当前工作空间',
  upload: {
    title: '选择或拖拽ArkhamDB内容包文件',
    subtitle: '支持 .json 和 .pack 格式文件，最大50MB',
    hint: '点击选择文件或将文件拖拽到此处'
  },
  fileInfo: {
    title: '文件信息',
    name: '文件名',
    size: '文件大小',
    type: '文件类型'
  },
  targetDirectory: {
    title: '目标目录',
    placeholder: '选择导入目录（可选）',
    hint: '留空则导入到工作空间根目录',
    root: '工作空间根目录'
  },
  validation: {
    title: '验证结果',
    valid: '✅ 内容包格式验证通过',
    invalid: '❌ 内容包格式验证失败',
    warning: '⚠️ 内容包存在一些问题',
    success: '内容包验证完成',
    packName: '内容包名称',
    language: '语言',
    totalCards: '总卡牌数',
    validCards: '有效卡牌数',
    errors: '验证错误'
  },
  errors: {
    invalidFile: '无效的文件格式，请选择 .json 或 .pack 文件',
    validationFailed: '内容包验证失败',
    validationError: '验证过程中发生错误',
    importFailed: '导入失败',
    importError: '导入过程中发生错误'
  },
  actions: {
    validate: '验证文件',
    import: '开始导入',
    cancel: '取消',
    refresh: '刷新'
  },
  importResult: {
    title: '导入结果',
    success: '成功导入 {count} 张卡牌',
    totalCards: '处理卡牌总数',
    language: '内容包语言',
    targetDirectory: '目标目录',
    logs: '导入日志'
  },
  language: {
    unknown: '未知'
  },
  // 新增的文本
  importWarning: '⚠️ 请谨慎操作！这个导入操作可能会覆盖工作空间中的某些配置和卡牌文件。建议在空目录中进行导入，或先备份重要数据。',
  importConfirm: {
    title: '重要提示',
    warning1: '• 请确保选择了正确的ArkhamDB内容包文件',
    warning2: '• 建议在空目录中执行导入操作',
    warning3: '• 导入的卡牌将覆盖同名的现有文件'
  },
  sampleCards: '示例卡牌',
  importing: '正在导入内容包...',
  importCompleted: '内容包导入完成',
  noLogs: '暂无日志信息',
  stopImport: '停止导入',
  close: '关闭'
};