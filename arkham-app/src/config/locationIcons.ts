// Mapping between Chinese icon names and SVG filenames (without .svg)
export const LOCATION_ICON_MAP: Record<string, string> = {
  '绿菱': 'diamond',
  '暗红漏斗': 'hourglass',
  '橙心': 'heart',
  '浅褐水滴': 'blob',
  '深紫星': 'star',
  '深绿斜二': 'equals',
  '深蓝T': 'T',
  '紫月': 'crescent',
  '红十': 'plus',
  '红方': 'square',
  '蓝三角': 'triangle',
  '褐扭': 'wave',
  '青花': '3circles',
  '黄圆': 'circle',
  '粉桃': 'spades',
};

export const getIconKeyByChinese = (name: string): string | null => {
  if (!name) return null;
  return LOCATION_ICON_MAP[name] || null;
};

export const getIconUrlByChinese = (name: string): string | null => {
  const key = getIconKeyByChinese(name);
  if (!key) return null;
  // Vite asset resolving
  return new URL(`../assets/location-icons/${key}.svg`, import.meta.url).href;
};

