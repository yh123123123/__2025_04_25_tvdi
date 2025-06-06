# TVdi 卡片網格組件技術需求

## 專案概述
基於 Figma 設計稿實現卡片網格佈局組件，包含圖示、標題和描述文字的卡片設計，作為網頁內容的局部元素使用。

## 設計規格分析

### 組件結構
- **組件名稱**: 卡片網格 (Card Grid)
- **組件類型**: 響應式卡片佈局
- **容器寬度**: 1129px (桌面版)
- **容器內距**: 64px
- **卡片數量**: 6張卡片 (2行3列)

### 卡片設計規格

#### 單張卡片
- **卡片寬度**: 301.33px (桌面版)
- **佈局方向**: 水平排列 (圖示 + 文字內容)
- **內部間距**: 24px (圖示與文字間距)
- **背景色**: `#FFFFFF` (白色)

#### 圖示區域
- **尺寸**: 32px × 32px
- **圖示顏色**: `#1E1E1E` (深灰色)
- **線條粗細**: 3px
- **圖示類型**: SVG 向量圖示

#### 文字內容區域
- **標題文字**:
  - 字體: Inter Semi-Bold (600)
  - 字體大小: 24px
  - 行高: 1.2
  - 字間距: -2%
  - 顏色: `#1E1E1E` (深灰色)
  - 內容: "Title"

- **描述文字**:
  - 字體: Inter Regular (400)
  - 字體大小: 16px
  - 行高: 1.4
  - 顏色: `#757575` (中灰色)
  - 內容: "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story."

#### 佈局間距
- **卡片間距**: 64px (水平和垂直)
- **標題與描述間距**: 8px
- **圖示與文字區域間距**: 24px

## 技術規格

### HTML 結構
```html
<div class="card-grid-container">
  <div class="card-grid">
    <div class="card">
      <div class="card-icon">
        <svg><!-- 圖示內容 --></svg>
      </div>
      <div class="card-content">
        <h3 class="card-title">Title</h3>
        <p class="card-description">Body text for whatever you'd like to say...</p>
      </div>
    </div>
    <!-- 重複 5 次 -->
  </div>
</div>
```

### RWD 響應式設計

#### 斷點設定
- **桌面版**: >= 1024px
- **平板版**: 768px - 1023px
- **手機版**: < 768px

#### 網格佈局適配
1. **桌面版**: 3列2行
   - 卡片寬度: 301.33px
   - 間距: 64px

2. **平板版**: 2列3行
   - 卡片寬度: 自動填充
   - 間距: 32px

3. **手機版**: 1列6行
   - 卡片寬度: 100%
   - 間距: 24px

#### 字體大小適配
- **桌面版**:
  - 標題: 24px
  - 描述: 16px

- **平板版**:
  - 標題: 20px
  - 描述: 14px

- **手機版**:
  - 標題: 18px
  - 描述: 14px

## 開發規範

### CSS 技術要求
- 使用 CSS Grid 或 Flexbox 實現響應式佈局
- 不使用 CSS 變數，直接寫入數值
- 實現平滑的響應式過渡效果
- 支援觸控設備的 hover 效果

### 圖示處理
- 使用 SVG 格式確保清晰度
- 支援動態替換圖示
- 圖示採用 inline SVG 或 icon font

### 瀏覽器支援
- Chrome/Safari/Firefox 最新版本
- Edge 最新版本
- iOS Safari 14+
- Android Chrome 90+

## 內容管理

### 動態內容支援
- 標題文字可自定義
- 描述文字可自定義
- 圖示可替換
- 支援不同數量的卡片

### 無障礙設計
- 語義化 HTML 標籤
- 圖示提供 alt 描述
- 適當的對比度
- 鍵盤導航支援

## 測試要求

### 功能測試
- [ ] 卡片內容顯示正常
- [ ] 圖示載入正確
- [ ] 文字內容換行正常

### 響應式測試
- [ ] 桌面版 3x2 網格正常
- [ ] 平板版 2x3 網格正常
- [ ] 手機版 1x6 網格正常
- [ ] 間距和字體大小適配正確

### 跨瀏覽器測試
- [ ] Chrome 測試通過
- [ ] Safari 測試通過
- [ ] Firefox 測試通過
- [ ] Edge 測試通過

## 使用方式
組件設計為獨立模組，可通過以下方式整合：
1. 直接嵌入現有網頁
2. 作為 React/Vue 組件
3. 整合至 CMS 系統

## 備註
- 設計稿顯示 6 張相同的卡片作為示例
- 圖示為通用資訊圖示，可根據實際需求替換
- 描述文字較長，需要考慮文字截斷或自動換行
- 卡片背景為白色，適合放置在淺色背景上
