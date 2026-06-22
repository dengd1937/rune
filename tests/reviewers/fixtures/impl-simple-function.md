实现一个 `sumSafe` 函数。

**文件**: `src/math.ts`

**需求**:
- 接收两个参数 `a: number`, `b: number`，返回它们的和
- 如果任一参数为 NaN，抛出 `TypeError("NaN is not allowed")`
- 如果结果溢出（超出 `Number.MAX_SAFE_INTEGER`），抛出 `RangeError("overflow")`

**测试文件**: `src/math.test.ts`
