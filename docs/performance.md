# 提出性能问题 → 查看执行计划 → 做一个调整 → 用相同查询验证 → 记录代价
## 一、准备 30 万条测试数据
创建 sql/performance/setup.sql
```
docker compose exec -T postgres  psql -U finflow -d finflow  < sql/performance/setup.sql
```
ANALYZE 会更新表统计信息，帮助优化器估算行数和选择执行计划。
## 二、先读懂 EXPLAIN ANALYZE
EXPLAIN 只估算计划；EXPLAIN ANALYZE 会真正执行语句。对 SELECT 通常没问题，但不要随意对 INSERT、UPDATE、DELETE 使用 ANALYZE，否则修改会真实发生
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    account_id,
    occurred_at,
    transaction_id,
    amount,
    transaction_type
FROM perf_transactions
WHERE account_id = 'A000001'
ORDER BY occurred_at DESC, transaction_id DESC
LIMIT 20;
"
```
指标或节点	含义
Seq Scan	顺序扫描表
Index Scan	通过索引定位记录，再读取表数据
Index Only Scan	查询所需字段可直接从索引获得
Bitmap Heap Scan	根据位图批量读取表数据
Sort	执行排序，可能消耗较多时间和内存
Rows Removed by Filter	读取后又过滤掉的行数
Execution Time	实际执行时间
shared read／hit	从磁盘读取／从缓存命中的块数

## 三、增加组合索引
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
CREATE INDEX idx_perf_account_time_covering
ON perf_transactions (
    account_id,
    occurred_at DESC,
    transaction_id DESC
)
INCLUDE (amount, transaction_type);
"
```
更新统计信息和可见性状态：
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "VACUUM ANALYZE perf_transactions;"
```
然后使用完全相同的查询再次执行 EXPLAIN (ANALYZE, BUFFERS)。
这个索引与查询的对应关系是：
查询条件：account_id
排序字段：occurred_at、transaction_id
返回字段：amount、transaction_type

组合索引：
```sql
(account_id, occurred_at DESC, transaction_id DESC)
```
覆盖字段：
```
INCLUDE (amount, transaction_type)
```
因此它同时尝试解决：
快速定位指定账户。
按索引顺序返回数据，尽量避免额外排序。
通过覆盖索引减少回表读取。
Index Only Scan 仍可能包含 Heap Fetch，不是创建了覆盖索引就一定完全无需访问表。
组合索引的最左前缀
对于：
sql
(account_id, occurred_at, transaction_id)
它通常适合：
sql
WHERE account_id = 'A000001'
以及：
sql
WHERE account_id = 'A000001'
  AND occurred_at >= ...
但不代表它同样适合只查询：
sql
WHERE occurred_at >= ...
因为没有提供第一列 account_id。优化器仍可能扫描整个索引或选择其他计划，需要以实际执行计划为准。
索引也不是越多越好：每个索引都会占用空间，并增加 INSERT、UPDATE、DELETE 的维护成本
四、避免对索引列随意套函数
先建立按时间排序的索引：
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
CREATE INDEX idx_perf_time_id_covering
ON perf_transactions (
    occurred_at DESC,
    transaction_id DESC
)
INCLUDE (account_id, amount);
"
```
写法一：对索引列进行类型转换
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
EXPLAIN (ANALYZE, BUFFERS)
SELECT transaction_id, occurred_at
FROM perf_transactions
WHERE occurred_at::date = DATE '2025-06-01';
"
```
这里实际过滤的是：
sql
CAST(occurred_at AS date)
普通 occurred_at 索引不能直接表达这个表达式的结果，因此通常需要额外过滤或扫描更多数据。
写法二：改成时间范围
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
EXPLAIN (ANALYZE, BUFFERS)
SELECT transaction_id, occurred_at
FROM perf_transactions
WHERE occurred_at >= TIMESTAMPTZ '2025-06-01 00:00:00+00'
  AND occurred_at <  TIMESTAMPTZ '2025-06-02 00:00:00+00'
ORDER BY occurred_at DESC, transaction_id DESC;
"
```
范围条件直接作用于原始索引列：
sql
occurred_at >= 起始时间
AND occurred_at < 第二天起始时间
使用“左闭右开”区间也能避免 BETWEEN 把第二天零点误算进来。
如果业务确实必须频繁按表达式查询，可以评估表达式索引，但不能把它当成所有写法随意的补救措施。
## 五、对比深分页与游标分页
1. OFFSET 深分页
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    transaction_id,
    occurred_at,
    account_id,
    amount
FROM perf_transactions
ORDER BY occurred_at DESC, transaction_id DESC
OFFSET 50000
LIMIT 20;
"
```
即使使用了索引，数据库通常仍需要按顺序经过前面的 50,000 条，再返回最后 20 条。
页码越靠后，成本通常越高：
Text
OFFSET 20       经过约 40 条
OFFSET 50000    经过约 50,020 条
2. 找到实验用游标
为了模拟第 50,000 条之后的一页，先取得锚点：
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
SELECT occurred_at, transaction_id
FROM perf_transactions
ORDER BY occurred_at DESC, transaction_id DESC
OFFSET 49999
LIMIT 1;
"
```
记录输出的时间和交易 ID。
3. 使用游标查询下一页
把下面的时间和 ID 替换成刚才的实际结果：
```
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    transaction_id,
    occurred_at,
    account_id,
    amount
FROM perf_transactions
WHERE (occurred_at, transaction_id) < (
    TIMESTAMPTZ '替换为游标时间',
    '替换为游标交易ID'
)
ORDER BY occurred_at DESC, transaction_id DESC
LIMIT 20;
"
```
真实应用不应该先执行一次 OFFSET 49999 来找游标。这里只是为了实验。正常流程是：
第一页按排序查询 20 条。
保存本页最后一条的 occurred_at 和 transaction_id。
下一页以这两个值作为游标继续查询。
因为 occurred_at 可能重复，所以需要唯一的 transaction_id 作为第二排序字段，否则翻页时可能遗漏或重复数据。
游标分页的代价是：不适合直接跳到任意页码，但非常适合“下一页”“加载更多”和无限滚动。
## 六、记录真实的调优证据
建议新建 docs/day-10-sql-tuning.md，记录：
Markdown
复制
代码
预览
### 查询一：账户最近交易

数据量：300,000

优化前：
- 主要扫描节点：
- Execution Time：
- Buffers：
- 是否额外排序：

优化后：
- 主要扫描节点：
- Execution Time：
- Buffers：
- 是否额外排序：

新增索引：
- 索引定义：
- 对写入和存储的潜在代价：

### 深分页与游标分页

- OFFSET 50000 的执行时间和扫描情况：
- 游标分页的执行时间和扫描情况：
每个查询可以重复执行两三次，避免把首次磁盘读取或偶然波动误判为索引收益。也不要只比较毫秒数，还要比较扫描节点、返回行数和 Buffers。
## 七、今天验收
你应该能解释：
为什么小表上加索引未必更快？
表很小时，顺序扫描的成本可能比访问索引再访问表更低，优化器会综合估算。
什么是组合索引的最左前缀？
查询是否提供组合索引前面的列，会影响索引能否被高效用于定位。
覆盖索引为什么仍需控制字段数量？
覆盖字段越多，索引越大，写入维护和存储成本越高。
为什么范围条件通常比 occurred_at::date 更友好？
范围条件直接作用于原始索引列，更容易利用普通索引。
为什么深分页需要唯一排序字段？
仅按可能重复的时间排序，页与页之间的顺序不稳定，容易重复或遗漏。
练习完成后，可以删除性能测试表：
bash
docker compose exec postgres psql \
  -U finflow -d finflow \
  -c "DROP TABLE IF EXISTS perf_transactions;"
删除前先保存执行计划和调优笔记。