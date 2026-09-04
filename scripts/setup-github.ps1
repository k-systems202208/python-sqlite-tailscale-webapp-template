[CmdletBinding()]
param(
    [string]$Repository = "",
    [string]$RulesetName = "Protect main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Stop-WithMessage {
    param([string]$Message)
    Write-Host ""
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

function Invoke-GhText {
    param([string[]]$Arguments)

    $output = & gh @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw ($output -join [Environment]::NewLine)
    }
    return ($output -join [Environment]::NewLine).Trim()
}

Write-Host "=== GitHub repository setup ===" -ForegroundColor Cyan

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Stop-WithMessage @"
GitHub CLI (gh) が見つかりません。
GitHub CLIをインストール後、次を実行して認証してください。

  gh auth login

Windowsでは winget を利用できる場合、次でも導入できます。

  winget install --id GitHub.cli
"@
}

& gh auth status --hostname github.com *> $null
if ($LASTEXITCODE -ne 0) {
    Stop-WithMessage @"
GitHub CLIがgithub.comへログインしていません。
次を実行して認証してから、もう一度このスクリプトを実行してください。

  gh auth login
"@
}

if ([string]::IsNullOrWhiteSpace($Repository)) {
    try {
        $Repository = Invoke-GhText @("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    }
    catch {
        Stop-WithMessage @"
現在のフォルダーからGitHubリポジトリを判定できませんでした。
Cloneしたリポジトリのルートで実行するか、次のように対象を指定してください。

  .\scripts\setup-github.ps1 -Repository owner/repository
"@
    }
}

if ($Repository -notmatch '^[^/]+/[^/]+$') {
    Stop-WithMessage "Repository は owner/repository 形式で指定してください。現在値: $Repository"
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$rulesetPath = Join-Path $repoRoot "github\protect-main.ruleset.json"

if (-not (Test-Path -LiteralPath $rulesetPath)) {
    Stop-WithMessage "Ruleset定義が見つかりません: $rulesetPath"
}

Write-Host "Target repository : $Repository"
Write-Host "Ruleset          : $RulesetName"
Write-Host "Ruleset file     : $rulesetPath"
Write-Host ""

try {
    $isAdmin = Invoke-GhText @("api", "repos/$Repository", "--jq", ".permissions.admin")
}
catch {
    Stop-WithMessage "リポジトリ情報を取得できませんでした。アクセス権を確認してください。`n$($_.Exception.Message)"
}

if ($isAdmin -ne "true") {
    Stop-WithMessage @"
この設定には対象リポジトリの管理権限が必要です。
GitHub Rulesetの作成・更新には Administration: write 相当の権限が必要です。
"@
}

Write-Host "[1/3] Repository merge settings" -ForegroundColor Yellow
try {
    Invoke-GhText @(
        "api",
        "--method", "PATCH",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository",
        "-F", "allow_squash_merge=true",
        "-F", "allow_merge_commit=false",
        "-F", "allow_rebase_merge=false",
        "-F", "allow_auto_merge=false",
        "-F", "delete_branch_on_merge=true",
        "-F", "allow_update_branch=true"
    ) | Out-Null
}
catch {
    Stop-WithMessage "リポジトリのMerge設定に失敗しました。`n$($_.Exception.Message)"
}

Write-Host "  Squash Merge only / Auto delete head branches: OK" -ForegroundColor Green

Write-Host "[2/3] Protect main Ruleset" -ForegroundColor Yellow
try {
    $rulesetsJson = Invoke-GhText @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository/rulesets"
    )
    $rulesets = @($rulesetsJson | ConvertFrom-Json)
    $existing = $rulesets | Where-Object { $_.name -eq $RulesetName } | Select-Object -First 1

    if ($null -ne $existing) {
        Write-Host "  Existing Ruleset found (ID: $($existing.id)). Updating..."
        Invoke-GhText @(
            "api",
            "--method", "PUT",
            "-H", "X-GitHub-Api-Version: 2026-03-10",
            "--input", $rulesetPath,
            "repos/$Repository/rulesets/$($existing.id)"
        ) | Out-Null
        Write-Host "  Ruleset updated: OK" -ForegroundColor Green
    }
    else {
        Write-Host "  Ruleset not found. Creating..."
        Invoke-GhText @(
            "api",
            "--method", "POST",
            "-H", "X-GitHub-Api-Version: 2026-03-10",
            "--input", $rulesetPath,
            "repos/$Repository/rulesets"
        ) | Out-Null
        Write-Host "  Ruleset created: OK" -ForegroundColor Green
    }
}
catch {
    Stop-WithMessage @"
Rulesetの作成・更新に失敗しました。
GitHubプランやリポジトリ権限によってRulesetsを利用できない場合があります。

$($_.Exception.Message)
"@
}

Write-Host "[3/3] Verification" -ForegroundColor Yellow
try {
    $repoSettings = Invoke-GhText @(
        "api",
        "repos/$Repository",
        "--jq",
        '{allow_squash_merge,allow_merge_commit,allow_rebase_merge,delete_branch_on_merge,allow_update_branch}'
    )

    $verifiedRuleset = Invoke-GhText @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository/rulesets",
        "--jq", ".[] | select(.name == `"$RulesetName`") | {id,name,enforcement}"
    )
}
catch {
    Stop-WithMessage "設定後の確認に失敗しました。`n$($_.Exception.Message)"
}

Write-Host ""
Write-Host "Repository settings:" -ForegroundColor Cyan
Write-Host $repoSettings
Write-Host ""
Write-Host "Ruleset:" -ForegroundColor Cyan
Write-Host $verifiedRuleset
Write-Host ""
Write-Host "GitHub初期設定が完了しました。" -ForegroundColor Green
Write-Host "以降は 日本語Issue -> Issue番号入りBranch -> PR -> CI -> Squash Merge の運用を使用してください。"
