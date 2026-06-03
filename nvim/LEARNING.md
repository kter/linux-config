# 学習メモ 2026-04-30

## TypeScript

### 型アサーション (`as`)

```typescript
const { sort, q: searchValue } = searchParams as { [key: string]: string };
```

- `as` で TypeScript に「この型として扱え」と強制する
- 実行時の保証はない——型で誤魔化しているだけ
- 安全にするなら `typeof x === 'string'` で実行時検証が必要

---

### インデックスシグネチャ

```typescript
{ [key: string]: string }
```

- 「どんな文字列キーでも受け付けるが、値は `string`」という型
- `key` という名前自体に意味はなく、慣習的な名前
- URL クエリパラメータのような動的なキーに使いやすい

---

### インターセクション型 (`&`)

```typescript
{ amount: string; currencyCode: string } & React.ComponentProps<"p">
```

- `A & B` で A **かつ** B の両方のプロパティを持つ型になる
- `A | B`（ユニオン型）は「どちらか」、`&` は「両方」
- React コンポーネントで独自 props に HTML 標準属性を追加するときによく使う

---

### ジェネリクスの型引数

```typescript
shopifyFetch<ShopifyProductsOperation>
React.ComponentProps<"p">
```

- `<...>` の中は「型の世界の引数」——実行時には存在しない
- 渡した型によって関数内の型が変わる
- `shopifyFetch` は渡した Operation 型から `variables` の型を自動で決定する

---

### 条件型 (`extends ? :`)

```typescript
type ExtractVariables<T> = T extends { variables: object }
  ? T["variables"]
  : never;
```

- 三項演算子の型版
- `T extends X` は「T が X の形をしているか？」という条件チェック
- `T["variables"]` はブラケット記法で型を取り出す（JS の `obj["key"]` の型版）
- `never` は「使用不可」を表す型

---

## Neovim / vim-surround

### `yst;"` の仕組み

```
ys  = surround オペレータ
t;  = ; の手前まで（till）
"   = 囲む文字
```

- `f;` は `;` を含む、`t;` は `;` の手前まで（含まない）
- `import lib/utils;` → `import "lib/utils";` にするときに使える

### テキストオブジェクトまとめ

| コマンド | 範囲 |
|----------|------|
| `iw` | 単語（空白なし） |
| `iW` | 空白区切りの塊（`/` 等を含む） |
| `t;` | `;` の手前まで |
| `f;` | `;` まで（含む） |

---

## TypeScript（続き）

### `[] as string[]` — 型アサーションで空配列の型を指定する

```typescript
const missingEnvironmentVariables = [] as string[];
```

- `[]` だけだと TypeScript は `never[]` と推論してしまう（要素がないためどんな型か不明）
- `as string[]` で「この配列には文字列を入れる」と明示する
- より一般的な書き方は `const arr: string[] = []`（型注釈）

---

### ジェネリクス関数のシグネチャ構造

```typescript
function shopifyFetch<T>({
  headers,
  query,
  variables,
}: {
  headers?: HeadersInit;
  query: string;
  variables?: ExtractVariables<T>;
}): Promise<{ status: number; body: T } | never>
```

- `<T>` — ジェネリクス（呼び出し側が型を指定する）
- `{ 値 }: { 型 }` — 分割代入と型定義がセット。`:` の左が値、右が型
- `Promise<T>` — 非同期の解決値の型。`await` したときに手に入る型が `T`
- `| never` — Union に `never` を含めると消える。意味はなく意図のコメント代わり

**構文まとめ：**
```
function 関数名<ジェネリクス>(引数: 引数の型): 戻り値の型
```

---

### `Promise<T>` と async 関数

```typescript
export async function getProductRecommendations(
  productId: string
): Promise<Product[]> {
  ...
  return reshapeProducts(...); // Product[] を return
}
```

- `async` 関数は `return` した値を自動的に `Promise` に包む
- `return Product[]` → 呼び出し側には `Promise<Product[]>` が届く
- `await` すると `Promise` が解けて `Product[]` が取り出せる

---

### クラスを型として使う

```typescript
export async function POST(req: NextRequest): Promise<NextResponse>
```

- TypeScript ではクラスは「値（インスタンス生成）」と「型」の2役を持つ
- `Promise<NextResponse>` は「NextResponse のインスタンスに解決される Promise」
- `NextResponse.json()` は静的メソッド。内部で `new NextResponse(...)` して返す

---

### `never` が戻り値の関数

```typescript
export declare function redirect(url: string, type?: RedirectType): never;
```

- 戻り値が `never` = 値を `return` することが絶対にない関数
- Next.js の `redirect()` は内部で例外をスローしてリダイレクトを実現する
- `| never`（Union の never）とは別物。こちらは「絶対に返らない」という意味

---

### Shopify GraphQL の Connection 型

```typescript
type Connection<T> = { edges: Array<Edge<T>> };
type Edge<T> = { node: T };
```

**型の入れ子構造：**
```
ShopifyCart.lines: Connection<CartItem>
  └── edges: Array<Edge<CartItem>>
                    └── node: CartItem
```

**実際のJSONデータ：**
```json
{
  "lines": {
    "edges": [
      { "node": { "id": "1", "quantity": 2 } },
      { "node": { "id": "2", "quantity": 1 } }
    ]
  }
}
```

- Relay 仕様由来の定番パターン（GitHub・Shopify など主要APIで採用）
- ページネーションの `cursor` を `edge` に付けられるためこの形になっている
- `removeEdgesAndNodes()` で `edges[].node` を取り出して `CartItem[]` に変換する
- `Cart` 型は `Omit<ShopifyCart, "lines"> & { lines: CartItem[] }` で `lines` を置き換えている

---

## Next.js

### 動的ルーティング `[param]`

```
app/search/[collection]/page.tsx
→ /search/shoes, /search/bags など任意URLにマッチ
```

- `[collection]` がパラメータ名
- `params.collection` でURLのその部分を取得できる
- Next.js 15 から `params` は `Promise<{ collection: string }>` になった

### ページコンポーネントの props

```typescript
export default async function CategoryPage(props: {
  params: Promise<{ collection: string }>;
  searchParams?: Promise<{ [key: string]: string | string[] | undefined }>;
})
```

- `params` / `searchParams` は Next.js が URL を解析して自動注入する
- 自分で渡す必要はない

---

## Neovim — node_modules へのジャンプ

- `gd`（LSP Definition）は `tsconfig.json` の `"exclude": ["node_modules"]` の影響でジャンプ不可
- これは正常な設定（含めると LSP が重くなる）
- 代替手段：`K` でホバーして型情報を確認する（ジャンプしなくても型は読める）

---

# 学習メモ 2026-05-01

## TypeScript — ジェネリクスと条件型の応用（`fetchGithub` を題材に）

### ジェネリクス制約 `<T extends X>`

```typescript
export const fetchGithub = async <T extends "commits" | "repo">(
  url: string,
  opts: Options<T>,
)
```

- `T extends "commits" | "repo"` は「T をこの2つに限定する」制約
- `Options<T>` の `fetchType: T` と連動し、渡した文字列リテラルで T が確定する
- 制約外の値（例：`"users"`）を渡すとコンパイルエラーになる

---

### `extends` の2つの使い方

| 文脈 | 意味 |
|---|---|
| `<T extends X>` | T を X の部分集合に制限する（ジェネリクス制約） |
| `T extends X ? A : B` | T が X に代入可能なら A、そうでなければ B（条件型） |

どちらも「T が X の形をしているか？」という代入可能性チェックが本質。

---

### 条件型で戻り値の型を切り替える

```typescript
): Promise<z.infer<
  T extends "repo" ? typeof repoSchema : typeof commitsSchema
> | null>
```

- `T extends "repo" ? typeof repoSchema : typeof commitsSchema` — 型レベルの三項演算子
- `z.infer<...>` — zodスキーマから TypeScript の型を自動導出
- `| null` — パース失敗時に `null` を返す可能性

結果：

```typescript
// fetchType: "repo" のとき
Promise<{ stargazers_count: number } | null>

// fetchType: "commits" のとき
Promise<Array<{ commit: { author: { date: string } }, author: { login: string, id: number } }> | null>
```

呼び出し側はキャストなしで正しい型が得られる。

---

## zod — 実行時バリデーションライブラリ

TypeScript の型はコンパイル時にしか存在しない。外部APIのレスポンスは実行時に来るため、型をつけても実際のデータが正しい保証がない。zodはその橋渡しをする。

### zod なし（危険）

```typescript
const data = await fetch(url).then(r => r.json()) as { stargazers_count: number };
// キャストだけ。実行時に number かどうか確認していない
console.log(data.stargazers_count + 1); // 実は文字列で "420001" になるかも
```

### zod あり（安全）

```typescript
const repoSchema = z.object({
  stargazers_count: z.number(),
});

const parsed = repoSchema.safeParse(data);

if (!parsed.success) {
  console.warn("予期しないレスポンス:", parsed.error);
  return null;
}

// parsed.data は型・実態ともに { stargazers_count: number } と保証済み
console.log(parsed.data.stargazers_count + 1); // 必ず number + 1 になる
```

### zod の主要メソッド

| メソッド | 動作 |
|---|---|
| `schema.parse(data)` | バリデーション失敗時に例外をスロー |
| `schema.safeParse(data)` | 失敗時に `{ success: false, error }` を返す（例外なし） |
| `z.infer<typeof schema>` | スキーマから TypeScript の型を導出 |

### zod ありとなしの差分

| | zod なし | zod あり |
|---|---|---|
| 型の保証 | コンパイル時のみ | コンパイル時 + 実行時 |
| 不正データ | 気づかず通過 | `safeParse` で検知 |
| 型定義 | 別途 `type` を書く | スキーマから自動生成 |
| APIの仕様変更 | 実行時に壊れるまで気づかない | バリデーション失敗で即検知 |
