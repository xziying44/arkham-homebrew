// 内容包类型定义文件

/**
 * 内容包元数据
 */
export interface ContentPackageMeta {
  code: string;           // UUID生成的唯一标识ID
  name: string;           // 名称
  description: string;    // 描述内容
  author: string;         // 作者
  language: 'zh' | 'en';  // 语言
  banner_url: string;     // 封面URL
  types: PackageType[];   // 内容包类型
  status: 'draft' | 'final'; // 状态，默认为final
  date_updated: string;   // 标准时间字符串
  generator: string;      // 导出备注信息，默认为"Arkham Card Maker 3.9"
  external_link?: string; // 外部地址（可选）
}

/**
 * 内容包数据结构
 */
export interface ContentPackage {
  meta: ContentPackageMeta;
  banner_base64: string;  // 封面base64数据
}

/**
 * 内容包类型枚举
 */
export type PackageType = 'investigators' | 'player_cards' | 'campaign';

/**
 * 内容包文件信息
 */
export interface ContentPackageFile {
  name: string;
  path: string;
  meta: ContentPackageMeta;
  banner_base64: string;
}

/**
 * 新建内容包表单数据
 */
export interface CreatePackageForm {
  name: string;
  description: string;
  author: string;
  language: 'zh' | 'en';
  types: PackageType[];
  external_link: string;
  banner_url: string;
  banner_base64: string;
}

/**
 * 内容包表单验证规则
 */
export interface PackageFormRules {
  name: string;
  description: string;
  author: string;
  language: string;
  types: string;
}

/**
 * 默认内容包元数据
 */
export const createDefaultMeta = (): ContentPackageMeta => ({
  code: '',
  name: '',
  description: '',
  author: '',
  language: 'zh',
  banner_url: '',
  types: [],
  status: 'final',
  date_updated: new Date().toISOString(),
  generator: 'Arkham Card Maker 3.9'
});

/**
 * 默认内容包数据
 */
export const createDefaultPackage = (): ContentPackage => ({
  meta: createDefaultMeta(),
  banner_base64: ''
});

/**
 * 内容包类型选项
 */
export const PACKAGE_TYPE_OPTIONS = [
  { label: '调查员卡', value: 'investigators' as PackageType },
  { label: '玩家卡', value: 'player_cards' as PackageType },
  { label: '剧本卡', value: 'campaign' as PackageType }
];

/**
 * 语言选项
 */
export const LANGUAGE_OPTIONS = [
  { label: '中文', value: 'zh' as const },
  { label: '英文', value: 'en' as const }
];