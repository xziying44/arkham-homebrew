# 玩家卡自动编号排序修复 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复内容包自动编号中玩家卡的排序规则，使其支持固定职阶顺序、调查员与签名卡相邻、同职阶按等级排序、Bonded 卡跟随主卡。

**Architecture:** 在 `bin/card_numbering.py` 中增加玩家卡专用排序层，仅影响无遭遇组卡牌的排序。签名卡关联优先从 `tts_config.signatures` 和稳定脚本 ID / 文件路径建立，Bonded 关联优先读取显式字段并提供保守回退，原有遭遇组编号和应用编号逻辑保持不变。

**Tech Stack:** Python 3、unittest、现有内容包编号服务

---

### Task 1: 补玩家卡排序失败测试

**Files:**
- Create: `tests/test_card_numbering.py`
- Modify: `bin/card_numbering.py`
- Test: `tests/test_card_numbering.py`

**Step 1: Write the failing test**

```python
def test_player_cards_follow_fixed_class_order():
    ...

def test_investigator_is_followed_by_signature_cards():
    ...

def test_bonded_cards_follow_their_parent_card():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_card_numbering.py`
Expected: FAIL，显示当前排序与预期不一致。

**Step 3: Write minimal implementation**

在 `bin/card_numbering.py` 中新增：

- 玩家卡识别函数
- 职阶优先级函数
- 稳定卡牌标识提取函数
- 签名卡 / Bonded 关系构建函数
- 玩家卡排序函数

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_card_numbering.py`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_card_numbering.py bin/card_numbering.py
git commit -m "fix: 修复玩家卡自动编号排序规则"
```

### Task 2: 回归现有测试

**Files:**
- Modify: `bin/card_numbering.py`
- Test: `tests/test_image_uploader_public_id.py`
- Test: `tests/test_workspace_path_normalization.py`
- Test: `tests/test_large_player_card_type_labels.py`
- Test: `tests/test_card_numbering.py`

**Step 1: Run related tests**

Run: `python3 -m unittest tests/test_card_numbering.py tests/test_image_uploader_public_id.py tests/test_workspace_path_normalization.py tests/test_large_player_card_type_labels.py`

Expected: PASS

**Step 2: Check diff**

Run: `git diff -- bin/card_numbering.py tests/test_card_numbering.py`

Expected: 只包含玩家卡排序修复与测试。

**Step 3: Commit**

```bash
git add bin/card_numbering.py tests/test_card_numbering.py
git commit -m "fix: 修复玩家卡自动编号排序规则"
```
