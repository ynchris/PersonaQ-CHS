# 女神异闻录Q 汉化补丁：把同一文件夹里的日版本体(.3ds)、更新(.cia)、DLC(.cia)打成中文 CIA。
# 原文件不会被修改。所有中间文件放在 _work，输出放在 输出 文件夹。
$ErrorActionPreference = 'Stop'
$Tools = $PSScriptRoot
$Root = Split-Path $Tools -Parent
$Work = Join-Path $Root '_work'
$Out = Join-Path $Root '输出'
$Log = Join-Path $Root '补丁日志.txt'
$M = Get-Content (Join-Path $Root 'patches\manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$CTR = Join-Path $Tools 'ctrtool.exe'; $T3 = Join-Path $Tools '3dstool.exe'
$MK = Join-Path $Tools 'makerom.exe'; $XD = Join-Path $Tools 'xdelta3-3.1.0-x86_64.exe'

function Say($s, $c = 'Gray') { Write-Host $s -ForegroundColor $c; Add-Content $Log $s -Encoding UTF8 }
function Fail($s) { throw $s }
function Sha($p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
function Run($exe, [string[]]$argv) {
    $q = ($argv | ForEach-Object { '"' + $_ + '"' }) -join ' '
    $o = Join-Path $Work 'stdout.txt'; $e = Join-Path $Work 'stderr.txt'
    $p = Start-Process -FilePath $exe -ArgumentList $q -Wait -PassThru -NoNewWindow -RedirectStandardOutput $o -RedirectStandardError $e
    $text = (Get-Content $o -Raw) + (Get-Content $e -Raw)
    Add-Content $Log ("> " + (Split-Path $exe -Leaf) + " " + $q + "`n" + $text) -Encoding UTF8
    if ($p.ExitCode -ne 0) { Fail ("工具运行失败：" + (Split-Path $exe -Leaf) + "（详见 补丁日志.txt）") }
    return $text
}
# 大文件优先用硬链接放进 _work（不占空间、路径只含英文），不行再复制
function Stage($src, $name) {
    $dst = Join-Path $Work $name
    try { New-Item -ItemType HardLink -Path $dst -Target $src | Out-Null } catch { Copy-Item -LiteralPath $src $dst }
    return $dst
}

# 解包一个 CIA，逐个内容解密、校验、打补丁，再封回 CIA
function Patch-Cia($cia, $info, $tag, $isDlc) {
    $dir = Join-Path $Work $tag; New-Item -ItemType Directory $dir | Out-Null
    Run $CTR @('-q', "--contents=$dir\c", $cia) | Out-Null
    $files = Get-ChildItem $dir -Filter 'c.*'
    if (-not $files) { Fail "$tag：无法读取 CIA 内容。文件可能损坏，或带有本工具无法解开的加密。" }
    $content = @(); $done = @()
    foreach ($f in $files) {
        $idx = $f.Name.Split('.')[1]; $cid = $f.Name.Split('.')[2]
        $row = $info.contents | Where-Object { $_.index -eq $idx }
        if (-not $row) { Fail "$tag：发现未知内容 $idx，不是对应版本的文件。" }
        $sec = Join-Path $dir $idx; New-Item -ItemType Directory $sec | Out-Null
        $names = @('romfs'); if ($row.kind -eq 'cxi') { $names += @('exefs', 'exh', 'logo', 'plain') }
        $a = @('-xtf', $row.kind, $f.FullName, '--header', "$sec\header.bin")
        foreach ($n in $names) { $a += @("--$n", "$sec\$n.bin") }
        Run $T3 $a | Out-Null
        $dec = Join-Path $dir "$idx.dec.$($row.kind)"
        $a = @('-ctf', $row.kind, $dec, '--header', "$sec\header.bin", '--not-encrypt')
        foreach ($n in $names) { $p = "$sec\$n.bin"; if ((Test-Path $p) -and (Get-Item $p).Length -gt 0) { $a += @("--$n", $p) } }
        Run $T3 $a | Out-Null
        Remove-Item $sec -Recurse; Remove-Item $f.FullName
        if ((Sha $dec) -ne $row.decrypted_sha256) { Fail "$tag：内容 $idx 解密后与日版原始数据不符。请确认是日版 v$($info.version) 的原始文件。" }
        $final = $dec
        if ($row.patch) {
            $final = Join-Path $dir "$idx.chs.$($row.kind)"
            Run $XD @('-d', '-f', '-s', $dec, (Join-Path $Root "patches\$($row.patch)"), $final) | Out-Null
            Remove-Item $dec
        }
        if ((Sha $final) -ne $row.final_sha256) { Fail "$tag：内容 $idx 打补丁后校验失败。" }
        $content += @('-content', ("{0}:{1}:{2}" -f $final, [Convert]::ToInt32($idx, 16), [Convert]::ToInt64($cid, 16)))
        $done += $row
    }
    $tmp = Join-Path $Work "$tag.cia"
    $a = @('-f', 'cia', '-o', $tmp, '-ver', "$($info.version)", '-ignoresign'); if ($isDlc) { $a += '-dlc' }
    Run $MK ($a + $content) | Out-Null
    Check-Cia $tmp $done $tag
    Remove-Item $dir -Recurse
    $script:CiaOut = $tmp; $script:CiaRows = $done
}
# 重新解出新 CIA 的内容，逐个比对哈希
function Check-Cia($cia, $rows, $tag) {
    $chk = Join-Path $Work "$tag.check"; New-Item -ItemType Directory $chk | Out-Null
    Run $CTR @('-q', "--contents=$chk\c", $cia) | Out-Null
    foreach ($r in $rows) {
        $f = Get-ChildItem $chk -Filter "c.$($r.index).*" | Select-Object -First 1
        if (-not $f -or (Sha $f.FullName) -ne $r.final_sha256) { Fail "$tag：生成的 CIA 复查失败（内容 $($r.index)）。" }
    }
    Remove-Item $chk -Recurse
}

try {
    Set-Content $Log "女神异闻录Q 汉化补丁 $($M.revision)  $(Get-Date)" -Encoding UTF8
    Say "女神异闻录Q 汉化补丁（版本 $($M.revision)）" 'Cyan'
    if (Test-Path $Work) { Remove-Item $Work -Recurse -Force }
    New-Item -ItemType Directory $Work | Out-Null; New-Item -ItemType Directory $Out -Force | Out-Null
    $free = (Get-PSDrive ((Get-Item $Root).PSDrive.Name)).Free
    if ($free -lt 6GB) { Fail ("硬盘剩余空间不足：需要至少 6 GB，目前只有 {0:N1} GB。" -f ($free / 1GB)) }

    Say "正在识别游戏文件……"
    $base = $null; $upd = $null; $dlc = $null
    foreach ($f in Get-ChildItem -LiteralPath $Root -File | Where-Object { $_.Extension -in '.3ds', '.cci', '.cia' }) {
        if ($f.Extension -ne '.cia') {
            if ((Sha $f.FullName) -eq $M.base.rom_sha256) { $base = $f; Say "  本体：$($f.Name)" 'Green' }
            else { Say "  跳过 $($f.Name)：不是本补丁支持的日版解密 .3ds（SHA256 不符）。" 'Yellow' }
            continue
        }
        $t = Stage $f.FullName 'probe.cia'
        $i = (Run $CTR @('-i', $t)).ToLower(); Remove-Item $t
        if ($i -match $M.update.title_id) { $upd = $f; Say "  更新：$($f.Name)" 'Green' }
        elseif ($i -match $M.dlc.title_id) { $dlc = $f; Say "  DLC：$($f.Name)" 'Green' }
        else { Say "  跳过 $($f.Name)：不是女神异闻录Q 日版的更新或 DLC。" 'Yellow' }
    }
    if (-not ($base -or $upd -or $dlc)) { Fail "没有找到可用的游戏文件。请把日版 .3ds、更新 .cia、DLC .cia 放在本文件夹（和 一键打补丁.bat 同一层）。" }
    if ($base -and -not $upd) { Say "  注意：没有找到更新 2.3.0。只装本体的话，部分界面文字（程序内文字）以更新为准，建议一起打补丁。" 'Yellow' }
    $made = @()

    if ($base) {
        Say "[本体] 正在打补丁（约需几分钟）……"
        $rom = Stage $base.FullName 'base.3ds'
        $p0 = Join-Path $Work 'p0.cxi'; $p1 = Join-Path $Work 'p1.cfa'
        Run $T3 @('-xtf', 'cci', $rom, '--partition0', $p0, '--partition1', $p1) | Out-Null
        Remove-Item $rom
        if ((Sha $p0) -ne $M.base.partition0_sha256 -or (Sha $p1) -ne $M.base.manual_sha256) { Fail "[本体] 解包后的数据与预期不符。" }
        $chs = Join-Path $Work 'base_chs.cxi'
        Run $XD @('-d', '-f', '-s', $p0, (Join-Path $Root "patches\$($M.base.patch)"), $chs) | Out-Null
        Remove-Item $p0
        if ((Sha $chs) -ne $M.base.localized_sha256) { Fail "[本体] 打补丁后校验失败。" }
        $tmp = Join-Path $Work 'base.cia'
        Run $MK @('-f', 'cia', '-o', $tmp, '-ver', "$($M.base.version)", '-ignoresign', '-content', "${chs}:0:0", '-content', "${p1}:1:1") | Out-Null
        Remove-Item $chs, $p1
        Check-Cia $tmp @([pscustomobject]@{ index = '0000'; final_sha256 = $M.base.localized_sha256 }, [pscustomobject]@{ index = '0001'; final_sha256 = $M.base.manual_sha256 }) 'base'
        $name = "PQ1_CHS_$($M.revision)_本体.cia"; Move-Item $tmp (Join-Path $Out $name) -Force; $made += $name
        Say "[本体] 完成" 'Green'
    }
    if ($upd) {
        Say "[更新] 正在打补丁……"
        Patch-Cia (Stage $upd.FullName 'update_in.cia') $M.update 'update' $false
        if (@($script:CiaRows).Count -ne $M.update.contents.Count) { Fail "[更新] 内容不完整，不是完整的 2.3.0 更新文件。" }
        $name = "PQ1_CHS_$($M.revision)_更新.cia"; Move-Item $script:CiaOut (Join-Path $Out $name) -Force; $made += $name
        Say "[更新] 完成" 'Green'
    }
    if ($dlc) {
        Say "[DLC] 正在打补丁……"
        Patch-Cia (Stage $dlc.FullName 'dlc_in.cia') $M.dlc 'dlc' $true
        $name = "PQ1_CHS_$($M.revision)_DLC.cia"; Move-Item $script:CiaOut (Join-Path $Out $name) -Force; $made += $name
        Say ("[DLC] 完成（包含 {0}/{1} 个内容）" -f @($script:CiaRows).Count, $M.dlc.contents.Count) 'Green'
    }
    Remove-Item $Work -Recurse -Force
    Say ""
    Say "全部完成！已在 输出 文件夹生成：" 'Cyan'
    foreach ($n in $made) { Say "  $n" 'Cyan' }
    Say "原文件没有被修改。"
}
catch {
    Say ""
    Say ("出错：" + $_.Exception.Message) 'Red'
    Say "原文件没有被修改。中间文件保留在 _work 文件夹，可以删除。" 'Red'
    exit 1
}
