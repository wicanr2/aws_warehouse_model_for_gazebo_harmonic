#!/usr/bin/env bash
# 遷移後 SDF 的「輕量靜態驗證」:只用 gz sdf 與 XML 解析,不跑物理/渲染 → CPU 吃很少,
# 本機可跑,也是 GitHub Actions 的第一道關。
#
# 檢查:
#   1) 14 個 model.sdf 通過 gz sdf -k(無 Error;Warning 只提示不擋)
#   2) 每個 world 是 XML 良構
#   3) world 裡每個 model:// 都對應得到本機 models/<name>/ 目錄
#
# 注意:gz sdf 無法解析 model://(那是 gz-sim 執行期 + GZ_SIM_RESOURCE_PATH 的功能,
#       獨立 sdformat 工具沒註冊 findFile callback)。world 是否真的能載入、include 是否
#       解析成功,由 CI 的 `gz sim` headless 載入把關(見 .github/workflows/validate.yml)。
#
# 用法:bash scripts/validate.sh

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GZ_SIM_RESOURCE_PATH="${ROOT}/models"
fail=0

echo "== 1) model.sdf(gz sdf -k)=="
for m in "${ROOT}"/models/*/model.sdf; do
  name="$(basename "$(dirname "$m")")"
  out="$(gz sdf -k "$m" 2>&1)"
  if echo "$out" | grep -qE 'Error Code'; then
    echo "  ✗ ${name}"; echo "$out" | grep 'Error Code' | sed 's/^/      /'; fail=1
  elif echo "$out" | grep -qi 'Warning'; then
    echo "  ⚠ ${name}(warning,不擋)"; echo "$out" | grep -i 'Warning' | sed 's/^/      /'
  else
    echo "  ✓ ${name}"
  fi
done

echo "== 2) world XML 良構 + model:// 路徑存在 =="
for w in "${ROOT}"/worlds/*.sdf; do
  wname="$(basename "$w")"
  if python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" "$w" 2>/tmp/xmlerr; then
    echo "  ✓ ${wname}(XML 良構)"
  else
    echo "  ✗ ${wname}(XML 壞)"; sed 's/^/      /' /tmp/xmlerr; fail=1
  fi
  for n in $(grep -ohE 'model://[A-Za-z0-9_]+' "$w" | sort -u | sed 's|model://||'); do
    if [ ! -d "${ROOT}/models/${n}" ]; then
      echo "  ✗ ${wname} 引用 model://${n},但缺 models/${n}/"; fail=1
    fi
  done
done

echo
if [ "$fail" -eq 0 ]; then echo "✅ 靜態驗證全部通過"; else echo "❌ 有錯誤(見上)"; fi
exit "$fail"
