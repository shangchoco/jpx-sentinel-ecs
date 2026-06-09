# 🛡️ JPX Sentinel ECS
### JPX 上場廃止銘柄 自動監視システム

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-ECS_Fargate-FF9900?style=flat-square&logo=amazonaws&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Slack](https://img.shields.io/badge/Notify-Slack_Webhook-4A154B?style=flat-square&logo=slack&logoColor=white)
![Version](https://img.shields.io/badge/version-v1.0.0-success?style=flat-square)

---

> 東京証券取引所（JPX）公式サイトの「上場廃止等の公表」ページを定期自動監視し、  
> **新規公示を即時 Slack 通知 + MySQL 蓄積**する AWS ECS バッチシステムです。

---

## 関連ドキュメント (Reference)
本プロジェクトのシステム詳細仕様、および詳細な設計根拠は以下のドキュメントを参照してください。

- [JPX上場廃止銘柄監視システム_詳細設計書.xlsx](docs/JPX上場廃止銘柄監視システム設計書.xlsx)

## 目次 / Table of Contents

- [背景・目的](#背景目的)
- [システム構成](#システム構成)
- [実行結果](#実行結果)
- [処理シーケンス](#処理シーケンス)
- [ディレクトリ構成](#ディレクトリ構成)
- [技術スタック](#技術スタック)
- [今後の課題・展望](#今後の課題展望)

---

## 背景・目的

JPX 上場廃止情報の**手動確認作業を完全自動化**するために開発したシステムです。

| 課題 | 解決策 |
|------|--------|
| 手動確認による工数・見落としリスク | EventBridge による定期自動実行 |
| 重複通知・重複登録の発生 | MySQL UNIQUE 制約 + `INSERT IGNORE` |
| 公示データの一元管理が困難 | RDS への永続化 + Spring Boot Excel 出力 |

---

## システム構成

* **EventBridge:** スケジューリングによるタスク自動起動
* **ECS Fargate:** サーバーレスなコンテナ実行環境
* **Terraform:** インフラのコード化 (IaC) により再現性を確保

<img width="1036" height="596" alt="image" src="https://github.com/user-attachments/assets/c1d8883b-f415-42d7-8dc9-88fa3093d2a0" />



## システム構成のポイント

- EventBridge Scheduler により ECS タスクを定期実行
- Selenium を利用して JPX 公開情報を取得・解析
- MySQL の UNIQUE 制約による重複データ登録防止
- 新規データ検知時のみ Slack 通知を送信
- Spring Boot API から Excel レポートを出力
- Docker コンテナ化し ECS Fargate 上で運用

## 実行結果

<img width="1084" height="596" alt="image" src="https://github.com/user-attachments/assets/1ba4df14-e964-4ae4-9be7-6512c1ea8b17" />
<img width="546" height="291" alt="image" src="https://github.com/user-attachments/assets/e5500a3d-54ba-4e25-b13c-c424c3c1a3d7" />

① Slack通知結果
- JPXから上場廃止関連の公示を検知
- Slackへ自動通知
- 担当者が即時確認可能


<br>

<img width="832" height="167" alt="image" src="https://github.com/user-attachments/assets/c5b5e283-09d3-4d46-8baa-dd57b7f58b58" />
<img width="1161" height="368" alt="image" src="https://github.com/user-attachments/assets/b7c46df2-5ba4-4aa1-ad43-284edaeca437" />

② Excel出力結果

収集した上場廃止関連データをSpring Boot API経由でExcel形式に出力できます。

主な出力項目：
- 銘柄コード
- 銘柄名
- 市場区分
- 上場廃止日
- 整理銘柄期間
  
<br>
  
<img width="1063" height="57" alt="image" src="https://github.com/user-attachments/assets/d893c28b-cbd9-4848-b335-d7340bf21f1f" />
<img width="827" height="526" alt="image" src="https://github.com/user-attachments/assets/b87ec54c-ae15-475a-bca4-f65ff73c3c51" />

③ ECS稼働状況

ECS Fargate上で動作確認を実施しました。<br>
個人開発環境のため通常時は停止し、<br>
検証時のみ起動する運用としています。<br>

## 処理シーケンス



<img width="842" height="835" alt="image" src="https://github.com/user-attachments/assets/6b25b7c5-03b3-4f39-a4c4-99bb26527acc" />




## ディレクトリ構成

```text
jpx-sentinel-ecs/
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
├── backend/                 # Spring Boot API
├── docs/                    # 設計書・アーキテクチャ資料
├── terraform/               # AWS IaC 定義
├── Dockerfile               # Python Collector コンテナ
├── docker-compose.yml       # ローカル開発環境
├── main.py                  # Flask アプリケーション
├── scraper.py               # JPX 情報収集ロジック
├── database.py              # DB 接続・保存処理
├── init_db.py               # DB 初期化
├── slack_alarm.py           # Slack 通知処理
├── README.md                # プロジェクト概要
└── requirements.txt         # Python ライブラリ
```

## 技術スタック



| カテゴリ | 技術 |
|----------|------|
| Cloud | AWS (VPC, ECS Fargate, RDS, EventBridge, CloudWatch, ECR) |
| IaC | Terraform |
| Container | Docker, Docker Compose |
| Backend | Java, Spring Boot |
| Data Collection | Python, Selenium, Flask |
| Database | MySQL 8.0 (Amazon RDS) |
| Notification | Slack Incoming Webhook |
| CI/CD | GitHub Actions |




## 今後の課題・展望

現在の ECS 環境から、Kubernetes (Amazon EKS) 基盤へ移行することで、より高度な運用管理と可観測性を実現します。

### 1. Amazon EKS によるスケーラブルな運用
* **自律的なリソース制御:** HPA (Horizontal Pod Autoscaler) を活用し、監視対象の増減や公示データの発生頻度に応じて、ポッド数を動的に最適化します。
* **疎結合アーキテクチャ:** 各機能（クローリング、集計、通知）を独立したマイクロサービスとして分離し、障害の局所化と保守性の向上を図ります。

* ### 2. Prometheus + Grafana による高度な可観測性
システムの状態を可視化し、異常検知を迅速化するため、以下の監視基盤を構築します。

* **Prometheus によるメトリクス収集:**
    * クローリングの成功/失敗率、HTTP レスポンスタイム、DB 接続プール状況などのメトリクスを時系列で収集します。
* **Grafana によるダッシュボード化:**
    * 収集したメトリクスを Grafana で視覚化し、現在の監視状況やシステム負荷をリアルタイムでモニタリングします。
    * **異常検知アラート:** 閾値を超えた負荷や連続的なエラー検知時に、Slack へ即時通知を行うフローを構築し、トラブルシューティングの初動を大幅に短縮します。

### 3. GitOps による自動化
* **ArgoCD 連携:** Git リポジトリ（マニフェスト）の状態をクラスターへ自動同期し、手動運用の排除とリリースプロセスの標準化を実現します。


---

*Developed by [shangchoco] - 2026*
