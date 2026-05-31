package com.jpx.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;

/**
 * 上場廃止銘柄情報を管理するエンティティ
 */
@Entity
@Table(name = "delisting_news")
@Getter
@Setter 
@NoArgsConstructor
public class DelistingNews {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id; // 識別子（ID）

    @Column(name = "stock_code") 
    private String stockCode; // 銘柄コード

    @Column(name = "stock_name") 
    private String stockName; // 銘柄名

    @Column(name = "market_type") 
    private String marketType; // 市場区分（プライム、スタンダード、グロースなど）

    @Column(name = "delisting_date") 
    private String delistingDate; // 上場廃止日

    @Column(name = "cleanup_start_date") 
    private String cleanupStartDate; // 整理銘柄売買開始日

    @Column(name = "cleanup_end_date") 
    private String cleanupEndDate; // 整理銘柄売買終了日
    
    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt; // レコード作成日時
}