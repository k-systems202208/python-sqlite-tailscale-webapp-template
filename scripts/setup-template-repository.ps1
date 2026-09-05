[CmdletBinding()]
param(
    [string]$Repository = "",
    [string]$RulesetName = "Protect main",
    [string[]]$Topics = @(
        "python",
        "flask",
        "sqlite",
        "tailscale",
        "webapp-template",
        "starter-template"
    )
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

Write-Host "=== Public template repository setup ===" -ForegroundColor Cyan

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Stop-WithMessage "GitHub CLI (gh) が見つかりません。gh auth login 済みの環境で実行してください。"
}

& gh auth status --hostname github.com *> $null
if ($LASTEXITCODE -ne 0) {
    Stop-WithMessage "GitHub CLIがgithub.comへログインしていません。gh auth login を実行してください。"
}

if ([string]::IsNullOrWhiteSpace($Repository)) {
    try {
        $Repository = Invoke-GhText -Arguments @("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    }
    catch {
        Stop-WithMessage "現在のフォルダーからGitHubリポジトリを判定できませんでした。-Repository owner/repository を指定してください。"
    }
}

if ($Repository -notmatch '^[^/]+/[^/]+$') {
    Stop-WithMessage "Repository は owner/repository 形式で指定してください。現在値: $Repository"
}

try {
    $isAdmin = Invoke-GhText -Arguments @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository",
        "--jq", ".permissions.admin"
    )
    $isTemplate = Invoke-GhText -Arguments @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository",
        "--jq", ".is_template"
    )
}
catch {
    Stop-WithMessage "Repository情報を取得できませんでした。`n$($_.Exception.Message)"
}

if ($isAdmin -ne "true") {
    Stop-WithMessage "この設定には対象Repositoryの管理権限が必要です。"
}

if ($isTemplate -ne "true") {
    Stop-WithMessage "対象RepositoryはTemplate repositoryではありません。派生アプリのWiki / Topicsは自動変更しません。"
}

$commonSetupPath = Join-Path $PSScriptRoot "setup-github.ps1"
if (-not (Test-Path -LiteralPath $commonSetupPath)) {
    Stop-WithMessage "共通GitHub設定スクリプトが見つかりません: $commonSetupPath"
}

Write-Host "[1/4] Common GitHub settings and Strict Ruleset" -ForegroundColor Yellow
& $commonSetupPath -Repository $Repository -RulesetName $RulesetName
if ($LASTEXITCODE -ne 0) {
    Stop-WithMessage "setup-github.ps1 が失敗しました。"
}

Write-Host "[2/4] Disable Wiki on template repository" -ForegroundColor Yellow
try {
    Invoke-GhText -Arguments @(
        "api",
        "--method", "PATCH",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository",
        "-F", "has_wiki=false"
    ) | Out-Null
}
catch {
    Stop-WithMessage "Wiki設定の更新に失敗しました。`n$($_.Exception.Message)"
}
Write-Host "  Wiki disabled: OK" -ForegroundColor Green

Write-Host "[3/4] Apply repository Topics" -ForegroundColor Yellow
try {
    $topicArguments = @(
        "api",
        "--method", "PUT",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "-H", "Accept: application/vnd.github+json",
        "repos/$Repository/topics"
    )

    foreach ($topic in $Topics) {
        if (-not [string]::IsNullOrWhiteSpace($topic)) {
            $topicArguments += @("-f", "names[]=$topic")
        }
    }

    Invoke-GhText -Arguments $topicArguments | Out-Null
}
catch {
    Stop-WithMessage "Topics設定の更新に失敗しました。`n$($_.Exception.Message)"
}
Write-Host "  Topics applied: $($Topics -join ', ')" -ForegroundColor Green

Write-Host "[4/4] Verify live repository settings" -ForegroundColor Yellow
try {
    $hasWiki = Invoke-GhText -Arguments @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository",
        "--jq", ".has_wiki"
    )

    if ($hasWiki -ne "false") {
        throw "Wikiが無効化されていません。"
    }
    Write-Host "  Wiki verification: OK" -ForegroundColor Green

    $actualTopicsText = Invoke-GhText -Arguments @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "-H", "Accept: application/vnd.github+json",
        "repos/$Repository/topics",
        "--jq", '.names | sort | @tsv'
    )
    $expectedTopics = @($Topics | Where-Object { $_ -and $_.Trim().Length -gt 0 } | Sort-Object)
    $expectedTopicsText = $expectedTopics -join "`t"

    if ($actualTopicsText -ne $expectedTopicsText) {
        throw "Topicsが期待値と一致しません。Actual: $actualTopicsText"
    }
    Write-Host "  Topics verification: OK" -ForegroundColor Green

    $rulesetRows = Invoke-GhText -Arguments @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository/rulesets",
        "--jq", '.[] | [.id,.name] | @tsv'
    )
    $rulesetId = ""
    foreach ($row in @($rulesetRows -split '\r?\n')) {
        if ([string]::IsNullOrWhiteSpace($row)) {
            continue
        }
        $columns = @($row -split "`t", 2)
        if ($columns.Count -eq 2 -and $columns[1] -eq $RulesetName) {
            $rulesetId = [string]$columns[0]
            break
        }
    }

    if ([string]::IsNullOrWhiteSpace($rulesetId)) {
        throw "Ruleset '$RulesetName' が見つかりません。"
    }

    $strictStatus = Invoke-GhText -Arguments @(
        "api",
        "-H", "X-GitHub-Api-Version: 2026-03-10",
        "repos/$Repository/rulesets/$rulesetId",
        "--jq", '.rules[].parameters.strict_required_status_checks_policy // empty'
    )

    if ([string]::IsNullOrWhiteSpace($strictStatus)) {
        throw "Required Status Checks ruleが見つかりません。"
    }

    if ($strictStatus -ne "true") {
        throw "Required Status ChecksがStrictではありません。"
    }
    Write-Host "  Strict verification: OK" -ForegroundColor Green
}
catch {
    Stop-WithMessage "実Repository設定の確認に失敗しました。`n$($_.Exception.Message)"
}

Write-Host ""
Write-Host "Template repository settings: OK" -ForegroundColor Green
Write-Host "  Strict Required Status Checks : ON"
Write-Host "  Wiki                          : OFF"
Write-Host "  Topics                        : $($expectedTopics -join ', ')"
