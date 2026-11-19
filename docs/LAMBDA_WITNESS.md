# Lambda 见证清单（从 `replica/src` 迁出，R1272）

原先在 `replica/src/Cybersole.Stores/Flows/LambdaWitness.cs`。它全部是记账——没有协议常量、没有运行时行为，
`HasWitness` / `ExaminedCount` 也只有它自己的测试在用。按 `AGENTS.md` §3，这类内容归 `docs/`。

## 一、什么算「见证」

原版把每个流程的步骤表塞进一个 **lambda 字面量**里，字面量同时携带该流程自己的 **ordinal 范围**。
所以「某个流程的表在哪」这个问题，只有在一个字面量的 **ordinal 与流程序号对得上**时才算被见证。

## 二、已见证（ordinal 区间对得上）

| 流程 | ordinal 区间 |
|---|---|
| `johnlewis` | 20 – 39 |
| `nike` | 41 – 58 |

## 三、未见证（缺口保持未解）

```
popmart
demandware-classic
demandware-dual
collectplus-app
structure-token-multi
structure-token-single
```

共 **6** 个；连同上面 2 个，一轮里考察过 **8** 个流程。

## 四、为什么「名字出现」不能当证据（R122 的例子）

> 步骤名在不同类之间会重复。一个提到某流程三个步骤名的 lambda 字面量，
> **仍然可能不是那个流程的表**——除非它的 ordinal 与流程对得上。

`Authorize` 在 ordinal 1 上就是 R122 抓到的那个例子。

## 五、这条对 Pop Mart 的意义

Pop Mart 有**两半**：抽签类那半 24 步，另一半走 `/shop/v1/*` 家族
（`cartDataList`、`couponsList`、优惠券提交、地址获取）——**这一半做的是「买」，不是「抽」**。
把两半混成一份表，就会像 R842 那次一样把「加多盒」误认成「通用多件」（见 `docs/ADD_TO_CART_COVERAGE.md`）。

## 六、怎么复算

「某流程的步骤表被见证了吗」不是跑一个脚本能答的，它要读镜像里的 lambda 字面量并比对 ordinal：

```
python analysis\ida.py str "<流程的步骤名>" --limit N     # 找到候选字面量
python analysis\names_at.py <off_va...>                   # 解出它带的 ordinal 序列
```

**名字命中不算见证，ordinal 对上才算。**

## 七、Pop Mart「买」的那半：六个方法（R122 扫出来的）

原先是 `LambdaWitness.cs` 里的第二个类 `PopMartCartSteps`，与本文件同批迁出。

```
1 GetCartDataList   2 FetchCoupons   3 SubmitDiscount
4 ClearCart         5 FetchAddress   6 FetchAddress   （两个 ordinal，同一个名字）
```

名字与家族已带的端点对得上：`cartDataList`、`couponsList`、优惠券提交、地址获取。

**`FetchAddress` 出现在两个 ordinal 上，按两条保留**——同名两个方法就是重载，合并会把一个方法藏起来。

> `ClearCart` / `FetchAddress` 在表里，但**没有端点服务它们**，所以 `PopMartFlow` **不实现**这两个方法。
> 这条由 `PopMartCartWiringTests.TheUnservableMethodsAreAbsent` 断言（断言的是**流程不实现**，
> 不是"表里有几行"）。
