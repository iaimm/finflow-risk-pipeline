一、每日交易汇总
目标：按天统计交易数、活跃账户数、总金额、支出、收入和净额。
创建 sql/reports/daily_transaction_summary.sql：

docker compose exec -T postgres  psql -U finflow -d finflow  < sql/reports/daily_transaction_summary.sql

二、客户累计交易额
目标：先计算每个客户每天的交易额，再按日期累计。
创建 sql/reports/customer_cumulative_amount.sql

docker compose exec -T postgres  psql -U finflow -d finflow  < sql/reports/customer_cumulative_amount.sql

CTE 主要提升可读性，不保证查询一定更快。

三、账户交易排名
目标：按账户累计交易总额从高到低排名。
创建 sql/reports/account_transaction_ranking.sql

docker compose exec -T postgres  psql -U finflow -d finflow  < sql/reports/account_transaction_ranking.sql

三种排名函数的区别
函数 	并列时的行为 
ROW_NUMBER()	强制给不同序号，例如 1、2、3、4
RANK()	并列后跳号，例如 1、2、2、4
DENSE_RANK()	并列后不跳号，例如 1、2、2、3
当前使用 RANK()，表示两个账户总额相同时，它们获得相同名次。

四、验证报表是否对得上
报表不能只满足于“SQL 能运行”，还要与源数据对账。
先查询交易总数和总金额：

docker compose exec postgres psql  -U finflow  -d finflow  -c "SELECT COUNT(*), SUM(amount) FROM transactions;"

然后检查：
每日汇总的 transaction_count 相加，应等于交易总数。
每日汇总的 total_amount 相加，应等于交易总金额。
每日汇总的 debit_amount + credit_amount，应等于 total_amount。
客户每日交易额全部相加，应等于交易总金额。
每个有交易的账户在排名报表中只出现一次。
排名报表的 total_amount 相加，应等于交易总金额。
如果源数据为 100 笔交易，这些报表最终都应覆盖同样的 100 笔交易，不能因为 JOIN 错误而增加或丢失交易。

五、进阶练习：包含没有交易的账户
当前排名使用 JOIN，所以没有交易的账户不会出现。
如果希望所有账户都出现，可以把账户与交易之间改成：
sql
LEFT JOIN transactions AS t
    ON t.account_id = a.account_id
并使用：
sql
COUNT(t.transaction_id) AS transaction_count,
COALESCE(SUM(t.amount), 0) AS total_amount
原因是：
COUNT(t.transaction_id) 不会把左连接产生的空交易行算成一笔交易。
没有交易时，SUM(t.amount) 返回 NULL，需要用 COALESCE 转为零。
六、今天验收
你应该能回答：
INNER JOIN 和 LEFT JOIN 对报表行数有什么影响？
为什么 GROUP BY 和窗口函数都可以求和，但结果行数不同？
PARTITION BY 与 GROUP BY 的区别是什么？
RANK() 和 DENSE_RANK() 有什么区别？
为什么报表必须验证交易笔数和金额，而不仅是检查 SQL 能否执行？
完成后提交：
bash
git add sql
git commit -m "feat: add daily cumulative and account ranking reports"
git push