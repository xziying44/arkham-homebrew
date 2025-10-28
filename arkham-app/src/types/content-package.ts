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
  status: 'draft' | 'alpha' | 'beta' | 'complete' | 'final'; // 状态，默认为final
  date_updated: string;   // 标准时间字符串
  generator: string;      // 导出备注信息，默认为"Arkham Card Maker 3.9"
  external_link?: string; // 外部地址（可选）
}

/**
 * 内容包卡牌信息
 */
export interface ContentPackageCard {
  filename: string;    // 相对于工作目录的文件名
  version?: string;    // 卡牌版本号（读取自卡牌文件）
  front_url?: string;  // 卡牌正面图片URL（本地file://或远程http://）
  back_url?: string;   // 卡牌背面图片URL（本地file://或远程http://）
  original_front_url?: string;
  original_back_url?: string;
  front_thumbnail_url?: string;
  back_thumbnail_url?: string;
  permanent?: boolean; // 永久卡牌
  exceptional?: boolean; // 卓越卡牌
  myriad?: boolean;    // 无数卡牌
  exile?: boolean;     // 可放逐
}

/**
 * 内容包数据结构
 */
export interface ContentPackage {
  meta: ContentPackageMeta;
  banner_base64: string;  // 封面base64数据
  cards?: ContentPackageCard[]; // 卡牌列表
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
  cards?: ContentPackageCard[]; // 卡牌列表
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
  banner_base64: '',
  cards: []
});

/**
 * 生成内容包类型选项（支持本地化）
 */
export const getPackageTypeOptions = (t: (key: string) => string) => [
  { label: t('contentPackage.packageTypes.investigators'), value: 'investigators' as PackageType },
  { label: t('contentPackage.packageTypes.player_cards'), value: 'player_cards' as PackageType },
  { label: t('contentPackage.packageTypes.campaign'), value: 'campaign' as PackageType }
];

/**
 * 生成语言选项（支持本地化）
 */
export const getLanguageOptions = (t: (key: string) => string) => [
  { label: t('contentPackage.languages.zh'), value: 'zh' as const },
  { label: t('contentPackage.languages.en'), value: 'en' as const }
];

/**
 * 生成状态选项（支持本地化）
 */
export const getStatusOptions = (t: (key: string) => string) => [
  { label: t('contentPackage.statusOptions.draft'), value: 'draft' as const },
  { label: t('contentPackage.statusOptions.alpha'), value: 'alpha' as const },
  { label: t('contentPackage.statusOptions.beta'), value: 'beta' as const },
  { label: t('contentPackage.statusOptions.complete'), value: 'complete' as const },
  { label: t('contentPackage.statusOptions.final'), value: 'final' as const }
];

/**
 * 内容包类型选项（向后兼容的静态版本）
 */
export const PACKAGE_TYPE_OPTIONS = [
  { label: '调查员卡', value: 'investigators' as PackageType },
  { label: '玩家卡', value: 'player_cards' as PackageType },
  { label: '剧本卡', value: 'campaign' as PackageType }
];

/**
 * 语言选项（向后兼容的静态版本）
 */
export const LANGUAGE_OPTIONS = [
  { label: '中文', value: 'zh' as const },
  { label: '英文', value: 'en' as const }
];

/**
 * 状态选项（向后兼容的静态版本）
 */
export const STATUS_OPTIONS = [
  { label: '草稿', value: 'draft' as const },
  { label: 'Alpha版', value: 'alpha' as const },
  { label: 'Beta版', value: 'beta' as const },
  { label: '完成版', value: 'complete' as const },
  { label: '最终版', value: 'final' as const }
];